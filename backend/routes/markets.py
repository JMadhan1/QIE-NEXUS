"""
Markets API Routes
Endpoints for prediction market operations
"""

from flask import Blueprint, jsonify, request
import logging
from services.blockchain import BlockchainService
from services.ai_inference import AIInferenceService
from services.oracle import OracleService

logger = logging.getLogger(__name__)

markets_bp = Blueprint('markets', __name__)

# Initialize services (will be injected from app.py)
blockchain_service = None
ai_service = None
oracle_service = None

def init_services(blockchain, ai, oracle):
    """Initialize services for this blueprint"""
    global blockchain_service, ai_service, oracle_service
    blockchain_service = blockchain
    ai_service = ai
    oracle_service = oracle

@markets_bp.route('/markets', methods=['GET'])
def get_markets():
    """
    GET /api/markets?category=forex&sort=volume&limit=20
    
    Returns: List of market objects
    """
    try:
        # Get query parameters
        category = request.args.get('category', 'all')
        sort_by = request.args.get('sort', 'volume')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        # Fetch markets from blockchain
        if not blockchain_service:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        markets = blockchain_service.get_active_markets()
        
        # Filter by category if specified
        if category != 'all':
            # This would filter based on oracle type in production
            pass
        
        # Sort markets
        if sort_by == 'volume':
            markets.sort(key=lambda x: x['totalStakeYes'] + x['totalStakeNo'], reverse=True)
        elif sort_by == 'time':
            markets.sort(key=lambda x: x['deadline'])
        elif sort_by == 'confidence':
            markets.sort(key=lambda x: x.get('aiConfidence', 50), reverse=True)
        
        # Paginate
        total = len(markets)
        markets = markets[offset:offset + limit]
        
        return jsonify({
            'markets': markets,
            'total': total,
            'limit': limit,
            'offset': offset
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching markets: {e}")
        return jsonify({'error': str(e)}), 500

@markets_bp.route('/markets/<int:market_id>', methods=['GET'])
def get_market_details(market_id):
    """
    GET /api/markets/123
    
    Returns: Complete market object with AI prediction and oracle data
    """
    try:
        if not blockchain_service:
            return jsonify({'error': 'Blockchain service not available'}), 503
        
        # Fetch market from smart contract
        market = blockchain_service.get_market(market_id)
        
        if not market:
            return jsonify({'error': 'Market not found'}), 404
        
        # Get AI prediction confidence
        if ai_service and oracle_service:
            oracle_prices = oracle_service.get_cached_prices()
            features = ai_service.prepare_features(oracle_prices, market)
            confidence = ai_service.predict(market_id, features)
            market['aiConfidence'] = confidence
        
        # Get oracle data
        if oracle_service:
            market['oraclePrices'] = oracle_service.get_cached_prices()
        
        # Calculate odds
        total_stake = market['totalStakeYes'] + market['totalStakeNo']
        if total_stake > 0:
            market['oddsYes'] = (market['totalStakeYes'] / total_stake) * 100
            market['oddsNo'] = (market['totalStakeNo'] / total_stake) * 100
        else:
            market['oddsYes'] = 50.0
            market['oddsNo'] = 50.0
        
        return jsonify(market), 200
        
    except Exception as e:
        logger.error(f"Error fetching market {market_id}: {e}")
        return jsonify({'error': str(e)}), 500

@markets_bp.route('/markets', methods=['POST'])
def create_market():
    """
    POST /api/markets
    Body: {question, deadline, oracle_address}
    
    Creates a new prediction market
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data or 'question' not in data:
            return jsonify({'error': 'Missing required field: question'}), 400
        
        if 'deadline' not in data:
            return jsonify({'error': 'Missing required field: deadline'}), 400
        
        if 'oracle_address' not in data:
            return jsonify({'error': 'Missing required field: oracle_address'}), 400
        
        # In production, this would call the smart contract
        # For now, return mock response
        return jsonify({
            'success': True,
            'message': 'Market creation requires wallet signature',
            'market_id': None,
            'tx_hash': None
        }), 200
        
    except Exception as e:
        logger.error(f"Error creating market: {e}")
        return jsonify({'error': str(e)}), 500

@markets_bp.route('/markets/<int:market_id>/stake', methods=['POST'])
def stake_on_market(market_id):
    """
    POST /api/markets/123/stake
    Body: {address, choice, amount, signature}
    
    Stake tokens on a prediction
    """
    try:
        data = request.get_json()
        
        # Validate input
        required_fields = ['address', 'choice', 'amount']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # In production, this would:
        # 1. Verify signature
        # 2. Call smart contract
        # 3. Wait for confirmation
        # 4. Emit WebSocket event
        
        return jsonify({
            'success': True,
            'message': 'Stake requires wallet signature',
            'tx_hash': None
        }), 200
        
    except Exception as e:
        logger.error(f"Error staking on market {market_id}: {e}")
        return jsonify({'error': str(e)}), 500

@markets_bp.route('/markets/<int:market_id>/activity', methods=['GET'])
def get_market_activity(market_id):
    """
    GET /api/markets/123/activity
    
    Returns: Recent activity for a market
    """
    try:
        # In production, this would fetch from blockchain events
        # For now, return mock data
        activity = [
            {
                'user': '0x1234...5678',
                'action': 'stake',
                'choice': 'YES',
                'amount': 100.0,
                'timestamp': 1640000000
            },
            {
                'user': '0x8765...4321',
                'action': 'stake',
                'choice': 'NO',
                'amount': 75.0,
                'timestamp': 1640000100
            }
        ]
        
        return jsonify({'activity': activity}), 200
        
    except Exception as e:
        logger.error(f"Error fetching activity for market {market_id}: {e}")
        return jsonify({'error': str(e)}), 500

@markets_bp.route('/markets/stats', methods=['GET'])
def get_platform_stats():
    """
    GET /api/markets/stats
    
    Returns: Platform-wide statistics
    """
    try:
        if not blockchain_service:
            # Return mock stats for development
            return jsonify({
                'totalValueLocked': 125000.0,
                'activeMarkets': 15,
                'totalPredictions': 1247,
                'averageWinRate': 68.5
            }), 200
        
        markets = blockchain_service.get_active_markets()
        
        # Calculate stats
        total_tvl = sum(m['totalStakeYes'] + m['totalStakeNo'] for m in markets)
        active_count = len(markets)
        
        return jsonify({
            'totalValueLocked': total_tvl,
            'activeMarkets': active_count,
            'totalPredictions': active_count * 50,  # Mock
            'averageWinRate': 68.5  # Mock
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching platform stats: {e}")
        return jsonify({'error': str(e)}), 500
