import requests
import base64
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


@dataclass
class KrogerProduct:
    """Data class for Kroger product information"""

    product_id: int
    name: str
    description: str
    price: float
    brand: str
    category: str

    def to_dict(self) -> Dict:
        """Convert product to dictionary"""
        return {
            "product_id": self.product_id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "brand": self.brand,
            "category": self.category,
        }

    @classmethod
    def from_api_response(cls, data: Dict) -> "KrogerProduct":
        """Create KrogerProduct from API response data"""
        items = data.get("items", [{}])
        price = items[0].get("price", {}).get("regular", 0.0) if items else 0.0
        return cls(
            product_id=int(data.get("productId", 0)),
            name=data.get("description", ""),
            description=data.get("description", ""),
            price=price,
            brand=data.get("brand", ""),
            category=data.get("categories", [""])[0] if data.get("categories") else "",
        )


class KrogerAPIError(Exception):
    """Custom exception for Kroger API errors"""

    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class KrogerAPI:
    """Handler for Kroger API interactions with improved error handling"""

    def __init__(self, client_id: str, client_secret: str):
        if not client_id or not client_secret:
            raise ValueError("Kroger API credentials are required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = "https://api-ce.kroger.com/v1"
        self.access_token = None
        self.token_expiry = None
        self.calls_remaining = 10000
        self.rate_limit_reset = datetime.now() + timedelta(days=1)

    def _get_auth_header(self) -> Dict[str, str]:
        """Get base64 encoded authorization header"""
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded_credentials}"}

    def _check_rate_limit(self):
        """Check and manage rate limiting"""
        now = datetime.now()
        if now >= self.rate_limit_reset:
            self.calls_remaining = 10000
            self.rate_limit_reset = now + timedelta(days=1)

        if self.calls_remaining <= 0:
            raise KrogerAPIError(
                "Rate limit exceeded. Please try again tomorrow.", status_code=429
            )

        self.calls_remaining -= 1

    def get_access_token(self) -> str:
        """Get access token using client credentials flow"""
        url = f"{self.base_url}/connect/oauth2/token"
        headers = {
            **self._get_auth_header(),
            "Content-Type": "application/x-www-form-urlencoded",
        }
        data = {"grant_type": "client_credentials", "scope": "product.compact"}

        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()

            self.access_token = token_data.get("access_token")
            self.token_expiry = datetime.now() + timedelta(
                seconds=token_data.get("expires_in", 3600) - 60
            )

            logger.info("Successfully obtained access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Response content: {e.response.text}")
            raise KrogerAPIError(
                "Failed to authenticate with Kroger API", status_code=401
            )

    def _ensure_valid_token(self):
        """Ensure we have a valid access token"""
        if not self.access_token or (
            self.token_expiry and datetime.now() >= self.token_expiry
        ):
            self.get_access_token()

    def search_products(
        self, ingredient: str, location_id: str, limit: int = 5
    ) -> List[KrogerProduct]:
        """Search for products matching an ingredient"""
        self._check_rate_limit()
        self._ensure_valid_token()

        url = f"{self.base_url}/products"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }
        params = {
            "filter.term": ingredient,
            "filter.locationId": location_id,
            "filter.limit": limit,
        }

        try:
            logger.debug(f"Searching products: {params}")
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 401:
                # Token expired, retry once
                self.get_access_token()
                headers["Authorization"] = f"Bearer {self.access_token}"
                response = requests.get(url, headers=headers, params=params)

            response.raise_for_status()
            data = response.json()

            products = []
            for item in data.get("data", []):
                try:
                    product = KrogerProduct.from_api_response(item)
                    products.append(product)
                except Exception as e:
                    logger.error(f"Error processing product data: {e}")
                    continue

            return products

        except requests.exceptions.RequestException as e:
            logger.error(f"Product search failed: {str(e)}")
            if hasattr(e.response, "text"):
                logger.error(f"Response content: {e.response.text}")
            if e.response.status_code == 429:
                raise KrogerAPIError("Rate limit exceeded", status_code=429)
            raise KrogerAPIError(
                "Failed to search products", status_code=e.response.status_code
            )
