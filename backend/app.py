"""
QIE Nexus - Flask Backend Application
Main entry point for the API server
"""

# Monkey patch for eventlet - MUST be first
import eventlet
eventlet.monkey_patch()

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv()

# Initialize Flask app
# Serve static files from the frontend folder
app = Flask(__name__, static_folder='../frontend', static_url_path='')
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'neural-oracle-secret-key-2025')
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import services
from services.blockchain import BlockchainService
from services.oracle import OracleService
from services.ai_inference import AIInferenceService
from services.ipfs import IPFSService

# Initialize services
try:
    blockchain_service = BlockchainService()
    oracle_service = OracleService()
    ai_service = AIInferenceService()
    ipfs_service = IPFSService()
    logger.info("All services initialized successfully")
except Exception as e:
    logger.error(f"Error initializing services: {e}")
    blockchain_service = None
    oracle_service = None
    ai_service = None
    ipfs_service = None

# Import routes
from routes.markets import markets_bp
from routes.oracles import oracles_bp
from routes.predictions import predictions_bp
from routes.users import users_bp

# Register blueprints
app.register_blueprint(markets_bp, url_prefix='/api')
app.register_blueprint(oracles_bp, url_prefix='/api')
app.register_blueprint(predictions_bp, url_prefix='/api')
app.register_blueprint(users_bp, url_prefix='/api')

# Inject services into routes
from routes import markets, oracles, predictions, users
markets.blockchain_service = blockchain_service
markets.ai_service = ai_service
markets.oracle_service = oracle_service
oracles.oracle_service = oracle_service
predictions.ai_service = ai_service
predictions.oracle_service = oracle_service
predictions.blockchain_service = blockchain_service
users.blockchain_service = blockchain_service

# ============ Background Tasks ============

def update_oracle_prices():
    """Update oracle prices every 30 seconds"""
    try:
        if oracle_service:
            prices = oracle_service.fetch_all_prices()
            # Emit to all connected clients
            socketio.emit('oracle_update', prices, namespace='/')
            logger.info(f"Oracle prices updated: {len(prices)} feeds")
    except Exception as e:
        logger.error(f"Error updating oracle prices: {e}")

def settle_expired_markets():
    """Check and settle expired markets every 5 minutes"""
    try:
        if blockchain_service:
            settled = blockchain_service.settle_expired_markets()
            if settled:
                logger.info(f"Settled {len(settled)} expired markets")
                socketio.emit('markets_settled', settled, namespace='/')
    except Exception as e:
        logger.error(f"Error settling markets: {e}")

def update_ai_predictions():
    """Update AI predictions for active markets every 2 minutes"""
    try:
        if ai_service and blockchain_service:
            active_markets = blockchain_service.get_active_markets()
            for market in active_markets:
                confidence = ai_service.predict(market['id'])
                socketio.emit('ai_update', {
                    'market_id': market['id'],
                    'confidence': confidence
                }, namespace='/')
    except Exception as e:
        logger.error(f"Error updating AI predictions: {e}")

# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(update_oracle_prices, 'interval', seconds=30)
scheduler.add_job(settle_expired_markets, 'interval', minutes=5)
scheduler.add_job(update_ai_predictions, 'interval', minutes=2)
scheduler.start()

# ============ WebSocket Events ============

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info(f"Client connected: {request.sid}")
    
    # Send initial data
    try:
        if oracle_service:
            prices = oracle_service.get_cached_prices()
            emit('oracle_update', prices)
        
        if blockchain_service:
            markets = blockchain_service.get_active_markets()
            emit('markets_update', markets)
    except Exception as e:
        logger.error(f"Error sending initial data: {e}")

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('subscribe_market')
def handle_subscribe_market(data):
    """Subscribe to specific market updates"""
    market_id = data.get('market_id')
    logger.info(f"Client {request.sid} subscribed to market {market_id}")
    # Join room for market-specific updates
    from flask_socketio import join_room
    join_room(f"market_{market_id}")

@socketio.on('unsubscribe_market')
def handle_unsubscribe_market(data):
    """Unsubscribe from market updates"""
    market_id = data.get('market_id')
    logger.info(f"Client {request.sid} unsubscribed from market {market_id}")
    from flask_socketio import leave_room
    leave_room(f"market_{market_id}")

# ============ Health Check ============

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'blockchain': blockchain_service is not None,
            'oracle': oracle_service is not None,
            'ai': ai_service is not None,
            'ipfs': ipfs_service is not None
        }
    }), 200

@app.route('/api/info', methods=['GET'])
def api_info():
    """API Info endpoint"""
    return jsonify({
        'name': 'QIE Nexus API',
        'version': '1.0.0',
        'description': 'AI-Powered Prediction Market on QIE Blockchain',
        'endpoints': {
            'markets': '/api/markets',
            'oracles': '/api/oracles/prices',
            'predictions': '/api/ai/predict/:market_id',
            'users': '/api/user/:address/portfolio'
        }
    }), 200

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

# ============ Error Handlers ============

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal error: {error}")
    return jsonify({'error': 'Internal server error'}), 500

# ============ Main ============

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'True') == 'True'
    
    logger.info(f"Starting QIE Nexus API on http://127.0.0.1:{port}")
    logger.info(f"Debug mode: {debug}")
    
    # Run with SocketIO
    socketio.run(
        app,
        host='127.0.0.1',
        port=port,
        debug=debug,
        use_reloader=debug
    )
