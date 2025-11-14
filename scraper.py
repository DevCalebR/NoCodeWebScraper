"""
ScraperPro - Enterprise Web Scraping Platform
Multi-client, configurable web scraper with tiered pricing support
"""

import os
import json
import time
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
import random
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SubscriptionTier(Enum):
    """Subscription tiers with feature limits"""
    PRO = {
        'name': 'Pro',
        'price': 49,
        'max_requests_per_day': 1000,
        'max_configs': 10,
        'export_formats': ['csv', 'excel', 'json'],
        'scheduling': True,
        'priority_support': False,
        'custom_headers': True,
        'api_access': True
    }
    ENTERPRISE = {
        'name': 'Enterprise',
        'price': 199,
        'max_requests_per_day': -1,  # Unlimited
        'max_configs': -1,  # Unlimited
        'export_formats': ['csv', 'excel', 'json', 'sql'],
        'scheduling': True,
        'priority_support': True,
        'custom_headers': True,
        'api_access': True,
        'dedicated_proxy': True
    }


@dataclass
class ClientConfig:
    """Client configuration with subscription tier"""
    client_id: str
    name: str
    email: str
    tier: str
    api_key: str
    created_at: str
    trial_ends_at: Optional[str] = None  # ISO format datetime
    is_trial: bool = False
    requests_today: int = 0
    last_request_date: str = None
    active: bool = True


@dataclass
class ScraperConfig:
    """Scraper configuration for a specific target"""
    config_id: str
    client_id: str
    name: str
    target_url: str
    selectors: Dict[str, str]
    pagination: Optional[Dict[str, Any]] = None
    custom_headers: Optional[Dict[str, str]] = None
    output_format: str = 'csv'
    schedule: Optional[str] = None  # cron-like format
    active: bool = True


