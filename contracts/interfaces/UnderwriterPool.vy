# Functions

@public
def initialize(_dao_protocol: address, _accepts_public_contributions: bool, _operator: address, _fee_percentage_per_i_token: uint256, _fee_percentage_per_s_token: uint256, _name: string[64], _symbol: string[32], _initial_exchange_rate: uint256, _currency: address, _l_address: address, _i_address: address, _s_address: address, _u_address: address, _dao_shield_payout: address, _erc20_currency_template_address: address) -> bool:
    pass

@constant
@public
def total_pool_share_token_supply() -> uint256:
    pass

@constant
@public
def l_token_balance() -> uint256:
    pass

@constant
@public
def i_token_balance(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def s_token_balance(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def u_token_balance(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def total_u_token_balance() -> uint256:
    pass

@constant
@public
def total_l_token_balance() -> uint256:
    pass

@constant
@public
def exchange_rate() -> uint256:
    pass

@constant
@public
def estimated_pool_share_tokens(_l_token_value: uint256) -> uint256:
    pass

@constant
@public
def i_token_fee(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def s_token_fee(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@public
def setShouldReject(_value: bool):
    pass

@constant
@public
def supportsInterface(interfaceID: bytes[10]) -> bool:
    pass

@public
def onMFTReceived(_operator: address, _from: address, _id: uint256, _value: uint256, _data: bytes32) -> bytes[10]:
    pass

@public
def set_public_contribution_acceptance(_acceptance: bool) -> bool:
    pass

@public
def support_mft(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _i_cost_per_day: uint256, _s_cost_per_day: uint256) -> bool:
    pass

@public
def withdraw_mft_support(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def set_i_cost_per_day(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def set_s_cost_per_day(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def set_fee_percentage_per_i_token(_value: uint256) -> bool:
    pass

@public
def set_fee_percentage_per_s_token(_value: uint256) -> bool:
    pass

@public
def withdraw_earnings() -> bool:
    pass

@public
def deregister() -> bool:
    pass

@public
def increment_s_tokens(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _l_token_value: uint256) -> bool:
    pass

@public
def decrement_s_tokens(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _l_token_value: uint256) -> bool:
    pass

@public
def exercise_u_tokens(_name: string[64], _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _value: uint256) -> bool:
    pass

@public
def contribute(_l_token_value: uint256) -> bool:
    pass

@public
def withdraw_contribution(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _pool_share_token_value: uint256) -> bool:
    pass

@public
def purchase_i_tokens(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _i_token_value: uint256, _fee_in_l_token: uint256) -> bool:
    pass

@public
def purchase_s_tokens(_expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _s_token_value: uint256, _fee_in_l_token: uint256) -> bool:
    pass

@constant
@public
def protocol_dao() -> address:
    pass

@constant
@public
def owner() -> address:
    pass

@constant
@public
def daos(arg0: uint256) -> address:
    pass

@constant
@public
def operator() -> address:
    pass

@constant
@public
def name() -> string[64]:
    pass

@constant
@public
def symbol() -> string[32]:
    pass

@constant
@public
def initial_exchange_rate() -> uint256:
    pass

@constant
@public
def currency() -> address:
    pass

@constant
@public
def l_address() -> address:
    pass

@constant
@public
def i_address() -> address:
    pass

@constant
@public
def s_address() -> address:
    pass

@constant
@public
def u_address() -> address:
    pass

@constant
@public
def pool_share_token() -> address:
    pass

@constant
@public
def fee_percentage_per_i_token() -> uint256:
    pass

@constant
@public
def fee_percentage_per_s_token() -> uint256:
    pass

@constant
@public
def operator_earnings() -> uint256:
    pass

@constant
@public
def markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def markets__i_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__s_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__u_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__i_cost_per_day(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__s_cost_per_day(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__is_active(arg0: bytes32) -> bool:
    pass

@constant
@public
def markets__id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def markets__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def market_id_to_hash(arg0: uint256) -> bytes32:
    pass

@constant
@public
def next_market_id() -> uint256:
    pass

@constant
@public
def DAO_TYPE_SHIELD_PAYOUT() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def accepts_public_contributions() -> bool:
    pass

@constant
@public
def shouldReject() -> bool:
    pass

@constant
@public
def lastData() -> bytes32:
    pass

@constant
@public
def lastOperator() -> address:
    pass

@constant
@public
def lastFrom() -> address:
    pass

@constant
@public
def lastId() -> uint256:
    pass

@constant
@public
def lastValue() -> uint256:
    pass
