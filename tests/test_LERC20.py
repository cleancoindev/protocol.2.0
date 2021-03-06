import pytest
from brownie import *
from web3 import Web3
from web3.exceptions import (
    ValidationError,
)
from conftest import (
    PROTOCOL_CONSTANTS,
    MAX_UINT256,
    ZERO_ADDRESS
)


def test_initial_state(accounts, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    a1, a2, a3 = accounts[1:4]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    assert Lend_token.balanceOf(_lend_token_holder) == 0
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    assert Lend_token.balanceOf(_lend_token_holder) == Web3.toWei(1000, 'ether')
    # get L_Lend_token
    L_Lend_token_address = CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone})
    test_token = get_ERC20_contract(address=L_Lend_token_address)
    # Check total supply, name, symbol and decimals are correctly set
    assert test_token.totalSupply({'from': anyone}) == 0
    assert test_token.name({'from': anyone}) == 'Wrapped Test Lend Token'
    assert test_token.symbol({'from': anyone}) == 'LDAI'
    assert test_token.decimals({'from': anyone}) == 18
    # Check several account balances as 0
    assert test_token.balanceOf(a1, {'from': anyone}) == 0
    assert test_token.balanceOf(a2, {'from': anyone}) == 0
    assert test_token.balanceOf(a3, {'from': anyone}) == 0
    # Check several allowances as 0
    assert test_token.allowance(a1, a1, {'from': anyone}) == 0
    assert test_token.allowance(a1, a2, {'from': anyone}) == 0
    assert test_token.allowance(a1, a3, {'from': anyone}) == 0
    assert test_token.allowance(a2, a3, {'from': anyone}) == 0


def test_mint_and_burn(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 500 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    L_Lend_token_address = CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone})
    test_token = get_ERC20_contract(address=L_Lend_token_address)
    # Test scenario were mints 2 to _lend_token_holder, burns twice (check balance consistency)
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(2, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert test_token.balanceOf(_lend_token_holder, {'from': anyone}) == Web3.toWei(2, 'ether')
    test_token.burn(Web3.toWei(2, 'ether'), {'from': _lend_token_holder})
    assert test_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), {'from': _lend_token_holder}))
    assert test_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    # Test scenario were mintes 0 to _lend_token_holder, burns (check balance consistency, false burn)
    CurrencyDaoContract.wrap(Lend_token.address, 0, {'from': _lend_token_holder, 'gas': 145000})
    assert test_token.balanceOf(_lend_token_holder, {'from': anyone}) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(2, 'ether'), {'from': _lend_token_holder}))
    # Check that _lend_token_holder cannot mint
    assert_tx_failed(lambda: test_token.mint(_lend_token_holder, Web3.toWei(2, 'ether'), {'from': _lend_token_holder}))


def test_totalSupply(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    anyone = accounts[-1]
    # Test total supply initially, after mint, between two burns, and after failed burn
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    assert test_token.totalSupply({'from': anyone}) == 0
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(2, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert test_token.totalSupply({'from': anyone}) == Web3.toWei(2, 'ether')
    test_token.burn(Web3.toWei(1, 'ether'), {'from': _lend_token_holder})
    assert test_token.totalSupply({'from': anyone}) == Web3.toWei(1, 'ether')
    test_token.burn(Web3.toWei(1, 'ether'), {'from': _lend_token_holder})
    assert test_token.totalSupply({'from': anyone}) == 0
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), {'from': _lend_token_holder}))
    assert test_token.totalSupply({'from': anyone}) == 0
    # Test that 0-valued mint can't affect supply
    CurrencyDaoContract.wrap(Lend_token.address, 0, {'from': _lend_token_holder, 'gas': 145000})
    assert test_token.totalSupply({'from': anyone}) == 0


def test_transfer(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    minter, a1, a2 = accounts[0:3]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), {'from': a2}))
    # _lend_token_holder wraps 2 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(2, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    test_token.burn(Web3.toWei(1, 'ether'), {'from': _lend_token_holder})
    test_token.transfer(a2, Web3.toWei(1, 'ether'), {'from': _lend_token_holder})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), {'from': _lend_token_holder}))
    test_token.burn(Web3.toWei(1, 'ether'), {'from': a2})
    assert_tx_failed(lambda: test_token.burn(Web3.toWei(1, 'ether'), {'from': a2}))
    # Ensure transfer fails with insufficient balance
    assert_tx_failed(lambda: test_token.transfer(_lend_token_holder, Web3.toWei(1, 'ether'), {'from': a2}))
    # Ensure 0-transfer always succeeds
    test_token.transfer(_lend_token_holder, 0, {'from': a2})
    # Ensure transfer fails when recipient is ZERO_ADDRESS
    assert_tx_failed(lambda: test_token.transfer(ZERO_ADDRESS, 0, {'from': a2}))


