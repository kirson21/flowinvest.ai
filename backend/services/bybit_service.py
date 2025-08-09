import aiohttp
import asyncio
import json
import hmac
import hashlib
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import websockets
import logging

class BybitService:
    def __init__(self):
        # Bybit API endpoints
        self.base_url_testnet = "https://api-testnet.bybit.com"
        self.base_url_mainnet = "https://api.bybit.com"
        self.ws_url_testnet = "wss://stream-testnet.bybit.com/v5/public/linear"
        self.ws_url_mainnet = "wss://stream.bybit.com/v5/public/linear"
        
        # Test API credentials (provided by user)
        self.test_api_key = "RAv5owejCE8AAY65Kb"
        self.test_api_secret = "pkIhdF9Sgo8H1WTtyEDXwrUWYUS8YgLkbqMZ"
        
        self.session = None
        self.websocket_connections = {}
        
    async def initialize(self):
        """Initialize HTTP session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close(self):
        """Close HTTP session and WebSocket connections"""
        if self.session:
            await self.session.close()
        
        for ws in self.websocket_connections.values():
            if not ws.closed:
                await ws.close()
    
    def _generate_signature(self, params: str, api_secret: str) -> str:
        """Generate HMAC SHA256 signature for Bybit API"""
        return hmac.new(
            api_secret.encode('utf-8'),
            params.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    def _get_headers(self, api_key: str, signature: str, timestamp: str) -> Dict[str, str]:
        """Get headers for authenticated requests"""
        return {
            'X-BAPI-API-KEY': api_key,
            'X-BAPI-SIGN': signature,
            'X-BAPI-TIMESTAMP': timestamp,
            'X-BAPI-RECV-WINDOW': '5000',
            'Content-Type': 'application/json'
        }
    
    async def test_connection(self, api_key: str = None, api_secret: str = None, is_testnet: bool = True) -> Dict[str, Any]:
        """Test connection to Bybit API"""
        await self.initialize()
        
        # Use provided credentials or default test credentials
        key = api_key or self.test_api_key
        secret = api_secret or self.test_api_secret
        base_url = self.base_url_testnet if is_testnet else self.base_url_mainnet
        
        try:
            # Test public endpoint first
            public_url = f"{base_url}/v5/market/time"
            async with self.session.get(public_url) as response:
                if response.status != 200:
                    return {"success": False, "error": "Public API connection failed"}
                
                data = await response.json()
                server_time = data.get('time', 'Unknown')
            
            # Test private endpoint
            timestamp = str(int(time.time() * 1000))
            param_str = f"timestamp={timestamp}&recv_window=5000"
            signature = self._generate_signature(param_str, secret)
            
            private_url = f"{base_url}/v5/account/wallet-balance"
            headers = self._get_headers(key, signature, timestamp)
            
            async with self.session.get(f"{private_url}?{param_str}", headers=headers) as response:
                if response.status == 200:
                    account_data = await response.json()
                    return {
                        "success": True,
                        "server_time": server_time,
                        "account_connected": True,
                        "testnet": is_testnet,
                        "message": "Bybit API connection successful"
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": f"Authentication failed: {error_data.get('retMsg', 'Unknown error')}",
                        "code": error_data.get('retCode')
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Connection failed: {str(e)}"
            }
    
    async def get_account_info(self, api_key: str, api_secret: str, is_testnet: bool = True) -> Dict[str, Any]:
        """Get account information"""
        await self.initialize()
        
        base_url = self.base_url_testnet if is_testnet else self.base_url_mainnet
        
        try:
            timestamp = str(int(time.time() * 1000))
            param_str = f"timestamp={timestamp}&recv_window=5000"
            signature = self._generate_signature(param_str, api_secret)
            
            url = f"{base_url}/v5/account/wallet-balance"
            headers = self._get_headers(api_key, signature, timestamp)
            
            async with self.session.get(f"{url}?{param_str}", headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "account_info": data.get('result', {}),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": error_data.get('retMsg', 'Failed to get account info')
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get account info: {str(e)}"
            }
    
    async def get_market_data(self, symbol: str, is_testnet: bool = True) -> Dict[str, Any]:
        """Get market data for a symbol"""
        await self.initialize()
        
        base_url = self.base_url_testnet if is_testnet else self.base_url_mainnet
        
        try:
            # Get ticker data
            ticker_url = f"{base_url}/v5/market/tickers"
            params = {"category": "linear", "symbol": symbol}
            
            async with self.session.get(ticker_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    tickers = data.get('result', {}).get('list', [])
                    
                    if tickers:
                        ticker = tickers[0]
                        return {
                            "success": True,
                            "symbol": symbol,
                            "price": float(ticker.get('lastPrice', 0)),
                            "volume": float(ticker.get('volume24h', 0)),
                            "change_24h": float(ticker.get('price24hPcnt', 0)),
                            "high_24h": float(ticker.get('highPrice24h', 0)),
                            "low_24h": float(ticker.get('lowPrice24h', 0)),
                            "timestamp": datetime.utcnow().isoformat()
                        }
                    else:
                        return {"success": False, "error": f"No data for symbol {symbol}"}
                else:
                    return {"success": False, "error": f"API request failed: {response.status}"}
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to get market data: {str(e)}"
            }
    
    async def place_order(
        self, 
        api_key: str, 
        api_secret: str, 
        symbol: str,
        side: str,  # "Buy" or "Sell"
        order_type: str,  # "Market" or "Limit"
        qty: str,
        price: str = None,
        is_testnet: bool = True,
        is_paper_trade: bool = True
    ) -> Dict[str, Any]:
        """Place an order (paper trade or real)"""
        
        if is_paper_trade:
            # Simulate paper trade
            return await self._simulate_paper_trade(symbol, side, order_type, qty, price)
        
        await self.initialize()
        base_url = self.base_url_testnet if is_testnet else self.base_url_mainnet
        
        try:
            timestamp = str(int(time.time() * 1000))
            
            # Prepare order data
            order_data = {
                "category": "linear",
                "symbol": symbol,
                "side": side,
                "orderType": order_type,
                "qty": qty,
                "timestamp": timestamp,
                "recv_window": "5000"
            }
            
            if order_type == "Limit" and price:
                order_data["price"] = price
            
            # Create signature
            param_str = "&".join([f"{k}={v}" for k, v in sorted(order_data.items())])
            signature = self._generate_signature(param_str, api_secret)
            
            url = f"{base_url}/v5/order/create"
            headers = self._get_headers(api_key, signature, timestamp)
            
            async with self.session.post(url, json=order_data, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('retCode') == 0:
                        return {
                            "success": True,
                            "order_id": data.get('result', {}).get('orderId'),
                            "message": "Order placed successfully"
                        }
                    else:
                        return {
                            "success": False,
                            "error": data.get('retMsg', 'Order placement failed')
                        }
                else:
                    error_data = await response.json()
                    return {
                        "success": False,
                        "error": f"Order placement failed: {error_data.get('retMsg', 'Unknown error')}"
                    }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to place order: {str(e)}"
            }
    
    async def _simulate_paper_trade(
        self, 
        symbol: str, 
        side: str, 
        order_type: str, 
        qty: str, 
        price: str = None
    ) -> Dict[str, Any]:
        """Simulate a paper trade"""
        
        try:
            # Get current market price
            market_data = await self.get_market_data(symbol, is_testnet=True)
            
            if not market_data["success"]:
                return {"success": False, "error": "Failed to get market price for paper trade"}
            
            current_price = market_data["price"]
            fill_price = float(price) if price and order_type == "Limit" else current_price
            
            # Simulate order execution
            simulated_order = {
                "success": True,
                "order_id": f"paper_{int(time.time() * 1000)}",
                "symbol": symbol,
                "side": side,
                "order_type": order_type,
                "quantity": float(qty),
                "price": fill_price,
                "status": "filled",
                "fill_time": datetime.utcnow().isoformat(),
                "is_paper_trade": True,
                "message": "Paper trade executed successfully"
            }
            
            return simulated_order
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Paper trade simulation failed: {str(e)}"
            }
    
    async def start_websocket_connection(self, symbols: List[str], callback, is_testnet: bool = True):
        """Start WebSocket connection for real-time data"""
        ws_url = self.ws_url_testnet if is_testnet else self.ws_url_mainnet
        
        try:
            websocket = await websockets.connect(ws_url)
            self.websocket_connections[f"market_data_{is_testnet}"] = websocket
            
            # Subscribe to ticker updates
            subscribe_msg = {
                "op": "subscribe",
                "args": [f"tickers.{symbol}" for symbol in symbols]
            }
            
            await websocket.send(json.dumps(subscribe_msg))
            
            # Listen for messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('topic') and data.get('topic').startswith('tickers.'):
                        await callback(data)
                except json.JSONDecodeError:
                    logging.warning(f"Failed to parse WebSocket message: {message}")
                except Exception as e:
                    logging.error(f"Error processing WebSocket message: {e}")
        
        except Exception as e:
            logging.error(f"WebSocket connection failed: {e}")
            return {"success": False, "error": f"WebSocket connection failed: {str(e)}"}
    
    async def stop_websocket_connection(self, connection_key: str):
        """Stop a specific WebSocket connection"""
        if connection_key in self.websocket_connections:
            websocket = self.websocket_connections[connection_key]
            if not websocket.closed:
                await websocket.close()
            del self.websocket_connections[connection_key]
    
    async def get_supported_symbols(self, is_testnet: bool = True) -> List[str]:
        """Get list of supported trading symbols"""
        await self.initialize()
        
        base_url = self.base_url_testnet if is_testnet else self.base_url_mainnet
        
        try:
            url = f"{base_url}/v5/market/instruments-info"
            params = {"category": "linear"}
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    instruments = data.get('result', {}).get('list', [])
                    
                    symbols = []
                    for instrument in instruments:
                        if instrument.get('status') == 'Trading':
                            symbols.append(instrument.get('symbol'))
                    
                    return symbols[:100]  # Return first 100 active symbols
                else:
                    return ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT"]  # Fallback list
        
        except Exception as e:
            logging.error(f"Failed to get supported symbols: {e}")
            return ["BTCUSDT", "ETHUSDT", "ADAUSDT", "SOLUSDT", "DOGEUSDT"]  # Fallback list