// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title OracleAggregator
 * @dev Aggregates data from multiple QIE oracles with consensus mechanism
 * @notice Fetches and validates data from 7 live oracles (forex, commodities, crypto)
 */
contract OracleAggregator is Ownable {
    
    // ============ Structs ============
    
    struct OracleData {
        uint256 price;
        uint256 timestamp;
        bool isValid;
    }
    
    struct Oracle {
        address oracleAddress;
        string name;
        string category; // "forex", "commodities", "crypto"
        bool isActive;
        uint256 weight; // For weighted average (basis points)
        uint256 lastUpdate;
    }
    
    // ============ State Variables ============
    
    mapping(bytes32 => Oracle) public oracles;
    mapping(bytes32 => mapping(address => OracleData)) public oracleData;
    mapping(bytes32 => uint256) public consensusPrice;
    
    bytes32[] public oracleIds;
    
    uint256 public constant OUTLIER_THRESHOLD = 2000; // 20% deviation
    uint256 public constant STALENESS_THRESHOLD = 300; // 5 minutes
    uint256 public constant WEIGHT_DENOMINATOR = 10000;
    
    // ============ Events ============
    
    event OracleRegistered(
        bytes32 indexed oracleId,
        address indexed oracleAddress,
        string name,
        string category
    );
    
    event OracleDataUpdated(
        bytes32 indexed oracleId,
        address indexed oracleAddress,
        uint256 price,
        uint256 timestamp
    );
    
    event ConsensusPriceCalculated(
        bytes32 indexed oracleId,
        uint256 price,
        uint256 validOracleCount,
        uint256 timestamp
    );
    
    event OracleDeactivated(bytes32 indexed oracleId);
    
    // ============ Constructor ============
    
    constructor() {
        // Initialize with QIE's 7 oracles
        _registerDefaultOracles();
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Register a new oracle
     * @param _name Oracle name (e.g., "BTC/USD")
     * @param _category Category (forex/commodities/crypto)
     * @param _oracleAddress Oracle contract address
     * @param _weight Weight for consensus (basis points)
     */
    function registerOracle(
        string memory _name,
        string memory _category,
        address _oracleAddress,
        uint256 _weight
    ) external onlyOwner {
        require(_oracleAddress != address(0), "Invalid oracle address");
        require(_weight <= WEIGHT_DENOMINATOR, "Invalid weight");
        
        bytes32 oracleId = keccak256(abi.encodePacked(_name, _category));
        
        oracles[oracleId] = Oracle({
            oracleAddress: _oracleAddress,
            name: _name,
            category: _category,
            isActive: true,
            weight: _weight,
            lastUpdate: 0
        });
        
        oracleIds.push(oracleId);
        
        emit OracleRegistered(oracleId, _oracleAddress, _name, _category);
    }
    
    /**
     * @notice Update oracle data (called by oracle contracts)
     * @param _oracleId Oracle identifier
     * @param _price Current price
     */
    function updateOracleData(
        bytes32 _oracleId,
        uint256 _price
    ) external {
        Oracle storage oracle = oracles[_oracleId];
        
        require(oracle.isActive, "Oracle not active");
        require(msg.sender == oracle.oracleAddress || msg.sender == owner(), "Not authorized");
        require(_price > 0, "Invalid price");
        
        oracleData[_oracleId][msg.sender] = OracleData({
            price: _price,
            timestamp: block.timestamp,
            isValid: true
        });
        
        oracle.lastUpdate = block.timestamp;
        
        emit OracleDataUpdated(_oracleId, msg.sender, _price, block.timestamp);
    }
    
    /**
     * @notice Calculate consensus price from multiple oracles
     * @param _oracleId Oracle identifier
     * @return price Consensus price
     */
    function calculateConsensusPrice(bytes32 _oracleId) public returns (uint256) {
        Oracle memory oracle = oracles[_oracleId];
        require(oracle.isActive, "Oracle not active");
        
        // Get all oracle prices
        uint256[] memory prices = new uint256[](oracleIds.length);
        uint256[] memory weights = new uint256[](oracleIds.length);
        uint256 validCount = 0;
        
        for (uint256 i = 0; i < oracleIds.length; i++) {
            bytes32 id = oracleIds[i];
            Oracle memory orc = oracles[id];
            OracleData memory data = oracleData[id][orc.oracleAddress];
            
            // Check if data is fresh and valid
            if (
                data.isValid &&
                block.timestamp - data.timestamp <= STALENESS_THRESHOLD &&
                data.price > 0
            ) {
                prices[validCount] = data.price;
                weights[validCount] = orc.weight;
                validCount++;
            }
        }
        
        require(validCount > 0, "No valid oracle data");
        
        // Filter outliers
        uint256[] memory filteredPrices = new uint256[](validCount);
        uint256[] memory filteredWeights = new uint256[](validCount);
        uint256 filteredCount = 0;
        
        // Calculate median for outlier detection
        uint256 median = _calculateMedian(prices, validCount);
        
        for (uint256 i = 0; i < validCount; i++) {
            uint256 deviation = prices[i] > median
                ? ((prices[i] - median) * 10000) / median
                : ((median - prices[i]) * 10000) / median;
            
            // Include if within threshold
            if (deviation <= OUTLIER_THRESHOLD) {
                filteredPrices[filteredCount] = prices[i];
                filteredWeights[filteredCount] = weights[i];
                filteredCount++;
            }
        }
        
        require(filteredCount > 0, "All oracles are outliers");
        
        // Calculate weighted average
        uint256 weightedSum = 0;
        uint256 totalWeight = 0;
        
        for (uint256 i = 0; i < filteredCount; i++) {
            weightedSum += filteredPrices[i] * filteredWeights[i];
            totalWeight += filteredWeights[i];
        }
        
        uint256 consensusValue = weightedSum / totalWeight;
        consensusPrice[_oracleId] = consensusValue;
        
        emit ConsensusPriceCalculated(_oracleId, consensusValue, filteredCount, block.timestamp);
        
        return consensusValue;
    }
    
    /**
     * @notice Get latest consensus price
     * @param _oracleId Oracle identifier
     * @return price Latest consensus price
     */
    function getConsensusPrice(bytes32 _oracleId) external view returns (uint256) {
        return consensusPrice[_oracleId];
    }
    
    /**
     * @notice Get oracle data
     * @param _oracleId Oracle identifier
     * @return Oracle struct
     */
    function getOracle(bytes32 _oracleId) external view returns (Oracle memory) {
        return oracles[_oracleId];
    }
    
    /**
     * @notice Get all active oracles
     * @return Array of oracle IDs
     */
    function getActiveOracles() external view returns (bytes32[] memory) {
        uint256 activeCount = 0;
        
        // Count active oracles
        for (uint256 i = 0; i < oracleIds.length; i++) {
            if (oracles[oracleIds[i]].isActive) {
                activeCount++;
            }
        }
        
        // Build array
        bytes32[] memory activeOracles = new bytes32[](activeCount);
        uint256 index = 0;
        
        for (uint256 i = 0; i < oracleIds.length; i++) {
            if (oracles[oracleIds[i]].isActive) {
                activeOracles[index] = oracleIds[i];
                index++;
            }
        }
        
        return activeOracles;
    }
    
    /**
     * @notice Check if oracle data is fresh
     * @param _oracleId Oracle identifier
     * @return isFresh Whether data is within staleness threshold
     */
    function isDataFresh(bytes32 _oracleId) external view returns (bool) {
        Oracle memory oracle = oracles[_oracleId];
        return block.timestamp - oracle.lastUpdate <= STALENESS_THRESHOLD;
    }
    
    // ============ Internal Functions ============
    
    /**
     * @notice Calculate median of array
     * @param _array Array of values
     * @param _length Length of valid data
     * @return median Median value
     */
    function _calculateMedian(
        uint256[] memory _array,
        uint256 _length
    ) internal pure returns (uint256) {
        if (_length == 0) return 0;
        if (_length == 1) return _array[0];
        
        // Simple bubble sort for small arrays
        for (uint256 i = 0; i < _length - 1; i++) {
            for (uint256 j = 0; j < _length - i - 1; j++) {
                if (_array[j] > _array[j + 1]) {
                    uint256 temp = _array[j];
                    _array[j] = _array[j + 1];
                    _array[j + 1] = temp;
                }
            }
        }
        
        if (_length % 2 == 0) {
            return (_array[_length / 2 - 1] + _array[_length / 2]) / 2;
        } else {
            return _array[_length / 2];
        }
    }
    
    /**
     * @notice Register default QIE oracles
     */
    function _registerDefaultOracles() internal {
        // Forex Oracles
        _registerOracleInternal("USD/EUR", "forex", address(0x1), 1500);
        _registerOracleInternal("JPY/GBP", "forex", address(0x2), 1500);
        
        // Commodities Oracles
        _registerOracleInternal("GOLD", "commodities", address(0x3), 1500);
        _registerOracleInternal("OIL", "commodities", address(0x4), 1500);
        
        // Crypto Oracles
        _registerOracleInternal("BTC/USD", "crypto", address(0x5), 1500);
        _registerOracleInternal("ETH/USD", "crypto", address(0x6), 1500);
        _registerOracleInternal("SOL/USD", "crypto", address(0x7), 1000);
    }
    
    function _registerOracleInternal(
        string memory _name,
        string memory _category,
        address _oracleAddress,
        uint256 _weight
    ) internal {
        bytes32 oracleId = keccak256(abi.encodePacked(_name, _category));
        
        oracles[oracleId] = Oracle({
            oracleAddress: _oracleAddress,
            name: _name,
            category: _category,
            isActive: true,
            weight: _weight,
            lastUpdate: 0
        });
        
        oracleIds.push(oracleId);
    }
    
    // ============ Admin Functions ============
    
    /**
     * @notice Deactivate an oracle
     * @param _oracleId Oracle identifier
     */
    function deactivateOracle(bytes32 _oracleId) external onlyOwner {
        oracles[_oracleId].isActive = false;
        emit OracleDeactivated(_oracleId);
    }
    
    /**
     * @notice Update oracle weight
     * @param _oracleId Oracle identifier
     * @param _newWeight New weight (basis points)
     */
    function updateOracleWeight(bytes32 _oracleId, uint256 _newWeight) external onlyOwner {
        require(_newWeight <= WEIGHT_DENOMINATOR, "Invalid weight");
        oracles[_oracleId].weight = _newWeight;
    }
}
