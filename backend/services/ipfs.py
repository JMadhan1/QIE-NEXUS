"""
IPFS Service
Handles IPFS integration for storing and retrieving AI models
"""

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class IPFSService:
    """Service for IPFS operations"""
    
    def __init__(self):
        """Initialize IPFS service"""
        self.ipfs_api_url = os.getenv('IPFS_API_URL', 'https://ipfs.infura.io:5001')
        self.ipfs_gateway = os.getenv('IPFS_GATEWAY_URL', 'https://ipfs.io/ipfs/')
        self.project_id = os.getenv('IPFS_PROJECT_ID')
        self.project_secret = os.getenv('IPFS_PROJECT_SECRET')
        
        self.client = None
        self.connected = False
        
        # Try to connect to IPFS
        try:
            import ipfshttpclient
            
            if self.project_id and self.project_secret:
                # Use Infura with authentication
                auth = (self.project_id, self.project_secret)
                self.client = ipfshttpclient.connect(
                    self.ipfs_api_url,
                    auth=auth
                )
            else:
                # Try local IPFS node
                self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
            
            self.connected = True
            logger.info("Connected to IPFS")
            
        except ImportError:
            logger.warning("ipfshttpclient not installed, IPFS features disabled")
        except Exception as e:
            logger.warning(f"Could not connect to IPFS: {e}")
    
    def upload_model(self, model_path: str) -> Optional[str]:
        """
        Upload AI model to IPFS
        
        Args:
            model_path: Path to model file
            
        Returns:
            IPFS hash or None
        """
        if not self.connected or not self.client:
            logger.error("IPFS not connected")
            return None
        
        try:
            # Add file to IPFS
            result = self.client.add(model_path)
            ipfs_hash = result['Hash']
            
            # Pin the file
            self.client.pin.add(ipfs_hash)
            
            logger.info(f"Model uploaded to IPFS: {ipfs_hash}")
            return ipfs_hash
            
        except Exception as e:
            logger.error(f"Error uploading to IPFS: {e}")
            return None
    
    def download_model(self, ipfs_hash: str, output_path: str) -> bool:
        """
        Download AI model from IPFS
        
        Args:
            ipfs_hash: IPFS hash of the model
            output_path: Path to save the model
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected or not self.client:
            # Try downloading via HTTP gateway
            return self._download_via_gateway(ipfs_hash, output_path)
        
        try:
            # Get file from IPFS
            self.client.get(ipfs_hash, target=output_path)
            
            logger.info(f"Model downloaded from IPFS: {ipfs_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading from IPFS: {e}")
            # Fallback to gateway
            return self._download_via_gateway(ipfs_hash, output_path)
    
    def _download_via_gateway(self, ipfs_hash: str, output_path: str) -> bool:
        """
        Download file via IPFS HTTP gateway
        
        Args:
            ipfs_hash: IPFS hash
            output_path: Output file path
            
        Returns:
            True if successful
        """
        try:
            import requests
            
            url = f"{self.ipfs_gateway}{ipfs_hash}"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save to file
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Model downloaded via gateway: {ipfs_hash}")
            return True
            
        except Exception as e:
            logger.error(f"Error downloading via gateway: {e}")
            return False
    
    def get_file_url(self, ipfs_hash: str) -> str:
        """
        Get HTTP URL for IPFS file
        
        Args:
            ipfs_hash: IPFS hash
            
        Returns:
            Gateway URL
        """
        return f"{self.ipfs_gateway}{ipfs_hash}"
    
    def pin_hash(self, ipfs_hash: str) -> bool:
        """
        Pin a hash to keep it available
        
        Args:
            ipfs_hash: IPFS hash to pin
            
        Returns:
            True if successful
        """
        if not self.connected or not self.client:
            return False
        
        try:
            self.client.pin.add(ipfs_hash)
            logger.info(f"Pinned IPFS hash: {ipfs_hash}")
            return True
        except Exception as e:
            logger.error(f"Error pinning hash: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if IPFS is connected"""
        return self.connected
