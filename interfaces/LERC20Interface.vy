# Events

Transfer: event({_from: address, _to: address, _value: uint256})
Approval: event({_owner: address, _spender: address, _value: uint256})

# Functions

@public
def initialize(_name: string[64], _symbol: string[32], _decimals: uint256, _supply: uint256) -> bool:
    pass

@constant
@public
def totalSupply() -> uint256:
    pass

@constant
@public
def allowance(_owner: address, _spender: address) -> uint256:
    pass

@public
def transfer(_to: address, _value: uint256) -> bool:
    pass

@public
def transferFrom(_from: address, _to: address, _value: uint256) -> bool:
    pass

@public
def approve(_spender: address, _value: uint256) -> bool:
    pass

@public
def mint(_to: address, _value: uint256) -> bool:
    pass

@public
def mintAndAuthorizeMinter(_to: address, _value: uint256) -> bool:
    pass

@public
def burn(_value: uint256):
    pass

@public
def burnFrom(_to: address, _value: uint256) -> bool:
    pass

@public
def burnAsAuthorizedMinter(_to: address, _value: uint256) -> bool:
    pass

@constant
@public
def name() -> string[72]:
    pass

@constant
@public
def symbol() -> string[33]:
    pass

@constant
@public
def decimals() -> uint256:
    pass

@constant
@public
def balanceOf(arg0: address) -> uint256:
    pass
