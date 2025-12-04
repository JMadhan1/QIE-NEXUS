"""
Predictions API Routes
Endpoints for AI predictions
"""

from flask import Blueprint, jsonify, request
import logging
from services.ai_inference import AIInferenceService
from services.oracle import OracleService
from services.blockchain import BlockchainService

logger = logging.getLogger(__name__)

predictions_bp = Blueprint('predictions', __name__)
ai_service = None
oracle_service = None
blockchain_service = None

def init_services(ai, oracle, blockchain):
    global ai_service, oracle_service, blockchain_service
    ai_service = ai
    oracle_service = oracle
    blockchain_service = blockchain

@predictions_bp.route('/ai/predict/<int:market_id>', methods=['GET'])
def get_ai_prediction(market_id):
    """GET /api/ai/predict/123 - Get AI prediction for market"""
    try:
        if not ai_service or not oracle_service:
            return jsonify({'error': 'AI service not available'}), 503
        
        # Get oracle prices
        oracle_prices = oracle_service.get_cached_prices()
        
        # Get market data
        market_data = blockchain_service.get_market(market_id) if blockchain_service else {}
        
        # Prepare features
        features = ai_service.prepare_features(oracle_prices, market_data)
        
        # Run inference
        confidence = ai_service.predict(market_id, features)
        
        return jsonify({
            'confidence': confidence,
            'reasoning': f'Based on {len(features)} features from 7 oracles',
            'last_updated': oracle_prices.get('timestamp')
        }), 200
    except Exception as e:
        logger.error(f"Error getting AI prediction: {e}")
        return jsonify({'error': str(e)}), 500

@predictions_bp.route('/ai/model/info', methods=['GET'])
def get_model_info():
    """GET /api/ai/model/info - Get model information"""
    try:
        if not ai_service:
            return jsonify({'error': 'AI service not available'}), 503
        
        info = ai_service.get_model_info()
        return jsonify(info), 200
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({'error': str(e)}), 500
