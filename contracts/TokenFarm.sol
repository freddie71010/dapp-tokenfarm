// stake tokens
// unstake tokens
// issue tokens
// add allowed tokens
// get ETH value to get underlining value of staked tokens

pragma solidity ^0.8.17;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink-brownie-contracts/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

contract TokenFarm is Ownable {
    address[] public s_allowedTokens;
    // mapping(address => mapping(address => uint256)) public s_stakingBalancePerTokenPerUser;
    mapping(address => mapping(address => uint256)) public s_stakingBalancePerUserPerToken;
    mapping(address => address) public s_tokenPriceFeed;
    address[] public s_stakers;
    
    IERC20 public immutable i_dappToken;
    
    event AddedNewAllowedToken(address token);
    event StakeTokens(address user, address token, uint256 quantity);
    event UnstakeTokens(address user, address token, uint256 quantity);
    event IssueRewardTokens(address user, uint256 quantity);
    
    constructor(address _dappTokenAddress) {
        i_dappToken = IERC20(_dappTokenAddress);

    }
    
    function stakeTokens(uint256 _amount, address _token) public {
        require(_amount > 0, "Amount must be > 0");
        require(tokenIsAllowed(_token), "Token is not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        // s_stakingBalancePerTokenPerUser[_token][msg.sender] += _amount;
        s_stakingBalancePerUserPerToken[msg.sender][_token] += _amount;
        
        s_stakers.push(msg.sender);
        emit StakeTokens(msg.sender, _token, _amount);
    }

    function unstakeTokens(address _token) public {
        uint256 balance = s_stakingBalancePerUserPerToken[msg.sender][_token];
        require(balance > 0, "Staking balance cannot be 0");
        IERC20(_token).transfer(msg.sender, balance);
        s_stakingBalancePerUserPerToken[msg.sender][_token] = 0;

        emit UnstakeTokens(msg.sender, _token, balance);
    }

    function tokenIsAllowed(address _token) public view returns (bool) {
        for(uint256 i=0; i < s_allowedTokens.length; i++) {
            if (s_allowedTokens[i] == _token) {
                return true;
            }
        }
        return false;
    }

    function addAllowedTokens(address _token) public onlyOwner {
        s_allowedTokens.push(_token);
        emit AddedNewAllowedToken(_token);
    }

    function setPriceFeedContract(address _token, address _priceFeed) external onlyOwner {
        s_tokenPriceFeed[_token] = _priceFeed;
    }

    function issueRewardTokens() public onlyOwner {
        for (uint256 i=0; i < s_stakers.length; i++) {
            address recipient = s_stakers[i];
            // send them token reward based on their TVL
            uint256 userTVL = getUserTVL(recipient);
            uint256 rewardAmt = userTVL / 10; // User receives 10% of TVL in reward tokens
            // uint256 rewardAmt = calculateRewardAmt(userTVL);
            i_dappToken.transfer(recipient, rewardAmt);
            emit IssueRewardTokens(recipient, rewardAmt);
        }
    }

    // function calculateRewardAmt(uint256 _userTVL) internal {
    //     // perform calculation to determine reward distribution
    // }

    function getUserTVL(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        for (uint8 token=0; token < s_allowedTokens.length; token++){
            address tokenAddress = s_allowedTokens[token];
            (uint256 price, uint256 decimals) = getTokenUSDPrice(tokenAddress);
            uint256 tokenQuantity = s_stakingBalancePerUserPerToken[_user][tokenAddress];
            totalValue += tokenQuantity * (price / (10**decimals));
        }
        return totalValue;
    }

    function getTokenUSDPrice(address _token) public view returns (uint256, uint256) {
        address priceFeedAddress = s_tokenPriceFeed[_token];
        AggregatorV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (,int price,,,) = priceFeed.latestRoundData();
        uint8 decimals = priceFeed.decimals();
        return (uint256(price), uint256(decimals));
    }

    function updateUniqueTokensStaked(address _user, address _token) internal onlyOwner {

    }
}