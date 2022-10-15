import pytest
from scripts.utils import LOCAL_BLOCKCHAIN_ENVIRONMENTS
from brownie import network, chain, web3 as brownie_web3


@pytest.fixture(scope="function")
def local_test():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()
    else:
        chain.reset()


@pytest.fixture(scope="function")
def non_local_test():
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip()


@pytest.fixture()
def eth_amount_staked():
    return brownie_web3.toWei(1, "ether")


@pytest.fixture()
def dapp_amount_staked():
    """This is meant to represent 1000 units of the dapp token ($FARM)"""
    return brownie_web3.toWei(1000, "ether")
