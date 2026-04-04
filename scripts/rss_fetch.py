import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse

def fetch_news(topic):
    url = f"https://news.google.com/rss/search?q={urllib.parse.quote(topic)}&hl=zh-TW&gl=TW&ceid=TW:zh-Hant"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            print(f"--- {topic} ---")
            for item in root.findall('./channel/item')[:5]:
                title = item.find('title').text
                link = item.find('link').text
                pubDate = item.find('pubDate').text
                source = item.find('source').text if item.find('source') is not None else 'Google News'
                print(f"Title: {title}")
                print(f"Source: {source} | Time: {pubDate}")
                print(f"URL: {link}\n")
    except Exception as e:
        print(f"Error fetching {topic}: {e}")

fetch_news('科技')
fetch_news('軍事')
