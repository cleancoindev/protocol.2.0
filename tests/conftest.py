import os

from eth_tester import (
    EthereumTester,
    PyEVMBackend
)
from eth_tester.exceptions import (
    TransactionFailed,
)
from eth_utils.toolz import (
    compose,
)
import pytest
from web3 import Web3
from web3.contract import (
    Contract,
    mk_collision_prop,
)
from web3.logs import DISCARD
from web3.providers.eth_tester import (
    EthereumTesterProvider,
)

from vyper import (
    compiler,
)


ZERO_ADDRESS = Web3.toChecksumAddress('0x0000000000000000000000000000000000000000')
EMPTY_BYTES32 = '0x0000000000000000000000000000000000000000000000000000000000000000'

# EXPIRIES
# Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
Z19 = 1577404799


class VyperMethod:
    ALLOWED_MODIFIERS = {'call', 'estimateGas', 'transact', 'buildTransaction'}

    def __init__(self, function, normalizers=None):
        self._function = function
        self._function._return_data_normalizers = normalizers

    def __call__(self, *args, **kwargs):
        return self.__prepared_function(*args, **kwargs)

    def __prepared_function(self, *args, **kwargs):
        if not kwargs:
            modifier, modifier_dict = 'call', {}
            fn_abi = [
                x
                for x
                in self._function.contract_abi
                if x.get('name') == self._function.function_identifier
            ].pop()
            # To make tests faster just supply some high gas value.
            modifier_dict.update({'gas': fn_abi.get('gas', 0) + 50000})
        elif len(kwargs) == 1:
            modifier, modifier_dict = kwargs.popitem()
            if modifier not in self.ALLOWED_MODIFIERS:
                raise TypeError(
                    f"The only allowed keyword arguments are: {self.ALLOWED_MODIFIERS}")
        else:
            raise TypeError(f"Use up to one keyword argument, one of: {self.ALLOWED_MODIFIERS}")
        return getattr(self._function(*args), modifier)(modifier_dict)


class VyperContract:
    """
    An alternative Contract Factory which invokes all methods as `call()`,
    unless you add a keyword argument. The keyword argument assigns the prep method.
    This call
    > contract.withdraw(amount, transact={'from': eth.accounts[1], 'gas': 100000, ...})
    is equivalent to this call in the classic contract:
    > contract.functions.withdraw(amount).transact({'from': eth.accounts[1], 'gas': 100000, ...})
    """

    def __init__(self, classic_contract, method_class=VyperMethod):
        classic_contract._return_data_normalizers += CONCISE_NORMALIZERS
        self._classic_contract = classic_contract
        self.address = self._classic_contract.address
        protected_fn_names = [fn for fn in dir(self) if not fn.endswith('__')]
        for fn_name in self._classic_contract.functions:
            # Override namespace collisions
            if fn_name in protected_fn_names:
                _concise_method = mk_collision_prop(fn_name)
            else:
                _classic_method = getattr(
                    self._classic_contract.functions,
                    fn_name)
                _concise_method = method_class(
                    _classic_method,
                    self._classic_contract._return_data_normalizers
                )
            setattr(self, fn_name, _concise_method)

    @classmethod
    def factory(cls, *args, **kwargs):
        return compose(cls, Contract.factory(*args, **kwargs))


def _none_addr(datatype, data):
    if datatype == 'address' and int(data, base=16) == 0:
        return (datatype, None)
    else:
        return (datatype, data)


CONCISE_NORMALIZERS = (_none_addr,)


@pytest.fixture
def tester():
    genesis_overrides = {"gas_limit": 3750000}
    custom_genesis_params = PyEVMBackend._generate_genesis_params(
        overrides=genesis_overrides
    )
    pyevm_backend = PyEVMBackend(genesis_parameters=custom_genesis_params)
    t = EthereumTester(backend=pyevm_backend)
    # t = EthereumTester()
    return t


def zero_gas_price_strategy(web3, transaction_params=None):
    return 0  # zero gas price makes testing simpler.


@pytest.fixture
def w3(tester):
    w3 = Web3(EthereumTesterProvider(tester))
    w3.eth.setGasPriceStrategy(zero_gas_price_strategy)
    return w3


