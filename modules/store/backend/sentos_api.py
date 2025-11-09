"""
Sentos API Integration
Documentation: https://api.sentos.com.tr/docs
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from django.utils import timezone
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class SentosAPI:
    """Sentos API client for marketplace integration"""
    
    def __init__(self, api_key: str, shop_url: str = None):
        self.api_key = api_key
        self.shop_url = shop_url or "https://berkinatolyesi.sentos.com.tr"
        self.base_url = "https://api.sentos.com.tr/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None, params: Dict = None) -> Dict:
        """Make API request with error handling"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                params=params,
                timeout=30
            )
            
            # Log the request for debugging
            logger.info(f"Sentos API {method} {endpoint}: {response.status_code}")
            
            if response.status_code == 401:
                raise Exception("Invalid API key or authentication failed")
            
            response.raise_for_status()
            
            return response.json() if response.text else {}
            
        except requests.exceptions.Timeout:
            logger.error(f"Sentos API timeout: {endpoint}")
            raise Exception("API request timed out")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Sentos API error: {str(e)}")
            raise Exception(f"API request failed: {str(e)}")
    
    # Shop Information
    def get_shop_info(self) -> Dict:
        """Get shop information"""
        return self._make_request("GET", "shop")
    
    def get_marketplaces(self) -> List[Dict]:
        """Get connected marketplaces"""
        return self._make_request("GET", "marketplaces")
    
    # Orders Management
    def get_orders(self, 
                   status: str = None,
                   start_date: datetime = None,
                   end_date: datetime = None,
                   marketplace: str = None,
                   page: int = 1,
                   limit: int = 50) -> Dict:
        """
        Get orders from Sentos
        
        Args:
            status: Order status filter (pending, processing, shipped, etc.)
            start_date: Start date for order filter
            end_date: End date for order filter
            marketplace: Filter by marketplace (amazon, etsy, etc.)
            page: Page number for pagination
            limit: Number of items per page
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if status:
            params["status"] = status
        
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        if end_date:
            params["end_date"] = end_date.isoformat()
        
        if marketplace:
            params["marketplace"] = marketplace
        
        return self._make_request("GET", "orders", params=params)
    
    def get_order(self, order_id: str) -> Dict:
        """Get single order details"""
        return self._make_request("GET", f"orders/{order_id}")
    
    def update_order_status(self, order_id: str, status: str, tracking_info: Dict = None) -> Dict:
        """
        Update order status
        
        Args:
            order_id: Order ID
            status: New status (processing, shipped, delivered, cancelled)
            tracking_info: Optional tracking information
        """
        data = {"status": status}
        
        if tracking_info:
            data.update({
                "tracking_number": tracking_info.get("tracking_number"),
                "tracking_company": tracking_info.get("tracking_company"),
                "tracking_url": tracking_info.get("tracking_url")
            })
        
        return self._make_request("PUT", f"orders/{order_id}/status", data=data)
    
    def get_order_items(self, order_id: str) -> List[Dict]:
        """Get order items"""
        return self._make_request("GET", f"orders/{order_id}/items")
    
    # Products Management
    def get_products(self,
                     marketplace: str = None,
                     status: str = None,
                     page: int = 1,
                     limit: int = 50) -> Dict:
        """
        Get products from Sentos
        
        Args:
            marketplace: Filter by marketplace
            status: Product status (active, inactive, out_of_stock)
            page: Page number
            limit: Items per page
        """
        params = {
            "page": page,
            "limit": limit
        }
        
        if marketplace:
            params["marketplace"] = marketplace
        
        if status:
            params["status"] = status
        
        return self._make_request("GET", "products", params=params)
    
    def get_product(self, product_id: str) -> Dict:
        """Get single product details"""
        return self._make_request("GET", f"products/{product_id}")
    
    def update_product_stock(self, product_id: str, quantity: int) -> Dict:
        """Update product stock quantity"""
        data = {"stock_quantity": quantity}
        return self._make_request("PUT", f"products/{product_id}/stock", data=data)
    
    def update_product_price(self, product_id: str, price: float, sale_price: float = None) -> Dict:
        """Update product price"""
        data = {"price": price}
        if sale_price is not None:
            data["sale_price"] = sale_price
        
        return self._make_request("PUT", f"products/{product_id}/price", data=data)
    
    # Inventory Management
    def get_inventory(self, page: int = 1, limit: int = 100) -> Dict:
        """Get inventory list"""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", "inventory", params=params)
    
    def bulk_update_inventory(self, updates: List[Dict]) -> Dict:
        """
        Bulk update inventory
        
        Args:
            updates: List of inventory updates
                [{"sku": "SKU123", "quantity": 10}, ...]
        """
        data = {"updates": updates}
        return self._make_request("POST", "inventory/bulk-update", data=data)
    
    # Customer Management
    def get_customers(self, page: int = 1, limit: int = 50) -> Dict:
        """Get customer list"""
        params = {"page": page, "limit": limit}
        return self._make_request("GET", "customers", params=params)
    
    def get_customer(self, customer_id: str) -> Dict:
        """Get customer details"""
        return self._make_request("GET", f"customers/{customer_id}")
    
    def get_customer_orders(self, customer_id: str) -> List[Dict]:
        """Get customer's order history"""
        return self._make_request("GET", f"customers/{customer_id}/orders")
    
    # Reports and Analytics
    def get_sales_report(self, start_date: datetime, end_date: datetime, marketplace: str = None) -> Dict:
        """Get sales report"""
        params = {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        }
        
        if marketplace:
            params["marketplace"] = marketplace
        
        return self._make_request("GET", "reports/sales", params=params)
    
    def get_inventory_report(self) -> Dict:
        """Get inventory report with low stock items"""
        return self._make_request("GET", "reports/inventory")
    
    def get_marketplace_performance(self, marketplace: str = None) -> Dict:
        """Get marketplace performance metrics"""
        params = {}
        if marketplace:
            params["marketplace"] = marketplace
        
        return self._make_request("GET", "reports/performance", params=params)
    
    # Webhook Management
    def register_webhook(self, event_type: str, url: str) -> Dict:
        """
        Register webhook for events
        
        Args:
            event_type: Event type (order.created, order.updated, etc.)
            url: Webhook URL
        """
        data = {
            "event_type": event_type,
            "url": url
        }
        return self._make_request("POST", "webhooks", data=data)
    
    def get_webhooks(self) -> List[Dict]:
        """Get registered webhooks"""
        return self._make_request("GET", "webhooks")
    
    def delete_webhook(self, webhook_id: str) -> Dict:
        """Delete webhook"""
        return self._make_request("DELETE", f"webhooks/{webhook_id}")
    
    # Utility Methods
    def test_connection(self) -> bool:
        """Test API connection"""
        try:
            self.get_shop_info()
            return True
        except Exception as e:
            logger.error(f"Sentos API connection test failed: {str(e)}")
            return False
    
    def sync_orders(self, since_date: datetime = None) -> Dict:
        """
        Sync all orders since a given date
        
        Args:
            since_date: Sync orders from this date (default: last 7 days)
        """
        if not since_date:
            since_date = timezone.now() - timedelta(days=7)
        
        results = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            page = 1
            while True:
                response = self.get_orders(
                    start_date=since_date,
                    page=page,
                    limit=100
                )
                
                orders = response.get("data", [])
                if not orders:
                    break
                
                for order_data in orders:
                    try:
                        # Process each order (to be implemented in views)
                        results["total"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(str(e))
                
                # Check if there are more pages
                if not response.get("has_next", False):
                    break
                
                page += 1
        
        except Exception as e:
            logger.error(f"Order sync failed: {str(e)}")
            results["errors"].append(str(e))
        
        return results
    
    def sync_products(self) -> Dict:
        """Sync all products"""
        results = {
            "total": 0,
            "created": 0,
            "updated": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            page = 1
            while True:
                response = self.get_products(page=page, limit=100)
                
                products = response.get("data", [])
                if not products:
                    break
                
                for product_data in products:
                    try:
                        # Process each product (to be implemented in views)
                        results["total"] += 1
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(str(e))
                
                # Check if there are more pages
                if not response.get("has_next", False):
                    break
                
                page += 1
        
        except Exception as e:
            logger.error(f"Product sync failed: {str(e)}")
            results["errors"].append(str(e))
        
        return results