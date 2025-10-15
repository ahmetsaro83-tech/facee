#!/usr/bin/env python3
"""
TikTok Scraper Module
Extracts video information (description, hashtags, video URL) from TikTok links
"""

import re
import time
from seleniumbase import SB
from bs4 import BeautifulSoup
from config import BROWSER_HEADLESS, BROWSER_TIMEOUT


class TikTokScraper:
    """TikTok video information scraper"""
    
    def __init__(self, headless=BROWSER_HEADLESS):
        """Initialize the scraper with browser settings"""
        self.headless = headless
        self.driver = None
        
    def scrape_tiktok_info(self, tiktok_url):
        """
        Scrape TikTok video information including description, hashtags, and video URL
        
        Args:
            tiktok_url (str): TikTok video URL
            
        Returns:
            dict: Dictionary containing video information
        """
        try:
            print(f"TikTok sayfası açılıyor: {tiktok_url}")
            
            # Use SB context manager with UC mode for TikTok
            with SB(uc=True, headless=self.headless, test=True) as sb:
                # Open TikTok URL with UC mode
                sb.uc_open_with_reconnect(tiktok_url, reconnect_time=4)
                
                # Wait for page to load
                time.sleep(3)
                
                # Wait for page to fully load and try different selectors
                description_selectors = [
                    'div[data-e2e="browse-video-desc"]',
                    'div[data-e2e="video-desc"]',
                    'div.css-1poc4bs-5e6d46e3--DivDescriptionContentContainer',
                    'div[class*="DivDescriptionContentContainer"]'
                ]
                
                description_found = False
                for selector in description_selectors:
                    try:
                        sb.wait_for_element(selector, timeout=5)
                        description_found = True
                        print(f"Açıklama container'ı bulundu: {selector}")
                        break
                    except:
                        continue
                
                if not description_found:
                    print("Açıklama container'ı bulunamadı, sayfayı yeniden yükleniyor...")
                    sb.refresh()
                    time.sleep(5)
                    # Try again after refresh
                    for selector in description_selectors:
                        try:
                            sb.wait_for_element(selector, timeout=5)
                            description_found = True
                            print(f"Yenileme sonrası açıklama container'ı bulundu: {selector}")
                            break
                        except:
                            continue
                
                # Get page source
                page_source = sb.get_page_source()
                soup = BeautifulSoup(page_source, 'html.parser')
                
                # Extract video information
                video_info = self._extract_video_info(soup, tiktok_url)
                
                print("TikTok video bilgileri başarıyla çekildi!")
                return video_info
            
        except Exception as e:
            print(f"TikTok scraping hatası: {str(e)}")
            raise
                
    def _extract_video_info(self, soup, original_url):
        """
        Extract video information from BeautifulSoup object
        
        Args:
            soup: BeautifulSoup object of the page
            original_url: Original TikTok URL
            
        Returns:
            dict: Extracted video information
        """
        video_info = {
            'url': original_url,
            'description': '',
            'hashtags': [],
            'mentions': [],
            'full_text': '',
            'video_download_url': '',
            'author': '',
            'timestamp': time.time()
        }
        
        try:
            # Try different selectors for description container
            desc_container = None
            
            # Try multiple selectors
            selectors_to_try = [
                {'data-e2e': 'browse-video-desc'},
                {'data-e2e': 'video-desc'},
                {'class': lambda x: x and 'DivDescriptionContentContainer' in x}
            ]
            
            for selector in selectors_to_try:
                desc_container = soup.find('div', selector)
                if desc_container:
                    print(f"Açıklama container'ı bulundu: {selector}")
                    break
            
            if desc_container:
                # Extract full text content
                video_info['full_text'] = desc_container.get_text(strip=True)
                print(f"Tam metin: {video_info['full_text']}")
                
                # Extract description (text that's not in hashtags or mentions)
                description_parts = []
                hashtags = []
                mentions = []
                
                # Process all spans and links in the description
                for element in desc_container.find_all(['span', 'a']):
                    if element.name == 'span':
                        # Check for description spans
                        if (element.get('data-e2e') == 'new-desc-span' or 
                            'font-weight: 400' in str(element.get('style', ''))):
                            text = element.get_text(strip=True)
                            if text and not text.startswith('#') and not text.startswith('@'):
                                description_parts.append(text)
                    
                    elif element.name == 'a':
                        # Check for hashtag links
                        if (element.get('data-e2e') == 'search-common-link' or
                            '/tag/' in element.get('href', '')):
                            hashtag_text = element.get_text(strip=True)
                            if hashtag_text.startswith('#'):
                                hashtags.append(hashtag_text)
                
                # Extract mentions from the full text using regex
                mention_pattern = r'@[\w._]+'
                mentions = re.findall(mention_pattern, video_info['full_text'])
                
                # Also extract hashtags from full text if not found in links
                hashtag_pattern = r'#[\w\u00C0-\u017F\u0100-\u024F\u1E00-\u1EFF]+'
                text_hashtags = re.findall(hashtag_pattern, video_info['full_text'])
                hashtags.extend(text_hashtags)
                
                # Clean up description
                video_info['description'] = ' '.join(description_parts).strip()
                video_info['hashtags'] = list(set(hashtags))  # Remove duplicates
                video_info['mentions'] = list(set(mentions))  # Remove duplicates
                
                # If no description found in spans, try to extract from full text
                if not video_info['description'] and video_info['full_text']:
                    # Remove hashtags and mentions from full text to get description
                    clean_text = video_info['full_text']
                    for hashtag in hashtags:
                        clean_text = clean_text.replace(hashtag, '')
                    for mention in mentions:
                        clean_text = clean_text.replace(mention, '')
                    video_info['description'] = clean_text.strip()
                
            # Try to extract author information
            try:
                author_element = soup.find('span', {'data-e2e': 'browse-username'})
                if author_element:
                    video_info['author'] = author_element.get_text(strip=True)
            except:
                pass
                
            # Try to extract video download URL (this might need adjustment based on TikTok's structure)
            try:
                video_element = soup.find('video')
                if video_element and video_element.get('src'):
                    video_info['video_download_url'] = video_element.get('src')
            except:
                pass
                
            print(f"Açıklama: {video_info['description']}")
            print(f"Hashtag'ler: {video_info['hashtags']}")
            print(f"Mention'lar: {video_info['mentions']}")
            print(f"Yazar: {video_info['author']}")
            
        except Exception as e:
            print(f"Video bilgisi çıkarma hatası: {str(e)}")
            
        return video_info
        
    def extract_video_id(self, tiktok_url):
        """
        Extract video ID from TikTok URL
        
        Args:
            tiktok_url (str): TikTok video URL
            
        Returns:
            str: Video ID or None if not found
        """
        # Pattern to match TikTok video URLs
        pattern = r'tiktok\.com/@[\w.-]+/video/(\d+)'
        match = re.search(pattern, tiktok_url)
        
        if match:
            return match.group(1)
        return None
        
    def is_valid_tiktok_url(self, url):
        """
        Check if the provided URL is a valid TikTok video URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid TikTok URL, False otherwise
        """
        tiktok_patterns = [
            r'https?://(?:www\.)?tiktok\.com/@[\w.-]+/video/\d+',
            r'https?://(?:vm|vt)\.tiktok\.com/[\w]+',
            r'https?://(?:www\.)?tiktok\.com/t/[\w]+',
        ]
        
        for pattern in tiktok_patterns:
            if re.match(pattern, url):
                return True
        return False


def test_scraper():
    """Test function for the TikTok scraper"""
    # Gerçek bir TikTok URL'si ile test edin
    test_url = input("TikTok URL'sini girin: ").strip()
    
    if not test_url:
        print("URL girilmedi!")
        return
    
    scraper = TikTokScraper(headless=False)
    
    try:
        if scraper.is_valid_tiktok_url(test_url):
            print("URL geçerli, video bilgileri çekiliyor...")
            video_info = scraper.scrape_tiktok_info(test_url)
            print("\n=== Çekilen bilgiler ===")
            print(f"URL: {video_info.get('url', 'N/A')}")
            print(f"Açıklama: {video_info.get('description', 'N/A')}")
            print(f"Hashtag'ler: {video_info.get('hashtags', [])}")
            print(f"Mention'lar: {video_info.get('mentions', [])}")
            print(f"Yazar: {video_info.get('author', 'N/A')}")
            print(f"Tam metin: {video_info.get('full_text', 'N/A')}")
        else:
            print("Geçersiz TikTok URL'si!")
            
    except Exception as e:
        print(f"Test hatası: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_scraper()