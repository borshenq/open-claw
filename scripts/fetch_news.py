from tavily import TavilyClient
import os

tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY", "dummy"))

queries = [
    "國內科技新聞 2026 4月",
    "國內軍事新聞 2026 4月"
]

for query in queries:
    print(f"Searching: {query}...")
    try:
        response = tavily.search(query=query, search_depth="advanced")
        for result in response.get("results", [])[:3]:
            print(f"- {result['title']}: {result['url']}")
    except Exception as e:
        print(f"Error for {query}: {e}")
