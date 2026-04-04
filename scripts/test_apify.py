import os
from apify_client import ApifyClient

# 使用你提供的 API 金鑰
token = "apify_api_4PbdSReSfvIyi1mlbIOWlxugxTDsWW2WID7e"
client = ApifyClient(token)

# 測試呼叫一個公共爬蟲 (例如 Google Search)
run_input = {
    "queries": "最新科技新聞 2026",
    "maxPagesPerQuery": 1,
}

print("Starting Google Search scraper...")
try:
    run = client.actor("apify/google-search-scraper").call(run_input=run_input)
    
    # 獲取結果
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        print(f"- {item.get('title')}: {item.get('url')}")
except Exception as e:
    print(f"Error: {e}")