def _get_contract(w3, source_code, *args, **kwargs):
    out = compiler.compile_code(
        source_code,
        ['abi', 'bytecode'],
        interface_codes=kwargs.pop('interface_codes', None),
    )
    abi = out['abi']
    bytecode = out['bytecode']
    value = kwargs.pop('value_in_eth', 0) * 10 ** 18  # Handle deploying with an eth value.
    c = w3.eth.contract(abi=abi, bytecode=bytecode)
    deploy_transaction = c.constructor(*args)
    tx_info = {
        'from': w3.eth.accounts[0],
        'value': value,
        'gasPrice': 0,
    }
    tx_info.update(kwargs)
    tx_hash = deploy_transaction.transact(tx_info)
    address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
    contract = w3.eth.contract(
        address,
        abi=abi,
        bytecode=bytecode,
        ContractFactoryClass=VyperContract,
    )
    return contract


def _get_contract_from_address(_w3, _address, _source_code_path, **kwargs):
    with open(_source_code_path) as f:
        source_code = f.read()

    out = compiler.compile_code(
        source_code,
        ['abi', 'bytecode'],
        interface_codes=kwargs.pop('interface_codes', None),
    )
    abi = out['abi']
    bytecode = out['bytecode']
    contract = _w3.eth.contract(
        _address,
        abi=abi,
        bytecode=bytecode,
        ContractFactoryClass=VyperContract,
    )
    return contract


@pytest.fixture
def get_contract(w3):
    def get_contract(source_code, *args, **kwargs):
        return _get_contract(w3, source_code, *args, **kwargs)

    return get_contract


@pytest.fixture
def get_logs(w3):
    def get_logs(tx_hash, c, event_name):
        tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
        logs = c._classic_contract.events[event_name]().processReceipt(tx_receipt, errors=DISCARD)
        return logs

    return get_logs


@pytest.fixture
def assert_tx_failed(tester):
    def assert_tx_failed(function_to_test, exception=TransactionFailed, exc_text=None):
        snapshot_id = tester.take_snapshot()
        with pytest.raises(exception) as excinfo:
            function_to_test()
        tester.revert_to_snapshot(snapshot_id)
        if exc_text:
            assert exc_text in str(excinfo.value)

    return assert_tx_failed


# Library contracts and DAOS

@pytest.fixture
def LST_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Lendroid Support Token', 'LST',
            18, 12000000000)
    return contract


@pytest.fixture
def Lend_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Lend Token', 'DAI',
            18, 1000000)
    return contract


@pytest.fixture
def Borrow_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Borrow Token', 'WETH',
            18, 1000000)
    return contract


@pytest.fixture
def Malicious_token(w3, get_contract):
    with open('contracts/templates/ERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, 'Test Malicious Token', 'XXX',
            18, 1000000)
    return contract


@pytest.fixture
def ERC20_library(w3, get_contract):
    with open('contracts/templates/ERC20Template2.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code)
    return contract


@pytest.fixture
def ERC1155_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/ERC1155Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def CurrencyPool_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/ContinuousCurrencyPoolERC20Template1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def CurrencyDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ContinuousCurrencyPoolERC20.vy')) as f:
            interface_codes['ContinuousCurrencyPoolERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/CurrencyDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def ShieldPayoutGraph_library(w3, get_contract):
    with open('contracts/templates/SimpleShieldPayoutGraph.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code)
    return contract


@pytest.fixture
def ShieldPayoutDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ShieldPayoutGraph.vy')) as f:
            interface_codes['ShieldPayoutGraph'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/ShieldPayoutDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def InterestPool_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/InterestPoolTemplate1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def InterestPoolDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPool.vy')) as f:
            interface_codes['InterestPool'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/InterestPoolDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def UnderwriterPool_library(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
            interface_codes['ERC1155'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/templates/UnderwriterPoolTemplate1.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def UnderwriterPoolDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPool.vy')) as f:
            interface_codes['UnderwriterPool'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/UnderwriterPoolDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract


@pytest.fixture
def LoanDao(w3, get_contract):
    interface_codes = {}
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
            interface_codes['ERC20'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
            interface_codes['ERC1155TokenReceiver'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/CurrencyDao.vy')) as f:
            interface_codes['CurrencyDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
            interface_codes['InterestPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
        os.pardir, 'contracts/interfaces/UnderwriterPoolDao.vy')) as f:
            interface_codes['UnderwriterPoolDao'] = {
                'type': 'vyper',
                'code': f.read()
            }
    with open('contracts/daos/LoanDao.v.py') as f:
        contract_code = f.read()
        # Pass constructor variables directly to the contract
        contract = get_contract(contract_code, interface_codes=interface_codes)
    return contract
