// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

/**
 * @title PredictionCore
 * @dev Main orchestrator contract for Neural Oracle prediction markets
 * @notice Handles market creation, staking, settlement, and reward distribution
 */
contract PredictionCore is ReentrancyGuard, Ownable {
    
    // ============ State Variables ============
    
    IERC20 public qieToken;
    uint256 public marketCounter;
    uint256 public constant MIN_STAKE = 1 ether; // 1 QIE minimum
    uint256 public constant PLATFORM_FEE = 200; // 2% (basis points)
    uint256 public constant FEE_DENOMINATOR = 10000;
    
    // ============ Structs ============
    
    struct Market {
        uint256 id;
        string question;
        uint256 deadline;
        uint256 totalStakeYes;
        uint256 totalStakeNo;
        bool settled;
        bool outcome; // true = YES, false = NO
        address oracleAddress;
        address creator;
        uint256 createdAt;
        uint8 aiConfidence; // 0-100
    }
    
    struct Prediction {
        address user;
        uint256 marketId;
        bool choice; // true = YES, false = NO
        uint256 amount;
        bool claimed;
        uint256 stakedAt;
    }
    
    // ============ Mappings ============
    
    mapping(uint256 => Market) public markets;
    mapping(uint256 => mapping(address => Prediction)) public predictions;
    mapping(uint256 => address[]) public marketParticipants;
    mapping(address => uint256[]) public userMarkets;
    
    // ============ Events ============
    
    event MarketCreated(
        uint256 indexed marketId,
        string question,
        uint256 deadline,
        address indexed creator,
        address oracleAddress
    );
    
    event PredictionStaked(
        address indexed user,
        uint256 indexed marketId,
        bool choice,
        uint256 amount,
        uint256 timestamp
    );
    
    event MarketSettled(
        uint256 indexed marketId,
        bool outcome,
        uint256 totalStakeYes,
        uint256 totalStakeNo,
        uint256 timestamp
    );
    
    event RewardsClaimed(
        address indexed user,
        uint256 indexed marketId,
        uint256 amount,
        uint256 timestamp
    );
    
    event AIConfidenceUpdated(
        uint256 indexed marketId,
        uint8 confidence
    );
    
    // ============ Constructor ============
    
    constructor(address _qieToken) {
        require(_qieToken != address(0), "Invalid token address");
        qieToken = IERC20(_qieToken);
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Create a new prediction market
     * @param _question The market question
     * @param _deadline Unix timestamp for market expiry
     * @param _oracleAddress Address of the oracle for settlement
     * @return marketId The ID of the created market
     */
    function createMarket(
        string memory _question,
        uint256 _deadline,
        address _oracleAddress
    ) external returns (uint256) {
        require(_deadline > block.timestamp, "Deadline must be in future");
        require(_oracleAddress != address(0), "Invalid oracle address");
        require(bytes(_question).length > 0, "Question cannot be empty");
        
        marketCounter++;
        uint256 marketId = marketCounter;
        
        markets[marketId] = Market({
            id: marketId,
            question: _question,
            deadline: _deadline,
            totalStakeYes: 0,
            totalStakeNo: 0,
            settled: false,
            outcome: false,
            oracleAddress: _oracleAddress,
            creator: msg.sender,
            createdAt: block.timestamp,
            aiConfidence: 50 // Default neutral
        });
        
        emit MarketCreated(marketId, _question, _deadline, msg.sender, _oracleAddress);
        
        return marketId;
    }
    
    /**
     * @notice Stake tokens on a prediction
     * @param _marketId The market ID
     * @param _choice true for YES, false for NO
     * @param _amount Amount of QIE tokens to stake
     */
    function stakePrediction(
        uint256 _marketId,
        bool _choice,
        uint256 _amount
    ) external nonReentrant {
        Market storage market = markets[_marketId];
        
        require(market.id != 0, "Market does not exist");
        require(!market.settled, "Market already settled");
        require(block.timestamp < market.deadline, "Market expired");
        require(_amount >= MIN_STAKE, "Stake below minimum");
        require(predictions[_marketId][msg.sender].amount == 0, "Already staked");
        
        // Transfer tokens from user
        require(
            qieToken.transferFrom(msg.sender, address(this), _amount),
            "Token transfer failed"
        );
        
        // Record prediction
        predictions[_marketId][msg.sender] = Prediction({
            user: msg.sender,
            marketId: _marketId,
            choice: _choice,
            amount: _amount,
            claimed: false,
            stakedAt: block.timestamp
        });
        
        // Update market totals
        if (_choice) {
            market.totalStakeYes += _amount;
        } else {
            market.totalStakeNo += _amount;
        }
        
        // Track participants
        marketParticipants[_marketId].push(msg.sender);
        userMarkets[msg.sender].push(_marketId);
        
        emit PredictionStaked(msg.sender, _marketId, _choice, _amount, block.timestamp);
    }
    
    /**
     * @notice Settle a market (only oracle or owner)
     * @param _marketId The market ID
     * @param _outcome true for YES, false for NO
     */
    function settleMarket(
        uint256 _marketId,
        bool _outcome
    ) external {
        Market storage market = markets[_marketId];
        
        require(market.id != 0, "Market does not exist");
        require(!market.settled, "Market already settled");
        require(block.timestamp >= market.deadline, "Market not expired");
        require(
            msg.sender == market.oracleAddress || msg.sender == owner(),
            "Not authorized"
        );
        
        market.settled = true;
        market.outcome = _outcome;
        
        emit MarketSettled(
            _marketId,
            _outcome,
            market.totalStakeYes,
            market.totalStakeNo,
            block.timestamp
        );
    }
    
    /**
     * @notice Claim rewards for a winning prediction
     * @param _marketId The market ID
     * @return reward The amount of rewards claimed
     */
    function claimRewards(uint256 _marketId) external nonReentrant returns (uint256) {
        Market storage market = markets[_marketId];
        Prediction storage prediction = predictions[_marketId][msg.sender];
        
        require(market.settled, "Market not settled");
        require(prediction.amount > 0, "No stake found");
        require(!prediction.claimed, "Already claimed");
        require(prediction.choice == market.outcome, "Prediction lost");
        
        prediction.claimed = true;
        
        // Calculate reward
        uint256 totalWinningStake = market.outcome ? market.totalStakeYes : market.totalStakeNo;
        uint256 totalLosingStake = market.outcome ? market.totalStakeNo : market.totalStakeYes;
        
        uint256 userShare = (prediction.amount * 1e18) / totalWinningStake;
        uint256 losingPool = totalLosingStake;
        
        // Deduct platform fee
        uint256 platformFee = (losingPool * PLATFORM_FEE) / FEE_DENOMINATOR;
        uint256 rewardPool = losingPool - platformFee;
        
        uint256 userReward = (rewardPool * userShare) / 1e18;
        uint256 totalPayout = prediction.amount + userReward;
        
        // Transfer rewards
        require(
            qieToken.transfer(msg.sender, totalPayout),
            "Reward transfer failed"
        );
        
        emit RewardsClaimed(msg.sender, _marketId, totalPayout, block.timestamp);
        
        return totalPayout;
    }
    
    /**
     * @notice Update AI confidence for a market
     * @param _marketId The market ID
     * @param _confidence Confidence score (0-100)
     */
    function updateAIConfidence(
        uint256 _marketId,
        uint8 _confidence
    ) external onlyOwner {
        require(_confidence <= 100, "Invalid confidence");
        require(markets[_marketId].id != 0, "Market does not exist");
        require(!markets[_marketId].settled, "Market already settled");
        
        markets[_marketId].aiConfidence = _confidence;
        
        emit AIConfidenceUpdated(_marketId, _confidence);
    }
    
    // ============ View Functions ============
    
    /**
     * @notice Get market details
     * @param _marketId The market ID
     * @return Market struct
     */
    function getMarket(uint256 _marketId) external view returns (Market memory) {
        return markets[_marketId];
    }
    
    /**
     * @notice Get user's prediction for a market
     * @param _marketId The market ID
     * @param _user User address
     * @return Prediction struct
     */
    function getPrediction(
        uint256 _marketId,
        address _user
    ) external view returns (Prediction memory) {
        return predictions[_marketId][_user];
    }
    
    /**
     * @notice Get all markets a user has participated in
     * @param _user User address
     * @return Array of market IDs
     */
    function getUserMarkets(address _user) external view returns (uint256[] memory) {
        return userMarkets[_user];
    }
    
    /**
     * @notice Get all participants in a market
     * @param _marketId The market ID
     * @return Array of participant addresses
     */
    function getMarketParticipants(uint256 _marketId) external view returns (address[] memory) {
        return marketParticipants[_marketId];
    }
    
    /**
     * @notice Calculate potential reward for a user
     * @param _marketId The market ID
     * @param _user User address
     * @return potentialReward The estimated reward if user wins
     */
    function calculatePotentialReward(
        uint256 _marketId,
        address _user
    ) external view returns (uint256) {
        Market memory market = markets[_marketId];
        Prediction memory prediction = predictions[_marketId][_user];
        
        if (prediction.amount == 0) return 0;
        
        uint256 totalWinningStake = prediction.choice ? market.totalStakeYes : market.totalStakeNo;
        uint256 totalLosingStake = prediction.choice ? market.totalStakeNo : market.totalStakeYes;
        
        if (totalWinningStake == 0) return 0;
        
        uint256 userShare = (prediction.amount * 1e18) / totalWinningStake;
        uint256 platformFee = (totalLosingStake * PLATFORM_FEE) / FEE_DENOMINATOR;
        uint256 rewardPool = totalLosingStake - platformFee;
        uint256 userReward = (rewardPool * userShare) / 1e18;
        
        return prediction.amount + userReward;
    }
    
    /**
     * @notice Get current odds for a market
     * @param _marketId The market ID
     * @return yesOdds Odds for YES (basis points)
     * @return noOdds Odds for NO (basis points)
     */
    function getOdds(uint256 _marketId) external view returns (uint256 yesOdds, uint256 noOdds) {
        Market memory market = markets[_marketId];
        uint256 totalStake = market.totalStakeYes + market.totalStakeNo;
        
        if (totalStake == 0) {
            return (5000, 5000); // 50/50 if no stakes
        }
        
        yesOdds = (market.totalStakeYes * 10000) / totalStake;
        noOdds = (market.totalStakeNo * 10000) / totalStake;
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Withdraw platform fees
     * @param _amount Amount to withdraw
     */
    function withdrawFees(uint256 _amount) external onlyOwner {
        require(
            qieToken.transfer(owner(), _amount),
            "Fee withdrawal failed"
        );
    }
    
    /**
     * @notice Emergency pause (if needed)
     */
    function pause() external onlyOwner {
        // Implement pause logic if needed
    }
}