class ClientManager:
    """Manages client subscriptions and configurations"""
    
    def __init__(self, data_dir: str = 'data/clients'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def create_client(self, name: str, email: str, tier: str = 'PRO') -> ClientConfig:
        """Create a new client with unique API key and 7-day trial"""
        client_id = hashlib.md5(f"{email}{datetime.now()}".encode()).hexdigest()[:12]
        api_key = hashlib.sha256(f"{client_id}{email}{time.time()}".encode()).hexdigest()
        
        # Calculate trial end date (7 days from now)
        trial_ends_at = (datetime.now() + timedelta(days=7)).isoformat()
        
        client = ClientConfig(
            client_id=client_id,
            name=name,
            email=email,
            tier=tier,
            api_key=api_key,
            created_at=datetime.now().isoformat(),
            trial_ends_at=trial_ends_at,
            is_trial=True,
            last_request_date=datetime.now().strftime('%Y-%m-%d')
        )
        
        self._save_client(client)
        logger.info(f"Created client {name} ({client_id}) with {tier} tier (7-day trial)")
        return client
    
    def _save_client(self, client: ClientConfig):
        """Save client configuration to disk"""
        file_path = self.data_dir / f"{client.client_id}.json"
        with open(file_path, 'w') as f:
            json.dump(asdict(client), f, indent=2)
    
    def load_client(self, client_id: str) -> Optional[ClientConfig]:
        """Load client configuration"""
        file_path = self.data_dir / f"{client_id}.json"
        if not file_path.exists():
            return None
        
        with open(file_path, 'r') as f:
            data = json.load(f)
            return ClientConfig(**data)
    
    def verify_api_key(self, api_key: str) -> Optional[ClientConfig]:
        """Verify API key and return client"""
        for file_path in self.data_dir.glob('*.json'):
            with open(file_path, 'r') as f:
                data = json.load(f)
                if data.get('api_key') == api_key:
                    return ClientConfig(**data)
        return None
    
    def check_rate_limit(self, client: ClientConfig) -> bool:
        """Check if client has exceeded rate limit"""
        # First check if trial has expired
        if client.is_trial:
            trial_end = datetime.fromisoformat(client.trial_ends_at)
            if datetime.now() > trial_end:
                # Trial expired - deactivate account
                client.active = False
                client.is_trial = False
                self._save_client(client)
                logger.warning(f"Trial expired for client {client.client_id}")
                return False
        
        tier_limits = SubscriptionTier[client.tier].value
        max_requests = tier_limits['max_requests_per_day']
        
        if max_requests == -1:  # Unlimited
            return True
        
        # Reset counter if new day
        today = datetime.now().strftime('%Y-%m-%d')
        if client.last_request_date != today:
            client.requests_today = 0
            client.last_request_date = today
            self._save_client(client)
        
        if client.requests_today >= max_requests:
            logger.warning(f"Rate limit exceeded for client {client.client_id}")
            return False
        
        return True
    
    def increment_usage(self, client: ClientConfig):
        """Increment client usage counter"""
        client.requests_today += 1
        self._save_client(client)
    
    def get_trial_days_remaining(self, client: ClientConfig) -> int:
        """Calculate days remaining in trial"""
        if not client.is_trial:
            return 0
        
        trial_end = datetime.fromisoformat(client.trial_ends_at)
        remaining = (trial_end - datetime.now()).days
        return max(0, remaining)
    
    def convert_trial_to_paid(self, client: ClientConfig) -> bool:
        """Convert trial to paid subscription (simulate payment processing)"""
        if not client.is_trial:
            return False
        
        client.is_trial = False
        client.trial_ends_at = None
        client.active = True
        self._save_client(client)
        
        logger.info(f"Converted client {client.client_id} from trial to paid {client.tier}")
        return True


class WebScraper:
    """Core web scraping engine with anti-detection features"""
    
    def __init__(self):
        self.session = requests.Session()
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
    
    def scrape(self, config: ScraperConfig, client: ClientConfig) -> pd.DataFrame:
        """Execute scraping based on configuration"""
        logger.info(f"Starting scrape for {config.name}")
        
        all_data = []
        current_url = config.target_url
        page_count = 0
        max_pages = 10 if config.pagination else 1
        
        while current_url and page_count < max_pages:
            try:
                # Random delay to avoid detection
                time.sleep(random.uniform(1, 3))
                
                # Fetch page
                html = self._fetch_page(current_url, config.custom_headers)
                soup = BeautifulSoup(html, 'lxml')
                
                # Extract data
                page_data = self._extract_data(soup, config.selectors)
                all_data.extend(page_data)
                
                logger.info(f"Extracted {len(page_data)} items from page {page_count + 1}")
                
                # Handle pagination
                if config.pagination:
                    current_url = self._get_next_page(soup, config.pagination, current_url)
                else:
                    current_url = None
                
                page_count += 1
                
            except Exception as e:
                logger.error(f"Error scraping {current_url}: {str(e)}")
                break
        
        df = pd.DataFrame(all_data)
        df['scraped_at'] = datetime.now().isoformat()
        df['client_id'] = client.client_id
        
        logger.info(f"Scraping completed. Total items: {len(df)}")
        return df
    
    def _fetch_page(self, url: str, custom_headers: Optional[Dict] = None) -> str:
        """Fetch page with anti-detection headers"""
        headers = {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        if custom_headers:
            headers.update(custom_headers)
        
        response = self.session.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    
    def _extract_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> List[Dict]:
        """Extract data using CSS selectors"""
        # Find all items (assuming list structure)
        container_selector = selectors.get('container', 'body')
        containers = soup.select(container_selector)
        
        if not containers:
            # If no container, try to extract from whole page
            containers = [soup]
        
        data = []
        for container in containers:
            item = {}
            for field, selector in selectors.items():
                if field == 'container':
                    continue
                
                element = container.select_one(selector)
                if element:
                    # Try to get text, href, or src
                    if element.name == 'a' and element.get('href'):
                        item[field] = element.get('href')
                    elif element.name == 'img' and element.get('src'):
                        item[field] = element.get('src')
                    else:
                        item[field] = element.get_text(strip=True)
                else:
                    item[field] = None
            
            if any(item.values()):  # Only add if we got some data
                data.append(item)
        
        return data
    
    def _get_next_page(self, soup: BeautifulSoup, pagination: Dict, current_url: str) -> Optional[str]:
        """Extract next page URL"""
        if 'next_selector' in pagination:
            next_link = soup.select_one(pagination['next_selector'])
            if next_link and next_link.get('href'):
                next_url = next_link.get('href')
                if not next_url.startswith('http'):
                    from urllib.parse import urljoin
                    next_url = urljoin(current_url, next_url)
                return next_url
        return None


class DataExporter:
    """Export data in various formats"""
    
    def __init__(self, output_dir: str = 'output'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, df: pd.DataFrame, config: ScraperConfig, client: ClientConfig) -> str:
        """Export data in specified format"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = f"{client.client_id}_{config.config_id}_{timestamp}"
        
        tier_formats = SubscriptionTier[client.tier].value['export_formats']
        format_type = config.output_format if config.output_format in tier_formats else tier_formats[0]
        
        if format_type == 'csv':
            file_path = self.output_dir / f"{base_name}.csv"
            df.to_csv(file_path, index=False)
        elif format_type == 'excel':
            file_path = self.output_dir / f"{base_name}.xlsx"
            df.to_excel(file_path, index=False, engine='openpyxl')
        elif format_type == 'json':
            file_path = self.output_dir / f"{base_name}.json"
            df.to_json(file_path, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
        
        logger.info(f"Exported data to {file_path}")
        return str(file_path)


class ScraperPro:
    """Main application orchestrator"""
    
    def __init__(self):
        self.client_manager = ClientManager()
        self.scraper = WebScraper()
        self.exporter = DataExporter()
        
        # Create necessary directories
        Path('logs').mkdir(exist_ok=True)
        Path('data/configs').mkdir(parents=True, exist_ok=True)
    
    def execute_scrape(self, api_key: str, config_id: str) -> Dict[str, Any]:
        """Execute a scrape job with full validation"""
        # Verify client
        client = self.client_manager.verify_api_key(api_key)
        if not client:
            return {'success': False, 'error': 'Invalid API key'}
        
        if not client.active:
            if client.is_trial:
                return {
                    'success': False, 
                    'error': 'Trial has expired. Please upgrade to continue.',
                    'trial_expired': True,
                    'payment_required': True
                }
            return {'success': False, 'error': 'Account inactive'}
        
        # Check rate limits
        if not self.client_manager.check_rate_limit(client):
            if client.is_trial:
                return {
                    'success': False, 
                    'error': 'Trial has expired. Please upgrade to continue.',
                    'trial_expired': True,
                    'payment_required': True
                }
            
            tier_limits = SubscriptionTier[client.tier].value
            return {
                'success': False,
                'error': f"Rate limit exceeded. Limit: {tier_limits['max_requests_per_day']} requests/day",
                'upgrade_url': '/pricing'
            }
        
        # Load scraper config
        config = self._load_scraper_config(config_id, client.client_id)
        if not config:
            return {'success': False, 'error': 'Configuration not found'}
        
        try:
            # Execute scrape
            df = self.scraper.scrape(config, client)
            
            # Export data
            output_file = self.exporter.export(df, config, client)
            
            # Update usage
            self.client_manager.increment_usage(client)
            
            result = {
                'success': True,
                'records': len(df),
                'output_file': output_file,
                'requests_remaining': self._get_remaining_requests(client)
            }
            
            # Add trial info if applicable
            if client.is_trial:
                days_remaining = self.client_manager.get_trial_days_remaining(client)
                result['trial_info'] = {
                    'is_trial': True,
                    'days_remaining': days_remaining,
                    'trial_ends_at': client.trial_ends_at,
                    'selected_tier': client.tier
                }
            
            return result
            
        except Exception as e:
            logger.error(f"Scrape execution failed: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _load_scraper_config(self, config_id: str, client_id: str) -> Optional[ScraperConfig]:
        """Load scraper configuration"""
        config_file = Path(f'data/configs/{client_id}_{config_id}.json')
        if not config_file.exists():
            return None
        
        with open(config_file, 'r') as f:
            data = json.load(f)
            return ScraperConfig(**data)
    
    def save_scraper_config(self, config: ScraperConfig):
        """Save scraper configuration"""
        config_file = Path(f'data/configs/{config.client_id}_{config.config_id}.json')
        with open(config_file, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    def _get_remaining_requests(self, client: ClientConfig) -> int:
        """Calculate remaining requests for today"""
        tier_limits = SubscriptionTier[client.tier].value
        max_requests = tier_limits['max_requests_per_day']
        
        if max_requests == -1:
            return -1  # Unlimited
        
        return max_requests - client.requests_today


# Example usage
if __name__ == '__main__':
    app = ScraperPro()
    
    # Create a demo client
    client = app.client_manager.create_client(
        name="Demo Client",
        email="demo@example.com",
        tier="PRO"
    )
    
    print(f"Created client with API key: {client.api_key}")
    
    # Create a sample configuration
    demo_config = ScraperConfig(
        config_id="demo_001",
        client_id=client.client_id,
        name="Demo Scraper",
        target_url="https://quotes.toscrape.com/",
        selectors={
            'container': '.quote',
            'text': '.text',
            'author': '.author',
            'tags': '.tags'
        },
        pagination={
            'next_selector': '.next > a'
        },
        output_format='csv'
    )
    
    app.save_scraper_config(demo_config)
    
    # Execute scrape
    result = app.execute_scrape(client.api_key, demo_config.config_id)
    print(json.dumps(result, indent=2))
