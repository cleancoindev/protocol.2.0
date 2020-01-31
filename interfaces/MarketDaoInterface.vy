# Functions

@public
def initialize(_LST: address, _dao_currency: address, _dao_interest_pool: address, _dao_underwriter_pool: address, _dao_shield_payout: address, _registry_position: address, _template_auction_erc20: address) -> bool:
    pass

@constant
@public
def s_payoff(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def u_payoff(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> uint256:
    pass

@constant
@public
def currency_remaining_for_auction(_loan_market_hash: bytes32) -> uint256:
    pass

@constant
@public
def liquidated_underlying_value(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _currency_value: uint256) -> uint256:
    pass

@constant
@public
def shield_market_hash(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bytes32:
    pass

@constant
@public
def loan_market_hash(_currency: address, _expiry: uint256(sec, positional), _underlying: address) -> bytes32:
    pass

@constant
@public
def currency_underlying_pair_hash(_currency: address, _underlying: address) -> bytes32:
    pass

@public
def set_template(_template_type: int128, _address: address) -> bool:
    pass

@public
def set_registry(_registry_type: int128, _address: address) -> bool:
    pass

@public
def set_price_oracle(_currency: address, _underlying: address, _oracle: address) -> bool:
    pass

@constant
@public
def maximum_liability_for_currency_market(_currency: address, _expiry: uint256(sec, positional)) -> uint256:
    pass

@public
def set_maximum_liability_for_currency_market(_currency: address, _expiry: uint256(sec, positional), _value: uint256) -> bool:
    pass

@constant
@public
def maximum_liability_for_loan_market(_currency: address, _expiry: uint256(sec, positional), _underlying: address) -> uint256:
    pass

@public
def set_maximum_liability_for_loan_market(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _value: uint256) -> bool:
    pass

@public
def set_auction_slippage_percentage(_value: uint256) -> bool:
    pass

@public
def set_auction_maximum_discount_percentage(_value: uint256) -> bool:
    pass

@public
def set_auction_discount_duration(_value: uint256(sec)) -> bool:
    pass

@public
def pause() -> bool:
    pass

@public
def unpause() -> bool:
    pass

@public
def escape_hatch_auction(_currency: address, _expiry: uint256(sec, positional), _underlying: address) -> bool:
    pass

@public
def escape_hatch_erc20(_currency: address, _is_l: bool) -> bool:
    pass

@public
def escape_hatch_mft(_mft_type: int128, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def open_shield_market(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256, _s_address: address, _s_id: uint256, _u_address: address, _u_id: uint256) -> bool:
    pass

@public
def settle_loan_market(_loan_market_hash: bytes32):
    pass

@public
def process_auction_purchase(_currency: address, _expiry: uint256(sec, positional), _underlying: address, _purchaser: address, _currency_value: uint256, _underlying_value: uint256, _is_auction_active: bool) -> (bool, bool):
    pass

@public
def open_position(_borrower: address, _currency_value: uint256, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def close_position(_borrower: address, _currency_value: uint256, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@public
def close_liquidated_position(_borrower: address, _currency_value: uint256, _currency: address, _expiry: uint256(sec, positional), _underlying: address, _strike_price: uint256) -> bool:
    pass

@constant
@public
def LST() -> address:
    pass

@constant
@public
def protocol_dao() -> address:
    pass

@constant
@public
def daos(arg0: int128) -> address:
    pass

@constant
@public
def registries(arg0: int128) -> address:
    pass

@constant
@public
def templates(arg0: int128) -> address:
    pass

@constant
@public
def expiry_markets__expiry(arg0: uint256(sec, positional)) -> uint256(sec, positional):
    pass

@constant
@public
def expiry_markets__id(arg0: uint256(sec, positional)) -> int128:
    pass

@constant
@public
def next_expiry_market_id() -> int128:
    pass

@constant
@public
def expiry_market_id_to_timestamp(arg0: int128) -> uint256(sec, positional):
    pass

@constant
@public
def loan_markets__currency(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def loan_markets__underlying(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__settlement_price(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__total_s_payout_value(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__status(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__liability(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__collateral(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__auction_curve(arg0: bytes32) -> address:
    pass

@constant
@public
def loan_markets__auction_currency_raised(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__auction_underlying_sold(arg0: bytes32) -> uint256:
    pass

@constant
@public
def loan_markets__shield_market_count(arg0: bytes32) -> int128:
    pass

@constant
@public
def loan_markets__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def loan_markets__id(arg0: bytes32) -> int128:
    pass

@constant
@public
def next_loan_market_id(arg0: uint256(sec, positional)) -> int128:
    pass

@constant
@public
def loan_market_id_to_hash(arg0: uint256(sec, positional), arg1: int128) -> bytes32:
    pass

@constant
@public
def shield_markets__currency(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__expiry(arg0: bytes32) -> uint256(sec, positional):
    pass

@constant
@public
def shield_markets__underlying(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__strike_price(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__s_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__s_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__u_address(arg0: bytes32) -> address:
    pass

@constant
@public
def shield_markets__u_id(arg0: bytes32) -> uint256:
    pass

@constant
@public
def shield_markets__hash(arg0: bytes32) -> bytes32:
    pass

@constant
@public
def shield_markets__id(arg0: bytes32) -> int128:
    pass

@constant
@public
def next_shield_market_id(arg0: bytes32) -> int128:
    pass

@constant
@public
def shield_market_id_to_hash(arg0: bytes32, arg1: int128) -> bytes32:
    pass

@constant
@public
def price_oracles(arg0: bytes32) -> address:
    pass

@constant
@public
def maximum_market_liabilities(arg0: bytes32) -> uint256:
    pass

@constant
@public
def auction_slippage_percentage() -> uint256:
    pass

@constant
@public
def auction_maximum_discount_percentage() -> uint256:
    pass

@constant
@public
def auction_discount_duration() -> uint256(sec):
    pass

@constant
@public
def LOAN_MARKET_STATUS_OPEN() -> uint256:
    pass

@constant
@public
def LOAN_MARKET_STATUS_SETTLING() -> uint256:
    pass

@constant
@public
def LOAN_MARKET_STATUS_CLOSED() -> uint256:
    pass

@constant
@public
def initialized() -> bool:
    pass

@constant
@public
def paused() -> bool:
    pass