def test_maxInts(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract, Deployer, Governor,
    Whale, Test_token_With_Zero_Supply,
    ProtocolDaoContract):
    Test_token = Test_token_With_Zero_Supply
    minter, a1, a2 = accounts[0:3]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _test_token_holder
    _test_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Test_token.address, True, {'from': Governor, 'gas': 2100000})
    # Whale mints MAX_UINT256 Lend_tokens
    Test_token.mint(Whale, MAX_UINT256, {'from': Whale})
    # _test_token_holder buys 1000 lend token from a 3rd party exchange
    Test_token.transfer(_test_token_holder, MAX_UINT256, {'from': Whale})
    # _test_token_holder authorizes CurrencyDaoContract to spend MAX_UINT256 Test_token
    Test_token.approve(CurrencyDaoContract.address, MAX_UINT256, {'from': _test_token_holder})
    # get L_Test_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Test_token.address, {'from': anyone}))
    CurrencyDaoContract.wrap(Test_token.address, MAX_UINT256, {'from': _test_token_holder, 'gas': 150000})
    # Assert that after obtaining max number of tokens, a1 can transfer those but no more
    assert test_token.balanceOf(_test_token_holder, {'from': anyone}) == MAX_UINT256
    test_token.transfer(a2, MAX_UINT256, {'from': _test_token_holder})
    assert test_token.balanceOf(a2, {'from': anyone}) == MAX_UINT256
    assert test_token.balanceOf(_test_token_holder, {'from': anyone}) == 0
    # [ next line should never work in EVM ]
    assert_tx_failed(lambda: test_token.mint(a2, 1, {'from': minter}))
    with pytest.raises(OverflowError):
        test_token.transfer(_test_token_holder, MAX_UINT256 + 1, {'from': a2})
    # Check approve/allowance w max possible token values
    assert test_token.balanceOf(a2, {'from': anyone}) == MAX_UINT256
    test_token.approve(_test_token_holder, MAX_UINT256, {'from': a2})
    test_token.transferFrom(a2, _test_token_holder, MAX_UINT256, {'from': _test_token_holder})
    assert test_token.balanceOf(_test_token_holder, {'from': anyone}) == MAX_UINT256
    assert test_token.balanceOf(a2, {'from': anyone}) == 0
    # Check that max amount can be burned
    test_token.burn(MAX_UINT256, {'from': _test_token_holder})
    assert test_token.balanceOf(_test_token_holder, {'from': anyone}) == 0


