import urllib.request, json, urllib.parse

queries = ['科技新聞', '軍事新聞']

for q in queries:
    url = f"http://localhost:8888/search?q={urllib.parse.quote(q)}&format=json&time_range=day"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
            print(f"--- {q} ---")
            for item in data.get('results', [])[:5]:
                print(f"Title: {item.get('title')}\nURL: {item.get('url')}\nContent: {item.get('content')}\n")
    except Exception as e:
        print(f"Error fetching {q}: {e}")
