import os
import json
from google import genai
from google.genai import types

def get_latest_files(dir_path, n=2):
    files = [os.path.join(dir_path, f) for f in os.listdir(dir_path) if f.endswith('.png')]
    files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    return files[:n]

def extract_news_from_image(image_path, source_name):
    print(f"Processing {image_path} from {source_name}...")
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    with open(image_path, "rb") as image_file:
        image_bytes = image_file.read()
        
    part = types.Part.from_bytes(data=image_bytes, mime_type="image/png")
    
    prompt = f"""
    This is a screenshot of a news article from {source_name}.
    Extract the main news story from it and create a short summary in both Portuguese and English.
    Return ONLY a JSON object with the following structure. Do NOT include markdown blocks like ```json. Just the raw JSON.
    {{
        "category": "news",
        "source": "{source_name}",
        "url": "#",
        "title_pt": "...",
        "title_en": "...",
        "summary_pt": "...",
        "summary_en": "...",
        "body_pt": "...",
        "body_en": "..."
    }}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, part]
    )
    
    try:
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3]
        elif text.startswith("```"):
            text = text[3:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error parsing response: {e}")
        print(response.text)
        return None

def main():
    reuters_dir = "/Users/tmss1988/Desktop/conteudos/reuters.txt"
    kitco_dir = "/Users/tmss1988/Desktop/conteudos/kictonews.txt"
    
    reuters_files = get_latest_files(reuters_dir, 1)
    kitco_files = get_latest_files(kitco_dir, 1)
    
    new_articles = []
    
    for f in reuters_files:
        article = extract_news_from_image(f, "Reuters")
        if article:
            new_articles.append(article)
            
    for f in kitco_files:
        article = extract_news_from_image(f, "Kitco News")
        if article:
            new_articles.append(article)
            
    # Load manual-news.json
    json_path = "/Users/tmss1988/Desktop/netfily/conteudos/manual-news.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    data["articles"] = new_articles + data.get("articles", [])
    
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Added {len(new_articles)} new articles to manual-news.json")

if __name__ == "__main__":
    main()