def test_transferFrom_and_Allowance(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    minter, a1, a2, a3 = accounts[0:4]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    test_token.transfer(a2, 1, {'from': _lend_token_holder})
    test_token.burn(1, {'from': _lend_token_holder})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.transferFrom(_lend_token_holder, a3, 1, {'from': a2}))
    test_token.transferFrom(_lend_token_holder, a3, 0, {'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, {'from': _lend_token_holder})
    assert test_token.allowance(_lend_token_holder, a2, {'from': anyone}) == 1
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.transferFrom(_lend_token_holder, a3, 1, {'from': a3}))
    assert test_token.balanceOf(a2, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    # Ensure transferFrom fails when recipient is ZERO_ADDRESS
    assert_tx_failed(lambda: test_token.transferFrom(a2, ZERO_ADDRESS, 1, {'from': _lend_token_holder}))
    test_token.transferFrom(a2, a3, 1, {'from': _lend_token_holder})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, {'from': _lend_token_holder}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, {'from': _lend_token_holder})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    assert_tx_failed(lambda: test_token.transferFrom(a2, a3, 1, {'from': _lend_token_holder}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 2, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 5, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 5


def test_burnFrom_and_Allowance(accounts, assert_tx_failed, get_ERC20_contract, get_CurrencyDao_contract,
    Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    minter, a1, a2, a3 = accounts[0:4]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    assert_tx_failed(lambda: test_token.burn(1, {'from': a2}))
    test_token.transfer(a2, 1, {'from': _lend_token_holder})
    test_token.burn(1, {'from': _lend_token_holder})
    # This should fail; no allowance or balance (0 always succeeds)
    assert_tx_failed(lambda: test_token.burnFrom(_lend_token_holder, 1, {'from': a2}))
    test_token.burnFrom(_lend_token_holder, 0, {'from': a2})
    # Correct call to approval should update allowance (but not for reverse pair)
    test_token.approve(a2, 1, {'from': _lend_token_holder})
    assert test_token.allowance(_lend_token_holder, a2, {'from': anyone}) == 1
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    # transferFrom should succeed when allowed, fail with wrong sender
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': a3}))
    assert test_token.balanceOf(a2, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    test_token.burnFrom(a2, 1, {'from': _lend_token_holder})
    # Allowance should be correctly updated after transferFrom
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    # transferFrom with no funds should fail despite approval
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': _lend_token_holder}))
    # 0-approve should not change balance or allow transferFrom to change balance
    test_token.transfer(a2, 1, {'from': _lend_token_holder})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    assert_tx_failed(lambda: test_token.burnFrom(a2, 1, {'from': _lend_token_holder}))
    # Test that if non-zero approval exists, 0-approval is NOT required to proceed
    # a non-conformant implementation is described in countermeasures at
    # https://docs.google.com/document/d/1YLPtQxZu1UAvO9cZ1O2RPXBbT0mooh4DYKjA_jp-RLM/edit#heading=h.m9fhqynw2xvt
    # the final spec insists on NOT using this behavior
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 1, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 1
    test_token.approve(_lend_token_holder, 2, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 2
    # Check that approving 0 then amount also works
    test_token.approve(_lend_token_holder, 0, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 0
    test_token.approve(_lend_token_holder, 5, {'from': a2})
    assert test_token.allowance(a2, _lend_token_holder, {'from': anyone}) == 5
    # Check that burnFrom to ZERO_ADDRESS failed
    assert_tx_failed(lambda: test_token.burnFrom(
        ZERO_ADDRESS, 0, {'from': _lend_token_holder}))


def test_raw_logs(accounts, get_log_args, get_ERC20_contract, get_CurrencyDao_contract, Deployer, Governor,
    Whale, Lend_token,
    ProtocolDaoContract):
    minter, a1, a2, a3 = accounts[0:4]
    anyone = accounts[-1]
    # get CurrencyDaoContract
    CurrencyDaoContract = get_CurrencyDao_contract(address=ProtocolDaoContract.daos(PROTOCOL_CONSTANTS['DAO_CURRENCY']))
    # assign one of the accounts as _lend_token_holder
    _lend_token_holder = accounts[5]
    # initialize CurrencyDaoContract
    ProtocolDaoContract.initialize_currency_dao({'from': Deployer})
    ProtocolDaoContract.set_token_support(Lend_token.address, True, {'from': Governor, 'gas': 2000000})
    # _lend_token_holder buys 1000 lend token from a 3rd party exchange
    Lend_token.transfer(_lend_token_holder, Web3.toWei(1000, 'ether'), {'from': Whale})
    # _lend_token_holder authorizes CurrencyDaoContract to spend 800 Lend_token
    Lend_token.approve(CurrencyDaoContract.address,  Web3.toWei(800, 'ether'), {'from': _lend_token_holder})
    # get L_Lend_token
    test_token = get_ERC20_contract(address=CurrencyDaoContract.token_addresses__l(Lend_token.address, {'from': anyone}))
    # _lend_token_holder wraps 800 Lend_token to L_lend_token
    tx = CurrencyDaoContract.wrap(Lend_token.address, Web3.toWei(800, 'ether'), {'from': _lend_token_holder, 'gas': 145000})
    # Check that mint appropriately emits Transfer event
    args = get_log_args(tx, 'Transfer', idx=1)
    assert args['_from'] == ZERO_ADDRESS
    assert args['_to'] == _lend_token_holder
    assert args['_value'] == Web3.toWei(800, 'ether')

    # Check that burn appropriately emits Transfer event
    args = get_log_args(test_token.burn(1, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == _lend_token_holder
    assert args['_to'] == ZERO_ADDRESS
    assert args['_value'] == 1

    args = get_log_args(test_token.burn(0, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == _lend_token_holder
    assert args['_to'] == ZERO_ADDRESS
    assert args['_value'] == 0

    # Check that transfer appropriately emits Transfer event
    args = get_log_args(test_token.transfer(
        a2, 1, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == _lend_token_holder
    assert args['_to'] == a2
    assert args['_value'] == 1

    args = get_log_args(test_token.transfer(
        a2, 0, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == _lend_token_holder
    assert args['_to'] == a2
    assert args['_value'] == 0

    # Check that approving amount emits events
    args = get_log_args(test_token.approve(_lend_token_holder, 1, {'from': a2}), 'Approval')
    assert args['_owner'] == a2
    assert args['_spender'] == _lend_token_holder
    assert args['_value'] == 1

    args = get_log_args(test_token.approve(a2, 0, {'from': a3}), 'Approval')
    assert args['_owner'] == a3
    assert args['_spender'] == a2
    assert args['_value'] == 0

    # Check that transferFrom appropriately emits Transfer event
    args = get_log_args(test_token.transferFrom(
        a2, a3, 1, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == a2
    assert args['_to'] == a3
    assert args['_value'] == 1

    args = get_log_args(test_token.transferFrom(
        a2, a3, 0, {'from': _lend_token_holder}), 'Transfer')
    assert args['_from'] == a2
    assert args['_to'] == a3
    assert args['_value'] == 0
