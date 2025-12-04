"""
Oracles API Routes
Endpoints for oracle price data
"""

from flask import Blueprint, jsonify, request
import logging
from services.oracle import OracleService

logger = logging.getLogger(__name__)

oracles_bp = Blueprint('oracles', __name__)
oracle_service = None

def init_services(oracle):
    global oracle_service
    oracle_service = oracle

@oracles_bp.route('/oracles/prices', methods=['GET'])
def get_oracle_prices():
    """GET /api/oracles/prices - Get all oracle prices"""
    try:
        if not oracle_service:
            return jsonify({'error': 'Oracle service not available'}), 503
        
        prices = oracle_service.get_cached_prices()
        return jsonify(prices), 200
    except Exception as e:
        logger.error(f"Error fetching oracle prices: {e}")
        return jsonify({'error': str(e)}), 500

@oracles_bp.route('/oracles/history', methods=['GET'])
def get_price_history():
    """GET /api/oracles/history?oracle=BTC&timeframe=24h"""
    try:
        oracle_name = request.args.get('oracle', 'BTC')
        timeframe = request.args.get('timeframe', '24h')
        
        if not oracle_service:
            return jsonify({'error': 'Oracle service not available'}), 503
        
        history = oracle_service.get_price_history(oracle_name, timeframe)
        return jsonify({'oracle': oracle_name, 'timeframe': timeframe, 'data': history}), 200
    except Exception as e:
        logger.error(f"Error fetching price history: {e}")
        return jsonify({'error': str(e)}), 500
