from scripts.utils import get_account, get_contract, DAPP_INITIAL_PRICE, DECIMALS
from scripts.deploy_contracts import deploy_contracts
import pytest
from brownie import exceptions


def test_set_price_feed_contract(local_test):
    # Arrange
    owner_acc = account = get_account()
    non_owner_acc = get_account(index=1)
    token_farm_contract, dapp_token = deploy_contracts()
    # Act
    token_farm_contract.setPriceFeedContract(
        dapp_token.address, get_contract("dai_usd_price_feed"), {"from": owner_acc}
    )
    # Assert
    assert token_farm_contract.s_tokenPriceFeed(dapp_token.address) == get_contract(
        "dai_usd_price_feed"
    )
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm_contract.setPriceFeedContract(
            dapp_token.address,
            get_contract("dai_usd_price_feed"),
            {"from": non_owner_acc},
        )


def test_add_allowable_tokens(local_test):
    # Arrange
    owner_acc = account = get_account()
    non_owner_acc = get_account(index=1)
    token_farm_contract, dapp_token = deploy_contracts()
    # Act
    token_farm_contract.addAllowedTokens(dapp_token.address, {"from": owner_acc})
    # Assert
    assert token_farm_contract.s_allowedTokens(0) == dapp_token.address
    with pytest.raises(exceptions.VirtualMachineError):
        token_farm_contract.s_allowedTokens(
            dapp_token.address,
            {"from": non_owner_acc},
        )
    return token_farm_contract, dapp_token


def test_stake_tokens(local_test, dapp_amount_staked):
    # Arrange
    owner_acc = account = get_account()
    token_farm_contract, dapp_token = deploy_contracts()
    # Act
    dapp_token.approve(
        token_farm_contract.address, dapp_amount_staked, {"from": account}
    )
    ## dapp_amount_staked = 1000 units = (1000, "ether")
    token_farm_contract.stakeTokens(
        dapp_amount_staked, dapp_token.address, {"from": account}
    )
    # Assert
    assert (
        # Solidity syntax: token_farm_contract.s_stakingBalancePerUserPerToken[account][dapp_token.address]
        # Brownie syntax:
        token_farm_contract.s_stakingBalancePerUserPerToken(
            account.address, dapp_token.address
        )
        == dapp_amount_staked
    )
    assert token_farm_contract.s_stakers(0) == account.address
    return token_farm_contract, dapp_token


def test_getusertvl(local_test, dapp_amount_staked):
    # Arrange
    owner_acc = account = get_account()
    token_farm_contract, dapp_token = test_stake_tokens(local_test, dapp_amount_staked)
    # Act
    total_val: int = token_farm_contract.getUserTVL(account.address, {"from": account})
    # Assert
    assert total_val == dapp_amount_staked


def test_unstake_tokens(local_test, dapp_amount_staked):
    # Arrange
    owner_acc = account = get_account()
    token_farm_contract, dapp_token = test_stake_tokens(local_test, dapp_amount_staked)
    # Act
    tx = token_farm_contract.unstakeTokens(dapp_token.address, {"from": account})
    # Assert
    assert tx.events["UnstakeTokens"]["quantity"] == dapp_amount_staked
    assert (
        token_farm_contract.s_stakingBalancePerUserPerToken(
            account.address, dapp_token.address
        )
        == 0
    )


def test_issue_tokens(local_test, dapp_amount_staked):
    # Arrange
    owner_acc = account = get_account()
    token_farm_contract, dapp_token = test_stake_tokens(local_test, dapp_amount_staked)
    starting_bal = dapp_token.balanceOf(account.address)
    print(starting_bal)
    # Act
    token_farm_contract.issueRewardTokens({"from": account})

    # Assert
    # TVL = 1000, rewards = 10% * 1000 = 100
    # balance = 9000 + 100 = 9100
    assert dapp_token.balanceOf(account.address) == starting_bal + (
        (dapp_amount_staked * DAPP_INITIAL_PRICE / (10**DECIMALS)) / 10
    )


def test_token_is_allowed(local_test):
    # Arrange
    owner_acc = account = get_account()
    random_address = get_account(index=1).address
    # Add dapp token to allow list
    token_farm_contract, dapp_token = test_add_allowable_tokens(local_test)
    # Act
    is_allowed: bool = token_farm_contract.tokenIsAllowed(
        random_address, {"from": account}
    )
    # Assert
    assert is_allowed == False
