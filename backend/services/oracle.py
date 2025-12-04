"""
Oracle Service
Fetches and aggregates data from QIE's 7 live oracles
"""

import requests
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

logger = logging.getLogger(__name__)

class OracleService:
    """Service for fetching and aggregating oracle data"""
    
    def __init__(self):
        """Initialize oracle service with cache"""
        self.cache = {}
        self.cache_ttl = int(os.getenv('ORACLE_CACHE_TTL', 60))  # 60 seconds
        self.last_update = {}
        
        # Oracle endpoints (these would be real QIE oracle addresses)
        self.oracles = {
            'forex': {
                'USD_EUR': 'https://api.qie.digital/oracle/forex/usd-eur',
                'JPY_GBP': 'https://api.qie.digital/oracle/forex/jpy-gbp'
            },
            'commodities': {
                'GOLD': 'https://api.qie.digital/oracle/commodities/gold',
                'OIL': 'https://api.qie.digital/oracle/commodities/oil'
            },
            'crypto': {
                'BTC': 'https://api.qie.digital/oracle/crypto/btc',
                'ETH': 'https://api.qie.digital/oracle/crypto/eth',
                'SOL': 'https://api.qie.digital/oracle/crypto/sol'
            }
        }
        
        # Fallback to public APIs for development
        self.use_fallback = True
        
        logger.info("Oracle service initialized")
    
    def fetch_all_prices(self) -> Dict:
        """
        Fetch prices from all 7 oracles
        
        Returns:
            Dictionary with oracle prices by category
        """
        prices = {
            'forex': {},
            'commodities': {},
            'crypto': {},
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Fetch forex prices
            prices['forex']['USD_EUR'] = self._fetch_forex_price('USD', 'EUR')
            prices['forex']['JPY_GBP'] = self._fetch_forex_price('JPY', 'GBP')
            
            # Fetch commodity prices
            prices['commodities']['GOLD'] = self._fetch_commodity_price('GOLD')
            prices['commodities']['OIL'] = self._fetch_commodity_price('OIL')
            
            # Fetch crypto prices
            prices['crypto']['BTC'] = self._fetch_crypto_price('bitcoin')
            prices['crypto']['ETH'] = self._fetch_crypto_price('ethereum')
            prices['crypto']['SOL'] = self._fetch_crypto_price('solana')
            
            # Update cache
            self.cache = prices
            self.last_update = datetime.now()
            
            logger.info("Successfully fetched all oracle prices")
            
        except Exception as e:
            logger.error(f"Error fetching oracle prices: {e}")
            # Return cached data if available
            if self.cache:
                return self.cache
        
        return prices
    
    def get_cached_prices(self) -> Dict:
        """
        Get cached oracle prices
        
        Returns:
            Cached price dictionary
        """
        # Check if cache is stale
        if self.last_update:
            age = (datetime.now() - self.last_update).total_seconds()
            if age > self.cache_ttl:
                # Refresh cache
                return self.fetch_all_prices()
        
        return self.cache if self.cache else self.fetch_all_prices()
    
    def get_consensus_price(self, oracle_name: str) -> Optional[float]:
        """
        Get consensus price for a specific oracle
        
        Args:
            oracle_name: Name of the oracle (e.g., 'BTC', 'GOLD')
            
        Returns:
            Consensus price or None
        """
        prices = self.get_cached_prices()
        
        # Search in all categories
        for category in ['forex', 'commodities', 'crypto']:
            if oracle_name in prices.get(category, {}):
                return prices[category][oracle_name]
        
        return None
    
    def get_price_history(self, oracle_name: str, timeframe: str = '24h') -> List[Dict]:
        """
        Get historical price data for an oracle
        
        Args:
            oracle_name: Name of the oracle
            timeframe: Time period ('1h', '24h', '7d', '30d')
            
        Returns:
            List of {timestamp, price} dictionaries
        """
        # For development, return mock data
        # In production, this would query a database or time-series store
        return self._get_mock_history(oracle_name, timeframe)
    
    # ============ Private Methods ============
    
    def _fetch_forex_price(self, base: str, quote: str) -> float:
        """Fetch forex price from API"""
        if self.use_fallback:
            # Use exchangerate-api.com for development
            try:
                url = f"https://api.exchangerate-api.com/v4/latest/{base}"
                response = requests.get(url, timeout=5)
                data = response.json()
                return data['rates'].get(quote, 0.0)
            except Exception as e:
                logger.error(f"Error fetching forex {base}/{quote}: {e}")
                return self._get_mock_price(f"{base}_{quote}")
        
        return self._get_mock_price(f"{base}_{quote}")
    
    def _fetch_commodity_price(self, commodity: str) -> float:
        """Fetch commodity price from API"""
        if self.use_fallback:
            # Mock commodity prices for development
            mock_prices = {
                'GOLD': 2045.30,
                'OIL': 73.50
            }
            return mock_prices.get(commodity, 0.0)
        
        return self._get_mock_price(commodity)
    
    def _fetch_crypto_price(self, crypto_id: str) -> float:
        """Fetch crypto price from CoinGecko API"""
        if self.use_fallback:
            try:
                url = f"https://api.coingecko.com/api/v3/simple/price"
                params = {
                    'ids': crypto_id,
                    'vs_currencies': 'usd'
                }
                response = requests.get(url, params=params, timeout=5)
                data = response.json()
                return data.get(crypto_id, {}).get('usd', 0.0)
            except Exception as e:
                logger.error(f"Error fetching crypto {crypto_id}: {e}")
                return self._get_mock_price(crypto_id)
        
        return self._get_mock_price(crypto_id)
    
    def _get_mock_price(self, asset: str) -> float:
        """Return mock price for development"""
        mock_prices = {
            'USD_EUR': 0.92,
            'JPY_GBP': 0.0056,
            'GOLD': 2045.30,
            'OIL': 73.50,
            'bitcoin': 43250.00,
            'ethereum': 2280.50,
            'solana': 98.75
        }
        return mock_prices.get(asset, 100.0)
    
    def _get_mock_history(self, oracle_name: str, timeframe: str) -> List[Dict]:
        """Generate mock historical data"""
        import random
        from datetime import datetime, timedelta
        
        # Determine number of data points based on timeframe
        points_map = {
            '1h': 60,    # 1 point per minute
            '24h': 288,  # 1 point per 5 minutes
            '7d': 168,   # 1 point per hour
            '30d': 720   # 1 point per hour
        }
        
        num_points = points_map.get(timeframe, 100)
        base_price = self.get_consensus_price(oracle_name) or 100.0
        
        history = []
        now = datetime.now()
        
        for i in range(num_points):
            # Calculate timestamp
            if timeframe == '1h':
                timestamp = now - timedelta(minutes=num_points - i)
            elif timeframe == '24h':
                timestamp = now - timedelta(minutes=(num_points - i) * 5)
            else:
                timestamp = now - timedelta(hours=num_points - i)
            
            # Generate price with random walk
            variation = random.uniform(-0.02, 0.02)  # ±2% variation
            price = base_price * (1 + variation)
            
            history.append({
                'timestamp': int(timestamp.timestamp()),
                'price': round(price, 2)
            })
        
        return history
    
    def calculate_technical_indicators(self, prices: List[float]) -> Dict:
        """
        Calculate technical indicators from price data
        
        Args:
            prices: List of recent prices
            
        Returns:
            Dictionary of technical indicators
        """
        if len(prices) < 14:
            return {}
        
        indicators = {}
        
        # Simple Moving Average (SMA)
        sma_7 = sum(prices[:7]) / 7
        sma_14 = sum(prices[:14]) / 14
        indicators['sma_7'] = sma_7
        indicators['sma_14'] = sma_14
        
        # Price Momentum
        indicators['momentum'] = prices[0] - prices[6]
        
        # Volatility (simplified standard deviation)
        mean = sum(prices[:7]) / 7
        variance = sum((p - mean) ** 2 for p in prices[:7]) / 7
        indicators['volatility'] = variance ** 0.5
        
        # Trend (positive if upward, negative if downward)
        indicators['trend'] = 1 if prices[0] > prices[6] else -1
        
        return indicators
