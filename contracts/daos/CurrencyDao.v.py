# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20
from contracts.interfaces import MultiFungibleToken
from contracts.interfaces import ERC20TokenPool

from contracts.interfaces import ProtocolDao


# Structs
struct TokenAddress:
    eth: address
    l: address
    i: address
    f: address
    s: address
    u: address


struct Pool:
    currency: address
    name: string[64]
    address_: address
    operator: address
    hash: bytes32


LST: public(address)
protocol_dao: public(address)
# eth address of token => TokenAddress
token_addresses: public(map(address, TokenAddress))
# pool_hash => Pool
pools: public(map(bytes32, Pool))
# dao_type => dao_address
daos: public(map(int128, address))
# registry_type => registry_address
registries: public(map(int128, address))
# template_name => template_contract_address
templates: public(map(int128, address))

DAO_INTEREST_POOL: constant(int128) = 2
DAO_UNDERWRITER_POOL: constant(int128) = 3
DAO_MARKET: constant(int128) = 4
DAO_SHIELD_PAYOUT: constant(int128) = 5

REGISTRY_POOL_NAME: constant(int128) = 1

TEMPLATE_TOKEN_POOL: constant(int128) = 1
TEMPLATE_ERC20: constant(int128) = 6
TEMPLATE_MFT: constant(int128) = 7

CALLER_ESCAPE_HATCH_TOKEN_HOLDER: constant(int128) = 3

MFT_TYPE_F: constant(int128) = 1
MFT_TYPE_I: constant(int128) = 2
MFT_TYPE_S: constant(int128) = 3
MFT_TYPE_U: constant(int128) = 4

initialized: public(bool)
paused: public(bool)


@public
def initialize(
        _LST: address,
        _template_token_pool: address,
        _template_erc20: address,
        _template_mft: address,
        _pool_name_registry: address,
        _dao_interest_pool: address,
        _dao_underwriter_pool: address,
        _dao_market: address,
        _dao_shield_payout: address
        ) -> bool:
    assert not self.initialized
    self.initialized = True
    self.protocol_dao = msg.sender
    self.LST = _LST

    self.daos[DAO_INTEREST_POOL] = _dao_interest_pool
    self.daos[DAO_UNDERWRITER_POOL] = _dao_underwriter_pool
    self.daos[DAO_MARKET] = _dao_market
    self.daos[DAO_SHIELD_PAYOUT] = _dao_shield_payout

    self.registries[REGISTRY_POOL_NAME] = _pool_name_registry

    self.templates[TEMPLATE_TOKEN_POOL] = _template_token_pool
    self.templates[TEMPLATE_ERC20] = _template_erc20
    self.templates[TEMPLATE_MFT] = _template_mft

    return True


@private
@constant
def _pool_hash(_currency: address) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_currency, bytes32)
        )
    )


@private
@constant
def _mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return keccak256(
        concat(
            convert(self.protocol_dao, bytes32),
            convert(_address, bytes32),
            convert(_currency, bytes32),
            convert(_expiry, bytes32),
            convert(_underlying, bytes32),
            convert(_strike_price, bytes32)
        )
    )


@private
@constant
def _is_token_supported(_token: address) -> bool:
    return self.pools[self._pool_hash(_token)].address_.is_contract


@private
def _transfer_erc20(_token: address, _from: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).transferFrom(_from, _to, _value))


@private
def _deposit_token_to_pool(_token: address, _from: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # transfer currency to currency pool
    self._transfer_erc20(_token, _from, self.pools[_pool_hash].address_, _value)


@private
def _withdraw_token_from_pool(_token: address, _to: address, _value: uint256):
    # validate currency address
    _pool_hash: bytes32 = self._pool_hash(_token)
    assert self.pools[_pool_hash].address_.is_contract, "token is not supported"
    # release token from token pool
    assert_modifiable(ERC20TokenPool(self.pools[_pool_hash].address_).release(_to, _value))


@private
def _mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).mintAndAuthorizeMinter(_to, _value))


@private
def _burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256):
    assert_modifiable(ERC20(_token).burnAsAuthorizedMinter(_to, _value))


@private
@constant
def _mft_addresses(_token: address) -> (address, address, address, address, address):
    return self.token_addresses[_token].l, self.token_addresses[_token].i, self.token_addresses[_token].f, self.token_addresses[_token].s, self.token_addresses[_token].u


