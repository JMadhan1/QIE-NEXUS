"""
Blockchain Service
Handles all Web3 interactions with QIE Blockchain smart contracts
"""

from web3 import Web3
import json
import os
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BlockchainService:
    """Service for interacting with QIE Blockchain smart contracts"""
    
    def __init__(self):
        """Initialize Web3 connection and contract instances"""
        # Connect to QIE RPC
        rpc_url = os.getenv('QIE_RPC_URL', 'http://localhost:8545')
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))
        
        # Check connection
        if not self.w3.is_connected():
            logger.warning(f"Failed to connect to QIE RPC at {rpc_url}")
            # Use mock mode for development
            self.mock_mode = True
        else:
            logger.info(f"Connected to QIE Blockchain at {rpc_url}")
            self.mock_mode = False
        
        # Load contract ABIs
        self.contracts = self._load_contracts()
        
    def _load_contracts(self) -> Dict:
        """Load smart contract instances"""
        contracts = {}
        
        try:
            # Load ABIs from files (you'll need to add these after compilation)
            abi_dir = os.path.join(os.path.dirname(__file__), '..', 'contracts', 'abi')
            
            # PredictionCore
            prediction_core_address = os.getenv('PREDICTION_CORE_ADDRESS')
            if prediction_core_address and prediction_core_address != '0x0000000000000000000000000000000000000000':
                with open(os.path.join(abi_dir, 'PredictionCore.json'), 'r') as f:
                    abi = json.load(f)
                contracts['prediction_core'] = self.w3.eth.contract(
                    address=Web3.to_checksum_address(prediction_core_address),
                    abi=abi
                )
            
            # OracleAggregator
            oracle_address = os.getenv('ORACLE_AGGREGATOR_ADDRESS')
            if oracle_address and oracle_address != '0x0000000000000000000000000000000000000000':
                with open(os.path.join(abi_dir, 'OracleAggregator.json'), 'r') as f:
                    abi = json.load(f)
                contracts['oracle_aggregator'] = self.w3.eth.contract(
                    address=Web3.to_checksum_address(oracle_address),
                    abi=abi
                )
            
            # NeuralInference
            neural_address = os.getenv('NEURAL_INFERENCE_ADDRESS')
            if neural_address and neural_address != '0x0000000000000000000000000000000000000000':
                with open(os.path.join(abi_dir, 'NeuralInference.json'), 'r') as f:
                    abi = json.load(f)
                contracts['neural_inference'] = self.w3.eth.contract(
                    address=Web3.to_checksum_address(neural_address),
                    abi=abi
                )
            
            logger.info(f"Loaded {len(contracts)} contract instances")
            
        except Exception as e:
            logger.error(f"Error loading contracts: {e}")
        
        return contracts
    
    def get_market(self, market_id: int) -> Optional[Dict]:
        """
        Get market details from smart contract
        
        Args:
            market_id: Market identifier
            
        Returns:
            Market data dictionary or None
        """
        if self.mock_mode:
            return self._get_mock_market(market_id)
        
        try:
            contract = self.contracts.get('prediction_core')
            if not contract:
                return None
            
            market = contract.functions.getMarket(market_id).call()
            
            return {
                'id': market[0],
                'question': market[1],
                'deadline': market[2],
                'totalStakeYes': self.w3.from_wei(market[3], 'ether'),
                'totalStakeNo': self.w3.from_wei(market[4], 'ether'),
                'settled': market[5],
                'outcome': market[6],
                'oracleAddress': market[7],
                'creator': market[8],
                'createdAt': market[9],
                'aiConfidence': market[10]
            }
        except Exception as e:
            logger.error(f"Error fetching market {market_id}: {e}")
            return None
    
    def get_active_markets(self) -> List[Dict]:
        """
        Get all active markets
        
        Returns:
            List of active market dictionaries
        """
        if self.mock_mode:
            return self._get_mock_markets()
        
        try:
            contract = self.contracts.get('prediction_core')
            if not contract:
                return []
            
            # Get market counter
            market_count = contract.functions.marketCounter().call()
            
            markets = []
            for i in range(1, market_count + 1):
                market = self.get_market(i)
                if market and not market['settled']:
                    markets.append(market)
            
            return markets
        except Exception as e:
            logger.error(f"Error fetching active markets: {e}")
            return []
    
    def get_user_predictions(self, address: str) -> List[Dict]:
        """
        Get all predictions for a user
        
        Args:
            address: User wallet address
            
        Returns:
            List of prediction dictionaries
        """
        if self.mock_mode:
            return self._get_mock_predictions(address)
        
        try:
            contract = self.contracts.get('prediction_core')
            if not contract:
                return []
            
            # Get user's market IDs
            market_ids = contract.functions.getUserMarkets(
                Web3.to_checksum_address(address)
            ).call()
            
            predictions = []
            for market_id in market_ids:
                prediction = contract.functions.getPrediction(
                    market_id,
                    Web3.to_checksum_address(address)
                ).call()
                
                predictions.append({
                    'user': prediction[0],
                    'marketId': prediction[1],
                    'choice': prediction[2],
                    'amount': self.w3.from_wei(prediction[3], 'ether'),
                    'claimed': prediction[4],
                    'stakedAt': prediction[5]
                })
            
            return predictions
        except Exception as e:
            logger.error(f"Error fetching user predictions: {e}")
            return []
    
    def settle_expired_markets(self) -> List[int]:
        """
        Settle all expired markets
        
        Returns:
            List of settled market IDs
        """
        if self.mock_mode:
            return []
        
        try:
            # This would typically be called by an oracle or admin
            # For now, just return empty list
            return []
        except Exception as e:
            logger.error(f"Error settling markets: {e}")
            return []
    
    def update_ai_confidence(self, market_id: int, confidence: int) -> bool:
        """
        Update AI confidence on-chain
        
        Args:
            market_id: Market ID
            confidence: Confidence score (0-100)
            
        Returns:
            Success boolean
        """
        if self.mock_mode:
            logger.info(f"[MOCK] Updated on-chain confidence for market {market_id} to {confidence}%")
            return True

        try:
            contract = self.contracts.get('prediction_core')
            private_key = os.getenv('OWNER_PRIVATE_KEY')
            
            if not contract or not private_key:
                logger.warning("Cannot update on-chain confidence: Missing contract or private key")
                return False
                
            account = self.w3.eth.account.from_key(private_key)
            
            # Build transaction
            tx = contract.functions.updateAIConfidence(
                market_id,
                confidence
            ).build_transaction({
                'from': account.address,
                'nonce': self.w3.eth.get_transaction_count(account.address),
                'gas': 200000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # Sign and send
            signed_tx = self.w3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            logger.info(f"Updated AI confidence on-chain. Tx: {self.w3.to_hex(tx_hash)}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating on-chain confidence: {e}")
            return False

    def listen_to_events(self, event_name: str, callback):
        """
        Listen to smart contract events
        
        Args:
            event_name: Name of the event to listen to
            callback: Function to call when event is emitted
        """
        if self.mock_mode:
            return
        
        try:
            contract = self.contracts.get('prediction_core')
            if not contract:
                return
            
            event_filter = contract.events[event_name].create_filter(fromBlock='latest')
            
            while True:
                for event in event_filter.get_new_entries():
                    callback(event)
        except Exception as e:
            logger.error(f"Error listening to events: {e}")
    
    # ============ Mock Data for Development ============
    
    def _get_mock_market(self, market_id: int) -> Dict:
        """Return mock market data for development"""
        import time
        return {
            'id': market_id,
            'question': f'Will BTC price be above $50,000 by end of week?',
            'deadline': int(time.time()) + 86400 * 7,  # 7 days from now
            'totalStakeYes': 1500.0,
            'totalStakeNo': 1200.0,
            'settled': False,
            'outcome': False,
            'oracleAddress': '0x1234567890123456789012345678901234567890',
            'creator': '0x0987654321098765432109876543210987654321',
            'createdAt': int(time.time()) - 86400,  # 1 day ago
            'aiConfidence': 78
        }
    
    def _get_mock_markets(self) -> List[Dict]:
        """Return mock markets for development"""
        import time
        return [
            {
                'id': 1,
                'question': 'Will BTC price be above $50,000 by end of week?',
                'deadline': int(time.time()) + 86400 * 7,
                'totalStakeYes': 1500.0,
                'totalStakeNo': 1200.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x1234567890123456789012345678901234567890',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400,
                'aiConfidence': 78
            },
            {
                'id': 2,
                'question': 'Will ETH reach $3,000 this month?',
                'deadline': int(time.time()) + 86400 * 14,
                'totalStakeYes': 2300.0,
                'totalStakeNo': 1800.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x2345678901234567890123456789012345678901',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400 * 2,
                'aiConfidence': 65
            },
            {
                'id': 3,
                'question': 'Will Gold price exceed $2,100/oz next week?',
                'deadline': int(time.time()) + 86400 * 5,
                'totalStakeYes': 980.0,
                'totalStakeNo': 1450.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x3456789012345678901234567890123456789012',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400 * 3,
                'aiConfidence': 52
            },
            {
                'id': 4,
                'question': 'Will SOL price double in the next 30 days?',
                'deadline': int(time.time()) + 86400 * 30,
                'totalStakeYes': 750.0,
                'totalStakeNo': 2100.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x4567890123456789012345678901234567890123',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400,
                'aiConfidence': 35
            },
            {
                'id': 5,
                'question': 'Will USD/EUR exchange rate stay above 0.90?',
                'deadline': int(time.time()) + 86400 * 10,
                'totalStakeYes': 1650.0,
                'totalStakeNo': 1320.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x5678901234567890123456789012345678901234',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400 * 4,
                'aiConfidence': 82
            },
            {
                'id': 6,
                'question': 'Will Oil prices drop below $70/barrel this quarter?',
                'deadline': int(time.time()) + 86400 * 60,
                'totalStakeYes': 1100.0,
                'totalStakeNo': 1900.0,
                'settled': False,
                'outcome': False,
                'oracleAddress': '0x6789012345678901234567890123456789012345',
                'creator': '0x0987654321098765432109876543210987654321',
                'createdAt': int(time.time()) - 86400 * 5,
                'aiConfidence': 48
            }
        ]
    
    def _get_mock_predictions(self, address: str) -> List[Dict]:
        """Return mock predictions for development"""
        import time
        return [
            {
                'user': address,
                'marketId': 1,
                'choice': True,
                'amount': 100.0,
                'claimed': False,
                'stakedAt': int(time.time()) - 3600
            }
        ]
