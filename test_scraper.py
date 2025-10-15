#!/usr/bin/env python3
"""
TikTok Scraper Test Script
Belirli bir TikTok URL'si ile scraper'ı test eder
"""

import sys
import json
from tiktok_scraper import scrape_tiktok_video_info

def test_tiktok_scraper():
    """TikTok scraper'ı test et"""
    
    # Test URL'si - Gerçek TikTok linki
    test_url = "https://www.tiktok.com/@burukhisler_/video/7558576126000401671"
    
    print("=" * 60)
    print("TikTok Scraper Test")
    print("=" * 60)
    print(f"Test URL: {test_url}")
    print("=" * 60)
    
    try:
        # Scraper'ı çalıştır
        result = scrape_tiktok_video_info(test_url, headless=False)
        
        print("\nScraping Sonucu:")
        print("-" * 40)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Sonuçları analiz et
        print("\nAnaliz:")
        print("-" * 40)
        print(f"URL: {result.get('url', 'N/A')}")
        print(f"Açıklama: '{result.get('description', 'Bulunamadı')}'")
        print(f"Açıklama uzunluğu: {len(result.get('description', ''))}")
        print(f"Hashtag'ler: {result.get('hashtags', [])}")
        print(f"Hashtag sayısı: {len(result.get('hashtags', []))}")
        print(f"Mentions: {result.get('mentions', [])}")
        print(f"Mention sayısı: {len(result.get('mentions', []))}")
        print(f"Başarılı: {result.get('scraping_successful', False)}")
        
        if result.get('error'):
            print(f"Hata: {result.get('error')}")
        
        # Beklenen sonuçları kontrol et
        print("\nBeklenen Sonuçlar:")
        print("-" * 40)
        expected_description = "Sevgiyi dışarı vurunca sevilmeyi de anlıyorsunuz."
        expected_hashtags = ["#ömertuğrulinançer", "#vavtv", "#sevgi", "#sevmek", "#karşılıklısevgi"]
        expected_mentions = ["@burukhisler_", "@tugrulinancer"]
        
        print(f"Beklenen açıklama: '{expected_description}'")
        print(f"Beklenen hashtag'ler: {expected_hashtags}")
        print(f"Beklenen mentions: {expected_mentions}")
        
        # Karşılaştırma
        print("\nKarşılaştırma:")
        print("-" * 40)
        if result.get('description'):
            if expected_description.lower() in result.get('description', '').lower():
                print("✅ Açıklama doğru çıkarıldı!")
            else:
                print("❌ Açıklama beklenenden farklı")
        else:
            print("❌ Açıklama bulunamadı")
            
        if len(result.get('hashtags', [])) >= 3:
            print("✅ Hashtag'ler çıkarıldı!")
        else:
            print("❌ Hashtag'ler yetersiz")
            
        if len(result.get('mentions', [])) >= 1:
            print("✅ Mentions çıkarıldı!")
        else:
            print("❌ Mentions bulunamadı")
        
    except Exception as e:
        print(f"Test hatası: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_tiktok_scraper()
