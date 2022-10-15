from brownie import DappToken, TokenFarm, web3 as brownie_web3

from scripts.utils import get_account, get_contract, get_publish_source

KEPT_BALANCE = brownie_web3.toWei(10_000, "ether")


def deploy_contracts():
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm_contract = TokenFarm.deploy(
        dapp_token.address,
        {"from": account},
        publish_source=get_publish_source(),
    )
    tx = dapp_token.transfer(
        token_farm_contract.address,
        # 1 M units - 10k units
        dapp_token.totalSupply() - KEPT_BALANCE,
        {"from": account},
    )
    tx.wait(1)
    weth_token = get_contract("weth_token")
    dai_token = get_contract("dai_token")  # FAU token will act as DAI
    link_token = get_contract("link_token")
    allowed_tokens_dict: dict = {
        dapp_token: get_contract("dai_usd_price_feed"),
        dai_token: get_contract("dai_usd_price_feed"),
        weth_token: get_contract("eth_usd_price_feed"),
        link_token: get_contract("link_usd_price_feed"),
    }
    add_allowed_tokens(token_farm_contract, allowed_tokens_dict, account)
    return token_farm_contract, dapp_token


def add_allowed_tokens(token_farm_contract, allowed_tokens_dict: dict, account):
    for token in allowed_tokens_dict:
        add_tx = token_farm_contract.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm_contract.setPriceFeedContract(
            token.address, allowed_tokens_dict[token], {"from": account}
        )
        set_tx.wait(1)
    return token_farm_contract


def main():
    deploy_contracts()
