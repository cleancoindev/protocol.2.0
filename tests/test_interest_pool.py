import os

import pytest

from web3 import Web3

from conftest import (
    PROTOCOL_CONSTANTS,
    POOL_NAME_REGISTRATION_MIN_STAKE_LST, POOL_NAME_LIONFURY,
    ZERO_ADDRESS, EMPTY_BYTES32,
    INTEREST_POOL_DAO_MIN_MFT_FEE, INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT,
    STRIKE_125, H20,
    MAX_LIABILITY_CURENCY_MARKET
)


def test_contribute(w3,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    Poolshare_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(InterestPool.address) == 0
    assert Poolshare_token.balanceOf(_pool_owner) == 0
    # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
    assert InterestPool.exchange_rate() == Web3.toWei(50, 'ether')
    assert InterestPool.estimated_pool_share_tokens(Web3.toWei(500, 'ether')) == Web3.toWei(25000, 'ether')
    assert InterestPool.l_token_balance() == 0
    assert InterestPool.total_pool_share_token_supply() == 0
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify L_Lend_token and Poolshare_token balances
    # assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(500, 'ether')
    # assert InterestPool.l_token_balance() == Web3.toWei(500, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(25000, 'ether')
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(25000, 'ether')
    # _pool_owner contributes 200 L_lend_token to his own pool _pool_name
    assert InterestPool.exchange_rate() == Web3.toWei(50, 'ether')
    assert InterestPool.estimated_pool_share_tokens(Web3.toWei(200, 'ether')) == Web3.toWei(10000, 'ether')
    tx_hash = InterestPool.contribute(Web3.toWei(200, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(700, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(700, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(35000, 'ether')
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(35000, 'ether')


def test_withdraw_contribution_sans_i_token_purchase(w3,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_Lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_Lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    # get Poolshare_token
    Poolshare_token = get_ERC20_Pool_Token_contract(address=InterestPool.pool_share_token())
    # verify L_Lend_token and Poolshare_token balances
    assert L_lend_token.balanceOf(InterestPool.address) == 0
    assert Poolshare_token.balanceOf(_pool_owner) == 0
    # _pool_owner contributes 500 L_lend_token to his own InterestPool
    InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 250000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(25000, 'ether')
    assert L_lend_token.balanceOf(_pool_owner) == Web3.toWei(300, 'ether')
    assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(500, 'ether')
    # _pool_owner withdraws 12500 Poolshare_token from his own InterestPool
    assert InterestPool.exchange_rate() == Web3.toWei(50, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(500, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(25000, 'ether')
    assert InterestPool.estimated_pool_share_tokens(Web3.toWei(250, 'ether')) == Web3.toWei(12500, 'ether')
    InterestPool.withdraw_contribution(Web3.toWei(12500, 'ether'), transact={'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(12500, 'ether')
    assert L_lend_token.balanceOf(_pool_owner) == Web3.toWei(550, 'ether')
    assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(250, 'ether')
    # _pool_owner withdraws 6250 Poolshare_token from his own InterestPool
    assert InterestPool.exchange_rate() == Web3.toWei(50, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(250, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(12500, 'ether')
    assert InterestPool.estimated_pool_share_tokens(Web3.toWei(125, 'ether')) == Web3.toWei(6250, 'ether')
    InterestPool.withdraw_contribution(Web3.toWei(6250, 'ether'), transact={'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(6250, 'ether')
    assert L_lend_token.balanceOf(_pool_owner) == Web3.toWei(675, 'ether')
    assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(125, 'ether')
    # _pool_owner withdraws all remaining 6250 Poolshare_token from his own InterestPool
    assert InterestPool.exchange_rate() == Web3.toWei(50, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(125, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(6250, 'ether')
    assert InterestPool.estimated_pool_share_tokens(Web3.toWei(125, 'ether')) == Web3.toWei(6250, 'ether')
    InterestPool.withdraw_contribution(Web3.toWei(6250, 'ether'), transact={'from': _pool_owner, 'gas': 200000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner) == 0
    assert L_lend_token.balanceOf(_pool_owner) == Web3.toWei(800, 'ether')
    assert L_lend_token.balanceOf(InterestPool.address) == 0
    assert InterestPool.l_token_balance() == 0
    assert InterestPool.total_pool_share_token_supply() == 0
    # _pool_owner again contributes 200 L_lend_token to his own InterestPool
    InterestPool.contribute(Web3.toWei(200, 'ether'), transact={'from': _pool_owner, 'gas': 250000})
    # verify L_Lend_token and Poolshare_token balances
    assert Poolshare_token.balanceOf(_pool_owner) == Web3.toWei(10000, 'ether')
    assert L_lend_token.balanceOf(_pool_owner) == Web3.toWei(600, 'ether')
    assert L_lend_token.balanceOf(InterestPool.address) == Web3.toWei(200, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(200, 'ether')
    assert InterestPool.total_pool_share_token_supply() == Web3.toWei(10000, 'ether')


def test_increment_i_tokens(w3,
        Whale, Deployer, Governor,
        LST_token, Lend_token,
        get_ERC20_contract, get_ERC20_Pool_Token_contract, get_MFT_contract,
        get_PoolNameRegistry_contract, get_InterestPool_contract,
        get_CurrencyDao_contract, get_InterestPoolDao_contract,
        ProtocolDao):
    # get CurrencyDao
    CurrencyDao = get_CurrencyDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # get InterestPoolDao
    InterestPoolDao = get_InterestPoolDao_contract(address=ProtocolDao.daos(PROTOCOL_CONSTANTS['DAO_INTEREST_POOL']))
    # get PoolNameRegistry
    PoolNameRegistry = get_PoolNameRegistry_contract(address=ProtocolDao.registries(PROTOCOL_CONSTANTS['REGISTRY_POOL_NAME']))
    # assign one of the accounts as _pool_owner
    _pool_owner = w3.eth.accounts[6]
    # initialize PoolNameRegistry
    ProtocolDao.initialize_pool_name_registry(Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Deployer})
    # initialize CurrencyDao
    ProtocolDao.initialize_currency_dao(transact={'from': Deployer})
    # initialize InterestPoolDao
    ProtocolDao.initialize_interest_pool_dao(transact={'from': Deployer})
    # set support for Lend_token
    ProtocolDao.set_token_support(Lend_token.address, True, transact={'from': Governor, 'gas': 2000000})
    # get L_lend_token
    L_lend_token = get_ERC20_contract(address=CurrencyDao.token_addresses__l(Lend_token.address))
    # get F_lend_token
    F_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__f(Lend_token.address))
    # get I_lend_token
    I_lend_token = get_MFT_contract(address=CurrencyDao.token_addresses__i(Lend_token.address))
    # _pool_owner buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_pool_owner, Web3.toWei(1000, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend 800 Lend_token
    Lend_token.approve(CurrencyDao.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner})
    # _pool_owner wraps 800 Lend_token to L_lend_token
    CurrencyDao.wrap(Lend_token.address, Web3.toWei(800, 'ether'), transact={'from': _pool_owner, 'gas': 145000})
    # _pool_owner buys POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token from a 3rd party exchange
    LST_token.transfer(_pool_owner, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': Whale})
    # _pool_owner authorizes CurrencyDao to spend POOL_NAME_REGISTRATION_MIN_STAKE_LST LST_token
    LST_token.approve(CurrencyDao.address, Web3.toWei(POOL_NAME_REGISTRATION_MIN_STAKE_LST, 'ether'), transact={'from': _pool_owner})
    # _pool_owner registers _pool_name POOL_NAME_LIONFURY at the InterestPoolDao
    _pool_name = POOL_NAME_LIONFURY
    InterestPoolDao.register_pool(
        False, Lend_token.address, _pool_name, Web3.toWei(50, 'ether'), 1, 90, transact={'from': _pool_owner, 'gas': 1200000})
    # get InterestPool
    InterestPool = get_InterestPool_contract(address=InterestPoolDao.pools__address_(_pool_name))
    tx_hash = ProtocolDao.set_minimum_mft_fee(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'],
        Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'),
        transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set MFT multiplier
    tx_hash = ProtocolDao.set_fee_multiplier_per_mft_count(
        PROTOCOL_CONSTANTS['DAO_INTEREST_POOL'], Web3.toWei(0, 'ether'),
        Web3.toWei(INTEREST_POOL_DAO_FEE_MULTIPLIER_PER_MFT_COUNT, 'ether'),
        transact={'from': Governor, 'gas': 75000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for expiry H20
    tx_hash = ProtocolDao.set_expiry_support(H20, "H20", True, transact={'from': Governor})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner buys INTEREST_POOL_DAO_MIN_MFT_FEE LST_token from a 3rd party exchange
    tx_hash = LST_token.transfer(_pool_owner, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': Whale})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # _pool_owner authorizes CurrencyDao to spend INTEREST_POOL_DAO_MIN_MFT_FEE LST_token
    tx_hash = LST_token.approve(CurrencyDao.address, Web3.toWei(INTEREST_POOL_DAO_MIN_MFT_FEE, 'ether'), transact={'from': _pool_owner})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    # set support for MFT H20
    tx_hash = InterestPool.support_mft(H20, Web3.toWei(0.01, 'ether'), transact={'from': _pool_owner, 'gas': 2500000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    _market_hash = InterestPool.market_hash(H20)
    _f_id = InterestPool.markets__f_id(_market_hash)
    _i_id = InterestPool.markets__i_id(_market_hash)
    # _pool_owner contributes 500 L_lend_token to his own pool _pool_name
    tx_hash = InterestPool.contribute(Web3.toWei(500, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPool.i_token_balance(H20) == 0
    assert I_lend_token.balanceOf(InterestPool.address, _i_id) == 0
    assert InterestPool.f_token_balance(H20) == 0
    assert F_lend_token.balanceOf(InterestPool.address, _f_id) == 0
    assert InterestPool.total_f_token_balance() == 0
    assert F_lend_token.totalBalanceOf(InterestPool.address) == 0
    assert InterestPool.l_token_balance() == Web3.toWei(500, 'ether')
    assert InterestPool.total_active_contributions() == Web3.toWei(500, 'ether')
    # _pool_owner increments ITokens by converting 300 L_lend_token to 300 ITokens and 300 FTokens
    tx_hash = InterestPool.increment_i_tokens(H20, Web3.toWei(300, 'ether'), transact={'from': _pool_owner, 'gas': 300000})
    tx_receipt = w3.eth.waitForTransactionReceipt(tx_hash)
    assert tx_receipt['status'] == 1
    assert InterestPool.i_token_balance(H20) == Web3.toWei(300, 'ether')
    assert I_lend_token.balanceOf(InterestPool.address, _i_id) == Web3.toWei(300, 'ether')
    assert InterestPool.f_token_balance(H20) == Web3.toWei(300, 'ether')
    assert F_lend_token.balanceOf(InterestPool.address, _f_id) == Web3.toWei(300, 'ether')
    assert InterestPool.total_f_token_balance() == Web3.toWei(300, 'ether')
    assert F_lend_token.totalBalanceOf(InterestPool.address) == Web3.toWei(300, 'ether')
    assert InterestPool.l_token_balance() == Web3.toWei(200, 'ether')
    assert InterestPool.total_active_contributions() == Web3.toWei(500, 'ether')


# def test_purchase_i_currency(w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_1_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
#     assert tx_1_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_2_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
#     assert tx_2_receipt['status'] == 1
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
#         'Interest Pool A', 'IPA', 50,
#         transact={'from': pool_owner, 'gas': 800000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # get InterestPool contract
#     logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
#     _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
#     InterestPool = get_contract(
#         'contracts/templates/InterestPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'InterestPoolDao'
#         ],
#         address=InterestPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get InterestPoolCurrency
#     InterestPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=InterestPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     tx_7_hash = InterestPool.register_expiry(Z19,
#         transact={'from': pool_owner, 'gas': 1100000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # get L_token
#     L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     L_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=L_token_address
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = w3.eth.accounts[2]
#     # High_Risk_Insurer buys 1000 lend token from a 3rd party exchange
#     tx_8_hash = Lend_token.transfer(High_Risk_Insurer, 1000 * 10 ** 18, transact={'from': owner})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend 100 lend currency
#     tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
#         transact={'from': High_Risk_Insurer})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # High_Risk_Insurer deposits Lend_token to Currency Pool and gets l_tokens
#     tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
#         transact={'from': High_Risk_Insurer, 'gas': 200000})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
#     # High_Risk_Insurer purchases InterestPoolCurrency for 100 L_tokens
#     # High_Risk_Insurer gets 5000 InterestPoolCurrency tokens
#     # 100 L_tokens are deposited into InterestPool account
#     tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': High_Risk_Insurer})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # verify InterestPool balances of l, i, f tokens
#     assert InterestPool.i_currency_balance(Z19) == 0
#     assert InterestPool.f_currency_balance(Z19) == 0
#     assert InterestPool.total_f_currency_balance() == 0
#     assert InterestPool.l_currency_balance() == 100 * 10 ** 18
#     assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
#     # pool_owner initiates offer of 20 I_tokens from the InterestPool
#     # 20 L_tokens burned from InterestPool account
#     # 20 I_tokens and 20 F_tokens deposited to InterestPool account
#     tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     # verify InterestPool balances of l, i, f tokens
#     assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
#     assert InterestPool.l_currency_balance() == 80 * 10 ** 18
#     assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
#     # High_Risk_Insurer purchases 10 i_tokens from InterestPool
#     tx_13_hash = InterestPool.purchase_i_currency(Z19, 10 * 10 ** 18, 0, transact={'from': High_Risk_Insurer})
#     tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
#     assert tx_13_receipt['status'] == 1
#     # verify InterestPool balances of l, i, f tokens
#     assert InterestPool.i_currency_balance(Z19) == 10 * 10 ** 18
#     assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
#     assert InterestPool.l_currency_balance() == 80 * 10 ** 18
#     assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
#     # get I_token
#     I_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__i_currency_address(Lend_token.address)
#     )
#     # verify High_Risk_Insurer balance of i tokens
#     assert I_token.balanceOf(High_Risk_Insurer, InterestPool.expiries__i_currency_id(Z19)) == 10 * 10 ** 18
#
#
# def test_redeem_f_currency(w3, get_contract, get_logs,
#         LST_token, Lend_token, Malicious_token,
#         ERC20_library, ERC1155_library,
#         CurrencyPool_library, CurrencyDao,
#         InterestPool_library, InterestPoolDao,
#         MarketDao
#     ):
#     owner = w3.eth.accounts[0]
#     # initialize CurrencyDao
#     tx_1_hash = CurrencyDao.initialize(
#         owner, LST_token.address, CurrencyPool_library.address,
#         ERC20_library.address, ERC1155_library.address,
#         MarketDao.address,
#         transact={'from': owner})
#     tx_1_receipt = w3.eth.waitForTransactionReceipt(tx_1_hash)
#     assert tx_1_receipt['status'] == 1
#     # initialize InterestPoolDao
#     tx_2_hash = InterestPoolDao.initialize(
#         owner, LST_token.address, CurrencyDao.address,
#         InterestPool_library.address, ERC20_library.address,
#         transact={'from': owner})
#     tx_2_receipt = w3.eth.waitForTransactionReceipt(tx_2_hash)
#     assert tx_2_receipt['status'] == 1
#     # set_offer_registration_fee_lookup()
#     _minimum_fee = 100
#     _minimum_interval = 10
#     _fee_multiplier = 2000
#     _fee_multiplier_decimals = 1000
#     tx_3_hash = InterestPoolDao.set_offer_registration_fee_lookup(_minimum_fee,
#         _minimum_interval, _fee_multiplier, _fee_multiplier_decimals,
#         transact={'from': owner})
#     tx_3_receipt = w3.eth.waitForTransactionReceipt(tx_3_hash)
#     assert tx_3_receipt['status'] == 1
#     # set_currency_support for Lend_token in CurrencyDao
#     tx_4_hash = CurrencyDao.set_currency_support(Lend_token.address, True,
#         transact={'from': owner, 'gas': 1570000})
#     tx_4_receipt = w3.eth.waitForTransactionReceipt(tx_4_hash)
#     assert tx_4_receipt['status'] == 1
#     # register_pool for Lend_token
#     pool_owner = w3.eth.accounts[1]
#     tx_5_hash = InterestPoolDao.register_pool(Lend_token.address,
#         'Interest Pool A', 'IPA', 50,
#         transact={'from': pool_owner, 'gas': 800000})
#     tx_5_receipt = w3.eth.waitForTransactionReceipt(tx_5_hash)
#     assert tx_5_receipt['status'] == 1
#     # get InterestPool contract
#     logs_5 = get_logs(tx_5_hash, InterestPoolDao, "PoolRegistered")
#     _pool_hash = InterestPoolDao.pool_hash(Lend_token.address, logs_5[0].args._pool_address)
#     interest_pool_interface_codes = {}
#     with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
#         os.pardir, 'contracts/interfaces/ERC20.vy')) as f:
#             interest_pool_interface_codes['ERC20'] = {
#                 'type': 'vyper',
#                 'code': f.read()
#             }
#     with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
#         os.pardir, 'contracts/interfaces/ERC1155.vy')) as f:
#             interest_pool_interface_codes['ERC1155'] = {
#                 'type': 'vyper',
#                 'code': f.read()
#             }
#     with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
#         os.pardir, 'contracts/interfaces/ERC1155TokenReceiver.vy')) as f:
#             interest_pool_interface_codes['ERC1155TokenReceiver'] = {
#                 'type': 'vyper',
#                 'code': f.read()
#             }
#     with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
#         os.pardir, 'contracts/interfaces/InterestPoolDao.vy')) as f:
#             interest_pool_interface_codes['InterestPoolDao'] = {
#                 'type': 'vyper',
#                 'code': f.read()
#             }
#     InterestPool = get_contract(
#         'contracts/templates/InterestPoolTemplate1.v.py',
#         interfaces=[
#             'ERC20', 'ERC1155', 'ERC1155TokenReceiver', 'InterestPoolDao'
#         ],
#         address=InterestPoolDao.pools__pool_address(_pool_hash)
#     )
#     # get InterestPoolCurrency
#     InterestPoolCurrency = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=InterestPool.pool_currency_address()
#     )
#     # pool_owner buys LST from a 3rd party
#     LST_token.transfer(pool_owner, 1000 * 10 ** 18, transact={'from': owner})
#     # pool_owner authorizes CurrencyDao to spend LST required for offer_registration_fee
#     tx_6_hash = LST_token.approve(CurrencyDao.address, InterestPoolDao.offer_registration_fee() * (10 ** 18),
#         transact={'from': pool_owner})
#     tx_6_receipt = w3.eth.waitForTransactionReceipt(tx_6_hash)
#     assert tx_6_receipt['status'] == 1
#     # pool_owner registers an expiry : Last Thursday of December 2019, i.e., December 26th, 2019, i.e., Z19
#     tx_7_hash = InterestPool.register_expiry(Z19,
#         transact={'from': pool_owner, 'gas': 1100000})
#     tx_7_receipt = w3.eth.waitForTransactionReceipt(tx_7_hash)
#     assert tx_7_receipt['status'] == 1
#     # get L_token
#     L_token_address = CurrencyDao.currencies__l_currency_address(Lend_token.address)
#     L_token = get_contract(
#         'contracts/templates/ERC20Template1.v.py',
#         address=L_token_address
#     )
#     # assign one of the accounts as a High_Risk_Insurer
#     High_Risk_Insurer = w3.eth.accounts[2]
#     # High_Risk_Insurer buys 1000 lend token from a 3rd party exchange
#     tx_8_hash = Lend_token.transfer(High_Risk_Insurer, 1000 * 10 ** 18, transact={'from': owner})
#     tx_8_receipt = w3.eth.waitForTransactionReceipt(tx_8_hash)
#     assert tx_8_receipt['status'] == 1
#     # High_Risk_Insurer authorizes CurrencyDao to spend 100 lend currency
#     tx_9_hash = Lend_token.approve(CurrencyDao.address, 100 * (10 ** 18),
#         transact={'from': High_Risk_Insurer})
#     tx_9_receipt = w3.eth.waitForTransactionReceipt(tx_9_hash)
#     assert tx_9_receipt['status'] == 1
#     # High_Risk_Insurer deposits Lend_token to Currency Pool and gets l_tokens
#     tx_10_hash = CurrencyDao.currency_to_l_currency(Lend_token.address, 100 * 10 ** 18,
#         transact={'from': High_Risk_Insurer, 'gas': 200000})
#     tx_10_receipt = w3.eth.waitForTransactionReceipt(tx_10_hash)
#     assert tx_10_receipt['status'] == 1
#     # High_Risk_Insurer purchases InterestPoolCurrency for 100 L_tokens
#     # High_Risk_Insurer gets 5000 InterestPoolCurrency tokens
#     # 100 L_tokens are deposited into InterestPool account
#     tx_11_hash = InterestPool.purchase_pool_currency(100 * 10 ** 18, transact={'from': High_Risk_Insurer})
#     tx_11_receipt = w3.eth.waitForTransactionReceipt(tx_11_hash)
#     assert tx_11_receipt['status'] == 1
#     # pool_owner initiates offer of 20 I_tokens from the InterestPool
#     # 20 L_tokens burned from InterestPool account
#     # 20 I_tokens and 20 F_tokens deposited to InterestPool account
#     tx_12_hash = InterestPool.increment_i_currency_supply(Z19, 20 * 10 ** 18, transact={'from': pool_owner, 'gas': 500000})
#     tx_12_receipt = w3.eth.waitForTransactionReceipt(tx_12_hash)
#     assert tx_12_receipt['status'] == 1
#     assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.f_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.total_f_currency_balance() == 20 * 10 ** 18
#     assert InterestPool.l_currency_balance() == (100 - 20) * 10 ** 18
#     assert InterestPool.total_l_currency_balance() == 100 * 10 ** 18
#     # High_Risk_Insurer redeems f_tokens worth 5000 InterestPoolCurrency tokens from InterestPool
#     assert InterestPool.estimated_pool_tokens(100 * 10 ** 18) == 5000 * 10 ** 18
#     tx_13_hash = InterestPool.redeem_f_currency(Z19, 5000 * 10 ** 18, transact={'from': High_Risk_Insurer, 'gas': 500000})
#     tx_13_receipt = w3.eth.waitForTransactionReceipt(tx_13_hash)
#     assert tx_13_receipt['status'] == 1
#     # get F_token
#     F_token = get_contract(
#         'contracts/templates/ERC1155Template2.v.py',
#         interfaces=['ERC1155TokenReceiver'],
#         address=CurrencyDao.currencies__f_currency_address(Lend_token.address)
#     )
#     # verify High_Risk_Insurer balance of l and f tokens
#     assert F_token.balanceOf(High_Risk_Insurer, InterestPool.expiries__f_currency_id(Z19)) == 100 * 10 ** 18
#     assert L_token.balanceOf(High_Risk_Insurer) == 0 * 10 ** 18
#     # verify InterestPool balance of InterestPoolCurrency tokens
#     assert InterestPoolCurrency.balanceOf(InterestPool.address) == 0
#     # verify multi_fungible_currency balances of InterestPool
#     assert InterestPool.i_currency_balance(Z19) == 20 * 10 ** 18
#     assert InterestPool.f_currency_balance(Z19) == 0
#     assert InterestPool.total_f_currency_balance() == 0
#     assert InterestPool.l_currency_balance() == 0
#     assert InterestPool.total_l_currency_balance() == 0
