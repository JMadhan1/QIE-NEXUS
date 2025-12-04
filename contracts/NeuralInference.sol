// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/**
 * @title NeuralInference
 * @dev On-chain AI inference engine using quantized neural networks
 * @notice Executes lightweight AI models for prediction confidence scores
 */
contract NeuralInference is Ownable {
    
    // ============ Structs ============
    
    struct ModelMetadata {
        string ipfsHash;
        uint256 version;
        uint256 uploadedAt;
        address uploader;
        bool isActive;
        uint256 inferenceCount;
        uint256 totalGasUsed;
    }
    
    struct InferenceResult {
        uint8 confidence; // 0-100
        uint256 timestamp;
        bytes32 modelHash;
        uint256 gasUsed;
    }
    
    // Simplified quantized weights (INT8 representation)
    struct QuantizedWeights {
        int8[] weights;
        int8[] biases;
        uint8 scale; // Scaling factor for dequantization
    }
    
    // ============ State Variables ============
    
    mapping(bytes32 => ModelMetadata) public models;
    mapping(uint256 => InferenceResult) public marketInferences;
    mapping(bytes32 => QuantizedWeights) public modelWeights;
    
    bytes32 public activeModelHash;
    uint256 public modelVersion;
    
    uint256 public constant MAX_INFERENCE_GAS = 500000; // 500k gas limit
    uint256 public constant FEATURE_COUNT = 21; // 7 oracles + 14 indicators
    
    // ============ Events ============
    
    event ModelUploaded(
        bytes32 indexed modelHash,
        string ipfsHash,
        uint256 version,
        address indexed uploader
    );
    
    event ModelActivated(
        bytes32 indexed modelHash,
        uint256 version
    );
    
    event InferenceExecuted(
        uint256 indexed marketId,
        uint8 confidence,
        bytes32 indexed modelHash,
        uint256 gasUsed
    );
    
    // ============ Constructor ============
    
    constructor() {
        // Initialize with default model
        _initializeDefaultModel();
    }
    
    // ============ Core Functions ============
    
    /**
     * @notice Upload a new AI model
     * @param _ipfsHash IPFS hash of the model file
     * @param _weights Quantized model weights
     * @param _biases Quantized model biases
     * @param _scale Scaling factor
     */
    function uploadModel(
        string memory _ipfsHash,
        int8[] memory _weights,
        int8[] memory _biases,
        uint8 _scale
    ) external onlyOwner {
        require(bytes(_ipfsHash).length > 0, "Invalid IPFS hash");
        require(_weights.length > 0, "Invalid weights");
        
        modelVersion++;
        bytes32 modelHash = keccak256(abi.encodePacked(_ipfsHash, modelVersion));
        
        models[modelHash] = ModelMetadata({
            ipfsHash: _ipfsHash,
            version: modelVersion,
            uploadedAt: block.timestamp,
            uploader: msg.sender,
            isActive: false,
            inferenceCount: 0,
            totalGasUsed: 0
        });
        
        modelWeights[modelHash] = QuantizedWeights({
            weights: _weights,
            biases: _biases,
            scale: _scale
        });
        
        emit ModelUploaded(modelHash, _ipfsHash, modelVersion, msg.sender);
    }
    
    /**
     * @notice Activate a model for inference
     * @param _modelHash Hash of the model to activate
     */
    function activateModel(bytes32 _modelHash) external onlyOwner {
        require(models[_modelHash].version > 0, "Model does not exist");
        
        // Deactivate previous model
        if (activeModelHash != bytes32(0)) {
            models[activeModelHash].isActive = false;
        }
        
        models[_modelHash].isActive = true;
        activeModelHash = _modelHash;
        
        emit ModelActivated(_modelHash, models[_modelHash].version);
    }
    
    /**
     * @notice Execute AI inference for a market
     * @param _marketId Market identifier
     * @param _features Input features (oracle prices + indicators)
     * @return confidence Prediction confidence (0-100)
     */
    function executeInference(
        uint256 _marketId,
        int256[FEATURE_COUNT] memory _features
    ) external returns (uint8) {
        uint256 gasStart = gasleft();
        
        require(activeModelHash != bytes32(0), "No active model");
        require(gasStart >= MAX_INFERENCE_GAS, "Insufficient gas");
        
        ModelMetadata storage model = models[activeModelHash];
        QuantizedWeights storage weights = modelWeights[activeModelHash];
        
        // Simplified neural network inference
        // Layer 1: Input -> Hidden (simplified LSTM)
        int256 hiddenSum = 0;
        
        for (uint256 i = 0; i < FEATURE_COUNT && i < weights.weights.length; i++) {
            hiddenSum += _features[i] * int256(int8(weights.weights[i]));
        }
        
        // Add bias
        if (weights.biases.length > 0) {
            hiddenSum += int256(int8(weights.biases[0])) * 1000;
        }
        
        // ReLU activation (simplified)
        if (hiddenSum < 0) {
            hiddenSum = 0;
        }
        
        // Layer 2: Hidden -> Output (sigmoid approximation)
        // Map to 0-100 range
        uint8 confidence = _sigmoid(hiddenSum, weights.scale);
        
        // Record inference
        uint256 gasUsed = gasStart - gasleft();
        
        marketInferences[_marketId] = InferenceResult({
            confidence: confidence,
            timestamp: block.timestamp,
            modelHash: activeModelHash,
            gasUsed: gasUsed
        });
        
        model.inferenceCount++;
        model.totalGasUsed += gasUsed;
        
        emit InferenceExecuted(_marketId, confidence, activeModelHash, gasUsed);
        
        return confidence;
    }
    
    /**
     * @notice Get inference result for a market
     * @param _marketId Market identifier
     * @return InferenceResult struct
     */
    function getInference(uint256 _marketId) external view returns (InferenceResult memory) {
        return marketInferences[_marketId];
    }
    
    /**
     * @notice Get active model metadata
     * @return ModelMetadata struct
     */
    function getActiveModel() external view returns (ModelMetadata memory) {
        return models[activeModelHash];
    }
    
    /**
     * @notice Get model performance metrics
     * @param _modelHash Model identifier
     * @return avgGasPerInference Average gas per inference
     * @return totalInferences Total number of inferences
     */
    function getModelMetrics(bytes32 _modelHash) external view returns (
        uint256 avgGasPerInference,
        uint256 totalInferences
    ) {
        ModelMetadata memory model = models[_modelHash];
        
        if (model.inferenceCount == 0) {
            return (0, 0);
        }
        
        avgGasPerInference = model.totalGasUsed / model.inferenceCount;
        totalInferences = model.inferenceCount;
    }
    
    // ============ Internal Functions ============
    
    /**
     * @notice Sigmoid activation function (approximation)
     * @param _x Input value
     * @param _scale Scaling factor
     * @return output Value between 0-100
     */
    function _sigmoid(int256 _x, uint8 _scale) internal pure returns (uint8) {
        // Simplified sigmoid: 1 / (1 + e^(-x))
        // Approximation for on-chain efficiency
        
        int256 scaled = _x / int256(uint256(_scale));
        
        // Clamp to reasonable range
        if (scaled > 500) return 95;
        if (scaled < -500) return 5;
        
        // Linear approximation in middle range
        if (scaled >= 0) {
            uint256 output = 50 + uint256(scaled) / 10;
            return output > 95 ? 95 : uint8(output);
        } else {
            uint256 output = 50 - uint256(-scaled) / 10;
            return output < 5 ? 5 : uint8(output);
        }
    }
    
    /**
     * @notice Initialize default model
     */
    function _initializeDefaultModel() internal {
        // Create a simple default model
        int8[] memory defaultWeights = new int8[](FEATURE_COUNT);
        int8[] memory defaultBiases = new int8[](1);
        
        // Initialize with small random-like values
        for (uint256 i = 0; i < FEATURE_COUNT; i++) {
            defaultWeights[i] = int8(int256((i * 7 + 3) % 20 - 10));
        }
        defaultBiases[0] = 0;
        
        modelVersion = 1;
        bytes32 modelHash = keccak256(abi.encodePacked("default", modelVersion));
        
        models[modelHash] = ModelMetadata({
            ipfsHash: "QmDefaultModel",
            version: 1,
            uploadedAt: block.timestamp,
            uploader: msg.sender,
            isActive: true,
            inferenceCount: 0,
            totalGasUsed: 0
        });
        
        modelWeights[modelHash] = QuantizedWeights({
            weights: defaultWeights,
            biases: defaultBiases,
            scale: 10
        });
        
        activeModelHash = modelHash;
    }
    
    // ============ Helper Functions ============
    
    /**
     * @notice Calculate technical indicators from price data
     * @param _prices Array of recent prices
     * @return indicators Array of calculated indicators
     */
    function calculateIndicators(
        uint256[] memory _prices
    ) external pure returns (int256[14] memory indicators) {
        require(_prices.length >= 14, "Insufficient price data");
        
        // Simple Moving Average (SMA)
        uint256 sma = 0;
        for (uint256 i = 0; i < 7; i++) {
            sma += _prices[i];
        }
        indicators[0] = int256(sma / 7);
        
        // Price momentum
        indicators[1] = int256(_prices[0]) - int256(_prices[6]);
        
        // Volatility (simplified standard deviation)
        int256 mean = indicators[0];
        uint256 variance = 0;
        for (uint256 i = 0; i < 7; i++) {
            int256 diff = int256(_prices[i]) - mean;
            variance += uint256(diff * diff);
        }
        indicators[2] = int256(variance / 7);
        
        // Additional indicators (simplified)
        for (uint256 i = 3; i < 14; i++) {
            indicators[i] = int256(_prices[i % _prices.length]);
        }
        
        return indicators;
    }
}
