import os
import re
import feedparser
from google import genai

# List your RSS feeds here. You can add as many as you want!
RSS_FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", # WSJ Markets
    "https://www.coindesk.com/arc/outboundfeeds/rss/", # CoinDesk
    "https://feeds.bbci.co.uk/news/business/rss.xml" # BBC Business
]

# The file we are going to update
# Path is relative to the root of the repository
HTML_FILE = "noticias.html"

def fetch_news():
    print("Fetching news from RSS feeds...")
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:5]: # Get top 5 from each feed
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            link = entry.get("link", "")
            articles.append(f"Title: {title}\nSummary: {summary}\nLink: {link}\n---")
    
    return "\n".join(articles)

def generate_ai_news(news_text):
    print("Sending news to Gemini AI for analysis...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set!")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert financial and tech news editor for a premium Portuguese/English news site called 'Tech & Ouro'.
    Read the following recent news articles and pick the 5 most important and impactful ones for our readers (investors, tech enthusiasts).
    
    For each of the 5 chosen articles, generate the following HTML snippet (make sure the category, title, description, and source link are fully translated into both Portuguese and English using span tags with lang="pt" and lang="en" attributes):
    <div class="card">
        <div>
            <p class="card-cat">
                <span lang="pt">Categoria em Português</span>
                <span lang="en">Category in English</span>
            </p>
            <h2 class="card-title">
                <span lang="pt">A catchy Portuguese title here</span>
                <span lang="en">A catchy English title here</span>
            </h2>
            <p class="card-desc">
                <span lang="pt">A short, engaging 2-sentence summary in Portuguese.</span>
                <span lang="en">A short, engaging 2-sentence summary in English.</span>
            </p>
        </div>
        <div class="card-meta">
            <span>
                <span lang="pt">HOJE</span>
                <span lang="en">TODAY</span>
            </span>
            <span>
                <a href="LINK_HERE" target="_blank" style="color: inherit; text-decoration: none;">
                    <span lang="pt">LER FONTE ORIGINAL →</span>
                    <span lang="en">READ ORIGINAL SOURCE →</span>
                </a>
            </span>
        </div>
    </div>
    
    Return ONLY the HTML code for the 5 articles. Do not wrap it in markdown code blocks.
    
    Here are the raw articles:
    {news_text}
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
    )
    
    return response.text.strip()

def update_html_file(new_html):
    print(f"Updating {HTML_FILE}...")
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
            
        # We look for the special marker in the HTML
        pattern = r"(<!-- AI_NEWS_START -->)(.*?)(<!-- AI_NEWS_END -->)"
        
        if not re.search(pattern, content, re.DOTALL):
            print("Could not find the <!-- AI_NEWS_START --> marker in the HTML file!")
            return
            
        updated_content = re.sub(pattern, rf"\1\n{new_html}\n\3", content, flags=re.DOTALL)
        
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        print("Successfully updated the news!")
        
    except Exception as e:
        print(f"Error updating file: {e}")

if __name__ == "__main__":
    try:
        raw_news = fetch_news()
        if not raw_news:
            print("No news found from feeds.")
            exit()
            
        ai_html = generate_ai_news(raw_news)
        update_html_file(ai_html)
    except Exception as e:
        print(f"Failed to update news: {e}")