@private
def _wrap(_token: address, _from: address, _to: address, _value: uint256):
    # deposit currency from _from address
    self._deposit_token_to_pool(_token, _from, _value)
    # mint currency l_token to _to address
    self._mint_and_self_authorize_erc20(self.token_addresses[_token].l, _to, _value)


@private
def _unwrap(_token: address, _from: address, _to: address, _value: uint256):
    # burrn currency l_token from _from address
    self._burn_as_self_authorized_erc20(self.token_addresses[_token].l, _from, _value)
    # release currency to _to address
    self._withdraw_token_from_pool(_token, _to, _value)


@public
@constant
def mft_hash(_address: address, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bytes32:
    return self._mft_hash(_address, _currency, _expiry, _underlying, _strike_price)


@public
@constant
def is_token_supported(_token: address) -> bool:
    return self._is_token_supported(_token)


@public
@constant
def mft_addresses(_token: address) -> (address, address, address, address, address):
    return self._mft_addresses(_token)


@public
@constant
def f_token(_currency: address, _expiry: timestamp) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(
        self.token_addresses[_currency].f, _currency, _expiry, ZERO_ADDRESS, 0)

    return self.token_addresses[_currency].f, MultiFungibleToken(self.token_addresses[_currency].f).hash_to_id(_mft_hash)


@public
@constant
def i_token(_currency: address, _expiry: timestamp) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(
        self.token_addresses[_currency].i, _currency, _expiry, ZERO_ADDRESS, 0)

    return self.token_addresses[_currency].i, MultiFungibleToken(self.token_addresses[_currency].i).hash_to_id(_mft_hash)


@public
@constant
def s_token(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(self.token_addresses[_currency].s,
        _currency, _expiry, _underlying, _strike_price)

    return self.token_addresses[_currency].s, MultiFungibleToken(self.token_addresses[_currency].s).hash_to_id(_mft_hash)


@public
@constant
def u_token(_currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> (address, uint256):
    _mft_hash: bytes32 = self._mft_hash(self.token_addresses[_currency].u,
        _currency, _expiry, _underlying, _strike_price)

    return self.token_addresses[_currency].u, MultiFungibleToken(self.token_addresses[_currency].u).hash_to_id(_mft_hash)


@public
def mint_and_self_authorize_erc20(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    self._mint_and_self_authorize_erc20(_token, _to, _value)
    return True


@public
def burn_as_self_authorized_erc20(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    self._burn_as_self_authorized_erc20(_token, _to, _value)
    return True


@public
@constant
def pool_hash(_token: address) -> bytes32:
    return self._pool_hash(_token)


# Escape-hatches
@private
def _pause():
    assert not self.paused
    self.paused = True


@private
def _unpause():
    assert self.paused
    self.paused = False

@public
def pause() -> bool:
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._pause()
    return True


@public
def unpause() -> bool:
    assert self.initialized
    assert msg.sender == self.protocol_dao
    self._unpause()
    return True


@private
def _transfer_balance_erc20(_token: address):
    assert_modifiable(ERC20(_token).transfer(
        ProtocolDao(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        ERC20(_token).balanceOf(self)
    ))


@private
def _transfer_balance_mft(_token: address,
    _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256):
    _mft_hash: bytes32 = self._mft_hash(_token, _currency, _expiry, _underlying, _strike_price)
    _id: uint256 = MultiFungibleToken(_token).hash_to_id(_mft_hash)
    _balance: uint256 = MultiFungibleToken(_token).balanceOf(self, _id)
    assert_modifiable(MultiFungibleToken(_token).safeTransferFrom(
        self,
        ProtocolDao(self.protocol_dao).authorized_callers(CALLER_ESCAPE_HATCH_TOKEN_HOLDER),
        _id, _balance, EMPTY_BYTES32
    ))


@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = _currency
    if _is_l:
        _token = self.token_addresses[_currency].l
    self._transfer_balance_erc20(_currency)
    return True


@public
def escape_hatch_mft(_mft_type: int128, _currency: address, _expiry: timestamp, _underlying: address, _strike_price: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.protocol_dao
    _token: address = ZERO_ADDRESS
    if _mft_type == MFT_TYPE_F:
        _token = self.token_addresses[_currency].f
    if _mft_type == MFT_TYPE_I:
        _token = self.token_addresses[_currency].i
    if _mft_type == MFT_TYPE_S:
        _token = self.token_addresses[_currency].s
    if _mft_type == MFT_TYPE_U:
        _token = self.token_addresses[_currency].u
    assert not _token == ZERO_ADDRESS
    self._transfer_balance_mft(_token, _currency, _expiry, _underlying, _strike_price)
    return True


@public
def set_template(_template_type: int128, _address: address) -> bool:
    assert self.initialized
    assert msg.sender == self.protocol_dao
    assert _template_type == TEMPLATE_TOKEN_POOL or \
           _template_type == TEMPLATE_ERC20 or \
           _template_type == TEMPLATE_MFT
    self.templates[_template_type] = _address
    return True


@public
def set_token_support(_token: address, _is_active: bool) -> bool:
    assert self.initialized
    assert not _token == self.LST
    assert msg.sender == self.protocol_dao
    assert _token.is_contract
    _pool_hash: bytes32 = self._pool_hash(_token)
    if _is_active:
        _name: string[64] = ERC20(_token).name()
        _symbol: string[32] = ERC20(_token).symbol()
        _decimals: uint256 = ERC20(_token).decimals()
        assert self.pools[_pool_hash].address_ == ZERO_ADDRESS, "token pool already exists"
        _pool_address: address = create_forwarder_to(self.templates[TEMPLATE_TOKEN_POOL])
        assert_modifiable(ERC20TokenPool(_pool_address).initialize(_token))
        # l token
        _l_address: address = create_forwarder_to(self.templates[TEMPLATE_ERC20])
        # _l_currency_name: string[64] = concat("L ", slice(_name, start=0, len=62))
        # _l_currency_symbol: string[32] = concat("L", slice(_symbol, start=0, len=31))
        assert_modifiable(ERC20(_l_address).initialize(
            _name, _symbol, _decimals, 0))
        # i token
        _i_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_i_address).initialize(self.protocol_dao, [
            self, self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
            self.daos[DAO_MARKET], ZERO_ADDRESS
        ]))
        # f token
        _f_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_f_address).initialize(self.protocol_dao, [
            self.daos[DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))
        # s token
        _s_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_s_address).initialize(self.protocol_dao, [
            self.daos[DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))
        # u token
        _u_address: address = create_forwarder_to(self.templates[TEMPLATE_MFT])
        assert_modifiable(MultiFungibleToken(_u_address).initialize(self.protocol_dao, [
            self.daos[DAO_MARKET],
            ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS, ZERO_ADDRESS
        ]))

        self.pools[_pool_hash] = Pool({
            currency: _token,
            name: _name,
            address_: _pool_address,
            operator: self,
            hash: _pool_hash
        })
        self.token_addresses[_token] = TokenAddress({
            eth: _token,
            l: _l_address,
            i: _i_address,
            f: _f_address,
            s: _s_address,
            u: _u_address
        })


    else:
        assert not self.pools[_pool_hash].address_ == ZERO_ADDRESS, "currency pool does not exist"
        clear(self.pools[_pool_hash].address_)
        clear(self.pools[_pool_hash].name)
        assert_modifiable(ERC20TokenPool(self.pools[_pool_hash].address_).destroy())

    return True


@public
def wrap(_token: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._wrap(_token, msg.sender, msg.sender, _value)

    return True


@public
def unwrap(_token: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    self._unwrap(_token, msg.sender, msg.sender, _value)

    return True


@public
def authorized_unwrap(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._unwrap(_token, msg.sender, _to, _value)

    return True


@public
def authorized_transfer_l(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL]
    ]
    self._transfer_erc20(self.token_addresses[_token].l, _from, _to, _value)
    return True


@public
def authorized_transfer_erc20(_token: address, _from: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender in [
        self.daos[DAO_INTEREST_POOL], self.daos[DAO_UNDERWRITER_POOL],
        self.registries[REGISTRY_POOL_NAME]
    ]
    self._transfer_erc20(_token, _from, _to, _value)
    return True


@public
def authorized_deposit_token(_token: address, _from: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._deposit_token_to_pool(_token, _from, _value)

    return True


@public
def authorized_withdraw_token(_token: address, _to: address, _value: uint256) -> bool:
    assert self.initialized
    assert not self.paused
    assert msg.sender == self.daos[DAO_MARKET]
    self._withdraw_token_from_pool(_token, _to, _value)
    return True
