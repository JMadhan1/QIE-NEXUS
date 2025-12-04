"""
Users API Routes
Endpoints for user portfolio and data
"""

from flask import Blueprint, jsonify, request
import logging
from datetime import datetime, timedelta
import random

logger = logging.getLogger(__name__)

users_bp = Blueprint('users', __name__)
blockchain_service = None

def init_services(blockchain):
    global blockchain_service
    blockchain_service = blockchain

@users_bp.route('/portfolio/<address>', methods=['GET'])
def get_user_portfolio(address):
    """GET /api/portfolio/0x123... - Get comprehensive user portfolio"""
    try:
        # For now, return mock data since blockchain service might not be fully connected
        # In production, this would fetch real data from the blockchain
        
        # Generate mock positions
        positions = [
            {
                'marketId': 'MKT-001',
                'question': 'Will Bitcoin reach $100,000 by end of 2024?',
                'prediction': 'YES',
                'amount': 500,
                'potentialWin': 750,
                'status': 'active',
                'deadline': (datetime.now() + timedelta(days=30)).isoformat()
            },
            {
                'marketId': 'MKT-002',
                'question': 'Will Ethereum 2.0 launch successfully?',
                'prediction': 'YES',
                'amount': 750,
                'potentialWin': 1125,
                'status': 'active',
                'deadline': (datetime.now() + timedelta(days=15)).isoformat()
            },
            {
                'marketId': 'MKT-003',
                'question': 'Will AI surpass human intelligence in 2024?',
                'prediction': 'NO',
                'amount': 250,
                'potentialWin': 375,
                'status': 'active',
                'deadline': (datetime.now() + timedelta(days=60)).isoformat()
            }
        ]
        
        # Generate mock transactions
        transactions = [
            {
                'type': 'Stake Placed',
                'amount': -500,
                'timestamp': (datetime.now() - timedelta(days=5)).isoformat(),
                'hash': f'0x{random.randint(10**15, 10**16-1):016x}'
            },
            {
                'type': 'Stake Placed',
                'amount': -750,
                'timestamp': (datetime.now() - timedelta(days=3)).isoformat(),
                'hash': f'0x{random.randint(10**15, 10**16-1):016x}'
            },
            {
                'type': 'Rewards Claimed',
                'amount': 1200,
                'timestamp': (datetime.now() - timedelta(days=2)).isoformat(),
                'hash': f'0x{random.randint(10**15, 10**16-1):016x}'
            },
            {
                'type': 'Stake Placed',
                'amount': -250,
                'timestamp': (datetime.now() - timedelta(days=1)).isoformat(),
                'hash': f'0x{random.randint(10**15, 10**16-1):016x}'
            }
        ]
        
        # Calculate statistics
        total_staked = sum(p['amount'] for p in positions)
        total_won = 2250  # Mock value
        win_rate = 66.7  # Mock value
        active_positions = len(positions)
        
        return jsonify({
            'positions': positions,
            'transactions': transactions,
            'stats': {
                'activePositions': active_positions,
                'totalStaked': total_staked,
                'totalWon': total_won,
                'winRate': win_rate
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user portfolio: {e}")
        return jsonify({'error': str(e)}), 500

@users_bp.route('/user/<address>/portfolio', methods=['GET'])
def get_user_portfolio_legacy(address):
    """GET /api/user/0x123.../portfolio - Legacy endpoint (redirects to new endpoint)"""
    return get_user_portfolio(address)

@users_bp.route('/user/<address>/stats', methods=['GET'])
def get_user_stats(address):
    """GET /api/user/0x123.../stats - Get user statistics only"""
    try:
        # Mock statistics
        stats = {
            'activePositions': 3,
            'totalStaked': 1500,
            'totalWon': 2250,
            'winRate': 66.7,
            'totalTransactions': 12,
            'memberSince': (datetime.now() - timedelta(days=90)).isoformat()
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        return jsonify({'error': str(e)}), 500

@users_bp.route('/user/<address>/positions', methods=['GET'])
def get_user_positions(address):
    """GET /api/user/0x123.../positions - Get user's active positions"""
    try:
        # Mock positions
        positions = [
            {
                'marketId': 'MKT-001',
                'question': 'Will Bitcoin reach $100,000 by end of 2024?',
                'prediction': 'YES',
                'amount': 500,
                'potentialWin': 750,
                'status': 'active',
                'deadline': (datetime.now() + timedelta(days=30)).isoformat()
            }
        ]
        
        return jsonify(positions), 200
        
    except Exception as e:
        logger.error(f"Error fetching user positions: {e}")
        return jsonify({'error': str(e)}), 500

@users_bp.route('/user/<address>/transactions', methods=['GET'])
def get_user_transactions(address):
    """GET /api/user/0x123.../transactions - Get user's transaction history"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # Mock transactions
        all_transactions = [
            {
                'type': 'Stake Placed',
                'amount': -500,
                'timestamp': (datetime.now() - timedelta(days=i)).isoformat(),
                'hash': f'0x{random.randint(10**15, 10**16-1):016x}'
            }
            for i in range(1, 21)
        ]
        
        # Paginate
        start = (page - 1) * limit
        end = start + limit
        transactions = all_transactions[start:end]
        
        return jsonify({
            'transactions': transactions,
            'page': page,
            'limit': limit,
            'total': len(all_transactions)
        }), 200
        
    except Exception as e:
        logger.error(f"Error fetching user transactions: {e}")
        return jsonify({'error': str(e)}), 500

