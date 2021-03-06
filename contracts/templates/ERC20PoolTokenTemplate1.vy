# @version 0.1.0b16
# @notice Implementation of Lendroid v2 - ERC20 Pool Token. This Template will be provided by the Lendroid Team.
# @dev THIS CONTRACT IS CURRENTLY UNDER AUDIT
# @author Vignesh (Vii) Meenakshi Sundaram (@vignesh-msundaram)
# Lendroid Foundation

from vyper.interfaces import ERC20

implements: ERC20

Transfer: event({_from: indexed(address), _to: indexed(address), _value: uint256})
Approval: event({_owner: indexed(address), _spender: indexed(address), _value: uint256})

name: public(string[64])
symbol: public(string[100])
decimals: public(uint256)

# NOTE: By declaring `balanceOf` as public, vyper automatically generates a 'balanceOf()' getter
#       method to allow access to account balances.
#       The _KeyType will become a required parameter for the getter and it will return _ValueType.
#       See: https://vyper.readthedocs.io/en/v0.1.0-beta.8/types.html?highlight=getter#mappings
balanceOf: public(map(address, uint256))
allowances: map(address, map(address, uint256))
total_supply: uint256
minter: address

initialized: bool


@public
def initialize(_name: string[64], _symbol: string[100], _decimals: uint256, _supply: uint256) -> bool:
    """
      Token symbol is a string array of size 100 instead of 32.
      This is because the symbol is of the format <pool_name>.<pool_type>.<currency_symbol>.
      Eg, LionFury1.RF.DAI (Interest Pool Token), LionFury7.RU.DAI (Underwriter Pool Token)
    """
    assert not self.initialized
    self.initialized = True
    init_supply: uint256 = _supply * 10 ** _decimals
    self.name = _name
    self.symbol = _symbol
    self.decimals = _decimals
    self.balanceOf[msg.sender] = init_supply
    self.total_supply = init_supply
    self.minter = msg.sender
    log.Transfer(ZERO_ADDRESS, msg.sender, init_supply)

    return True


@public
@constant
def totalSupply() -> uint256:
    """
        @dev Total number of tokens in existence.
    """
    return self.total_supply


@public
@constant
def allowance(_owner : address, _spender : address) -> uint256:
    """
    @dev Function to check the amount of tokens that an owner allowed to a spender.
    @param _owner The address which owns the funds.
    @param _spender The address which will spend the funds.
    @return An uint256 specifying the amount of tokens still available for the spender.
    """
    return self.allowances[_owner][_spender]


@public
def transfer(_to : address, _value : uint256) -> bool:
    """
    @dev Transfer token for a specified address
    @param _to The address to transfer to.
    @param _value The amount to be transferred.
    """
    # verify _to address is not 0x0
    assert not _to == ZERO_ADDRESS
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[msg.sender] -= _value
    self.balanceOf[_to] += _value
    log.Transfer(msg.sender, _to, _value)
    return True


@public
def transferFrom(_from : address, _to : address, _value : uint256) -> bool:
    """
     @dev Transfer tokens from one address to another.
          Note that while this function emits a Transfer event, this is not required as per the specification,
          and other compliant implementations may not emit the event.
     @param _from address The address which you want to send tokens from
     @param _to address The address which you want to transfer to
     @param _value uint256 the amount of tokens to be transferred
    """
    # verify _to address is not 0x0
    assert not _to == ZERO_ADDRESS
    # NOTE: vyper does not allow underflows
    #       so the following subtraction would revert on insufficient balance
    self.balanceOf[_from] -= _value
    self.balanceOf[_to] += _value
    # NOTE: vyper does not allow underflows
    #      so the following subtraction would revert on insufficient allowance
    self.allowances[_from][msg.sender] -= _value
    log.Transfer(_from, _to, _value)
    return True


@private
def _approve(_owner: address, _spender : address, _value : uint256):
    """
    @dev Internal function to approve the owner address to spend the specified amount of tokens on behalf of spender.
         Beware that changing an allowance with this method brings the risk that someone may use both the old
         and the new allowance by unfortunate transaction ordering. One possible solution to mitigate this
         race condition is to first reduce the spender's allowance to 0 and set the desired value afterwards:
         https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
    @param _spender The address which will spend the funds.
    @param _value The amount of tokens to be spent.
    """
    self.allowances[_owner][_spender] = _value
    log.Approval(_owner, _spender, _value)


@public
def approve(_spender : address, _value : uint256) -> bool:
    """
    @dev Approve the passed address to spend the specified amount of tokens on behalf of msg.sender.
    @param _spender The address which will spend the funds.
    @param _value The amount of tokens to be spent.
    """
    self._approve(msg.sender, _spender, _value)
    return True


@private
def _mint(_minter: address, _to: address, _value: uint256):
    """
    @dev Internal function that mints an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    assert _minter == self.minter
    # verify _to address is not 0x0
    assert not _to == ZERO_ADDRESS
    self.total_supply += _value
    self.balanceOf[_to] += _value
    log.Transfer(ZERO_ADDRESS, _to, _value)


@public
def mint(_to: address, _value: uint256) -> bool:
    """
    @dev Mint an amount of the token and assigns it to an account.
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    self._mint(msg.sender, _to, _value)
    return True


@public
def mintAndAuthorizeMinter(_to: address, _value: uint256) -> bool:
    """
    @dev Mint an amount of the token and assigns it to an account.
         Also, approve the minter address to spend the specified amount of tokens on behalf of to account
         This encapsulates the modification of balances such that the
         proper events are emitted.
    @param _to The account that will receive the created tokens.
    @param _value The amount that will be created.
    """
    self._mint(msg.sender, _to, _value)
    self._approve(_to, msg.sender, _value)
    return True


@private
def _burn(_from: address, _value: uint256):
    """
    @dev Internal function that burns an amount of the token of a given
         account.
    @param _from The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert _from != ZERO_ADDRESS
    self.total_supply -= _value
    self.balanceOf[_from] -= _value
    log.Transfer(_from, ZERO_ADDRESS, _value)


@public
def burn(_value: uint256):
    """
    @dev Burn an amount of the token of msg.sender.
    @param _value The amount that will be burned.
    """
    self._burn(msg.sender, _value)


@public
def burnFrom(_to: address, _value: uint256) -> bool:
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    self.allowances[_to][msg.sender] -= _value
    self._burn(_to, _value)
    return True


@public
def burnAsAuthorizedMinter(_to: address, _value: uint256) -> bool:
    """
    @dev Burn an amount of the token from a given account.
    @param _to The account whose tokens will be burned.
    @param _value The amount that will be burned.
    """
    assert msg.sender == self.minter
    self._burn(_to, _value)
    return True
