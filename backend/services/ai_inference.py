"""
AI Inference Service
Handles AI model loading and inference for predictions
"""

import numpy as np
import logging
from typing import Dict, List, Optional
import os

logger = logging.getLogger(__name__)

class AIInferenceService:
    """Service for AI model inference"""
    
    def __init__(self):
        """Initialize AI inference service"""
        self.model = None
        self.model_path = os.getenv('AI_MODEL_PATH', './ml/model.onnx')
        self.model_loaded = False
        
        # Try to load ONNX model
        try:
            import onnxruntime as ort
            if os.path.exists(self.model_path):
                self.session = ort.InferenceSession(self.model_path)
                self.model_loaded = True
                logger.info(f"ONNX model loaded from {self.model_path}")
            else:
                logger.warning(f"Model file not found at {self.model_path}, using fallback")
                self.session = None
        except ImportError:
            logger.warning("ONNX Runtime not installed, using fallback predictions")
            self.session = None
        except Exception as e:
            logger.error(f"Error loading ONNX model: {e}")
            self.session = None
        
        # Cache for predictions
        self.prediction_cache = {}
    
    def predict(self, market_id: int, features: Optional[List[float]] = None) -> int:
        """
        Run AI inference for a market
        
        Args:
            market_id: Market identifier
            features: Optional input features (oracle prices + indicators)
            
        Returns:
            Confidence score (0-100)
        """
        # Check cache
        if market_id in self.prediction_cache:
            return self.prediction_cache[market_id]
        
        try:
            if self.model_loaded and self.session and features:
                # Run ONNX inference
                confidence = self._run_onnx_inference(features)
            else:
                # Use fallback prediction
                confidence = self._fallback_prediction(market_id, features)
            
            # Cache result
            self.prediction_cache[market_id] = confidence
            
            logger.info(f"Prediction for market {market_id}: {confidence}% confidence")
            return confidence
            
        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return 50  # Neutral prediction on error
    
    def _run_onnx_inference(self, features: List[float]) -> int:
        """
        Run ONNX model inference
        
        Args:
            features: Input feature array
            
        Returns:
            Confidence score (0-100)
        """
        try:
            # Prepare input
            input_name = self.session.get_inputs()[0].name
            input_data = np.array([features], dtype=np.float32)
            
            # Run inference
            result = self.session.run(None, {input_name: input_data})
            
            # Convert output to confidence (0-100)
            # Assuming output is a probability (0-1)
            confidence = int(result[0][0] * 100)
            
            # Clamp to valid range
            return max(0, min(100, confidence))
            
        except Exception as e:
            logger.error(f"ONNX inference error: {e}")
            return 50
    
    def _fallback_prediction(self, market_id: int, features: Optional[List[float]] = None) -> int:
        """
        Fallback prediction using simple heuristics
        
        Args:
            market_id: Market identifier
            features: Optional features
            
        Returns:
            Confidence score (0-100)
        """
        # Simple heuristic: use market ID and features to generate pseudo-random but consistent prediction
        import hashlib
        
        # Create deterministic seed from market ID
        seed = int(hashlib.md5(str(market_id).encode()).hexdigest()[:8], 16)
        np.random.seed(seed % (2**32))
        
        if features and len(features) > 0:
            # Use features to influence prediction
            feature_sum = sum(features)
            base_confidence = 50 + (feature_sum % 30) - 15  # Range: 35-65
            
            # Add some noise
            noise = np.random.normal(0, 10)
            confidence = int(base_confidence + noise)
        else:
            # Random confidence between 40-80
            confidence = int(np.random.uniform(40, 80))
        
        # Clamp to valid range
        return max(5, min(95, confidence))
    
    def prepare_features(self, oracle_prices: Dict, market_data: Dict) -> List[float]:
        """
        Prepare input features for the model
        
        Args:
            oracle_prices: Dictionary of oracle prices
            market_data: Market metadata
            
        Returns:
            Feature array (21 features: 7 oracles + 14 indicators)
        """
        features = []
        
        # Extract oracle prices (7 features)
        oracle_values = []
        for category in ['forex', 'commodities', 'crypto']:
            for key, value in oracle_prices.get(category, {}).items():
                if isinstance(value, (int, float)):
                    oracle_values.append(float(value))
        
        # Pad or truncate to 7 values
        oracle_values = (oracle_values + [0.0] * 7)[:7]
        features.extend(oracle_values)
        
        # Calculate technical indicators (14 features)
        # For simplicity, using derived features from oracle prices
        if len(oracle_values) >= 7:
            # Moving average
            features.append(sum(oracle_values) / len(oracle_values))
            
            # Momentum
            features.append(oracle_values[0] - oracle_values[-1])
            
            # Volatility (std dev)
            mean = sum(oracle_values) / len(oracle_values)
            variance = sum((x - mean) ** 2 for x in oracle_values) / len(oracle_values)
            features.append(variance ** 0.5)
            
            # Additional derived features
            features.extend([
                max(oracle_values),
                min(oracle_values),
                oracle_values[0],  # Latest price
                oracle_values[-1],  # Oldest price
                sum(1 for i in range(len(oracle_values)-1) if oracle_values[i] > oracle_values[i+1]),  # Up days
                sum(1 for i in range(len(oracle_values)-1) if oracle_values[i] < oracle_values[i+1]),  # Down days
                oracle_values[0] / oracle_values[-1] if oracle_values[-1] != 0 else 1.0,  # Price ratio
                (max(oracle_values) - min(oracle_values)) / max(oracle_values) if max(oracle_values) != 0 else 0.0,  # Range
                # Pad remaining
                0.0, 0.0, 0.0
            ])
        else:
            # Pad with zeros if insufficient data
            features.extend([0.0] * 14)
        
        # Ensure exactly 21 features
        return features[:21]
    
    def update_model(self, model_path: str) -> bool:
        """
        Update the AI model
        
        Args:
            model_path: Path to new model file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            import onnxruntime as ort
            
            # Load new model
            new_session = ort.InferenceSession(model_path)
            
            # If successful, replace old model
            self.session = new_session
            self.model_path = model_path
            self.model_loaded = True
            
            # Clear cache
            self.prediction_cache.clear()
            
            logger.info(f"Model updated successfully from {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating model: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """
        Get information about the current model
        
        Returns:
            Dictionary with model metadata
        """
        return {
            'loaded': self.model_loaded,
            'path': self.model_path,
            'type': 'ONNX' if self.model_loaded else 'Fallback',
            'cache_size': len(self.prediction_cache)
        }
