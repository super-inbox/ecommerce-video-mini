"""
Website scraper for extracting images and product descriptions
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import Dict, List
import os
from pathlib import Path


class WebsiteScraper:
    """Scrapes images and text content from websites"""
    
    def __init__(self, download_dir: str = "downloaded_images"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape(self, url: str) -> Dict:
        """
        Scrape website for images and descriptions
        
        Args:
            url: Website URL to scrape
            
        Returns:
            Dictionary containing images, descriptions, and brand info
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract brand name
            brand_name = self._extract_brand_name(soup, url)
            
            # Extract images
            images = self._extract_images(soup, url)
            
            # Extract product descriptions
            descriptions = self._extract_descriptions(soup)
            
            return {
                'url': url,
                'brand_name': brand_name,
                'images': images,
                'descriptions': descriptions
            }
            
        except Exception as e:
            raise Exception(f"Failed to scrape website: {str(e)}")
    
    def _extract_brand_name(self, soup: BeautifulSoup, url: str) -> str:
        """Extract brand name from page"""
        # Try meta tags first
        og_site_name = soup.find('meta', property='og:site_name')
        if og_site_name and og_site_name.get('content'):
            return og_site_name['content']
        
        # Try title
        title = soup.find('title')
        if title:
            return title.text.split('|')[0].split('-')[0].strip()
        
        # Fallback to domain name
        domain = urlparse(url).netloc
        return domain.replace('www.', '').split('.')[0].capitalize()
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract and download images from the page"""
        images = []
        img_tags = soup.find_all('img')
        
        for i, img in enumerate(img_tags[:20]):  # Limit to 20 images
            src = img.get('src') or img.get('data-src')
            if not src:
                continue
            
            # Skip small images (likely icons)
            width = img.get('width')
            height = img.get('height')
            if width and height:
                try:
                    if int(width) < 200 or int(height) < 200:
                        continue
                except:
                    pass
            
            # Make URL absolute
            img_url = urljoin(base_url, src)
            
            # Download image
            try:
                local_path = self._download_image(img_url, i)
                if local_path:
                    images.append({
                        'url': img_url,
                        'local_path': str(local_path),
                        'alt': img.get('alt', ''),
                        'index': i
                    })
            except Exception as e:
                print(f"Warning: Could not download image {img_url}: {e}")
                continue
        
        return images
    
    def _download_image(self, url: str, index: int) -> Path:
        """Download an image to local storage"""
        try:
            response = self.session.get(url, timeout=5)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = '.jpg'
            elif 'png' in content_type:
                ext = '.png'
            elif 'webp' in content_type:
                ext = '.webp'
            else:
                ext = '.jpg'  # Default
            
            # Save file
            filename = self.download_dir / f"image_{index}{ext}"
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return filename
            
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")
    
    def _extract_descriptions(self, soup: BeautifulSoup) -> List[str]:
        """Extract product descriptions and relevant text"""
        descriptions = []
        
        # Look for product descriptions in common tags
        selectors = [
            'meta[name="description"]',
            'meta[property="og:description"]',
            '.product-description',
            '.description',
            'article p',
            '.content p'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                if selector.startswith('meta'):
                    text = elem.get('content', '')
                else:
                    text = elem.get_text(strip=True)
                
                if text and len(text) > 20:  # Minimum length
                    descriptions.append(text)
        
        # Get main heading
        h1 = soup.find('h1')
        if h1:
            descriptions.insert(0, h1.get_text(strip=True))
        
        return descriptions[:10]  # Limit to 10 descriptions