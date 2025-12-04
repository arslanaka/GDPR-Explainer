import requests
from bs4 import BeautifulSoup
import json
import os
import time

# Configuration
BASE_URL = "https://gdpr-info.eu"
OUTPUT_DIR = "../data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "gdpr_raw.json")

def fetch_article(article_num):
    url = f"{BASE_URL}/art-{article_num}-gdpr/"
    try:
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch Article {article_num}: Status {response.status_code}")
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Title
        title_tag = soup.find('h1', class_='entry-title')
        title = title_tag.text.strip() if title_tag else f"Article {article_num}"
        
        # Extract Content
        content_div = soup.find('div', class_='entry-content')
        if not content_div:
            return None
            
        # Remove unwanted elements (like ads or navigation if any inside content)
        for script in content_div(["script", "style"]):
            script.decompose()
            
        text = content_div.get_text(separator="\n").strip()
        
        return {
            "id": f"ART-{article_num}",
            "type": "article",
            "number": article_num,
            "title": title,
            "text": text,
            "url": url
        }
    except Exception as e:
        print(f"Error fetching Article {article_num}: {e}")
        return None

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        
    data = []
    
    print("Starting GDPR Extraction...")
    
    # Fetch Articles 1 to 99
    for i in range(1, 100):
        print(f"Fetching Article {i}...")
        article = fetch_article(i)
        if article:
            data.append(article)
        time.sleep(0.2) # Be polite to the server
        
    # Save to JSON
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    print(f"Successfully saved {len(data)} items to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
