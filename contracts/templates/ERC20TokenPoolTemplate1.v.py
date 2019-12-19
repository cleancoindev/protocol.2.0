# Vyper version of the Lendroid protocol v2
# THIS CONTRACT HAS NOT BEEN AUDITED!


from contracts.interfaces import ERC20


owner: public(address)
token: public(address)

initialized: public(bool)


@public
def initialize(_token: address) -> bool:
    assert not self.initialized
    self.initialized = True
    self.owner = msg.sender
    self.token = _token

    return True


@public
@constant
def borrowable_amount() -> uint256:
    return ERC20(self.token).balanceOf(self)


@public
def release(_to: address, _value: uint256) -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(ERC20(self.token).transfer(_to, _value))

    return True


@public
def destroy() -> bool:
    assert self.initialized
    assert msg.sender == self.owner
    assert_modifiable(ERC20(self.token).transfer(
        self.owner,
        ERC20(self.token).balanceOf(self)
    ))
    selfdestruct(self.owner)
