import os
import re
import feedparser
from google import genai

# List your RSS feeds here for Tech & Ouro (Markets, Crypto, Tech/Business)
# Using highly reliable Google News RSS queries to get fresh news from the best global sources
RSS_FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", # WSJ Markets
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml", # WSJ World News
    "https://news.google.com/rss/search?q=when:24h+source:reuters&hl=en-US&gl=US&ceid=US:en", # Reuters Global
    "https://news.google.com/rss/search?q=when:24h+source:bloomberg&hl=en-US&gl=US&ceid=US:en", # Bloomberg Markets
    "https://news.google.com/rss/search?q=when:24h+source:financial+times&hl=en-US&gl=US&ceid=US:en" # Financial Times
]

# The file we are going to update
HTML_FILE = "noticias.html"

def get_existing_links():
    """Lê o ficheiro noticias.html e extrai os links das notícias já publicadas (Cache)."""
    if not os.path.exists(HTML_FILE):
        return set()
    
    try:
        with open(HTML_FILE, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Procura por todos os títulos ou descrições para evitar duplicados
        titles = set(re.findall(r'<h2 class="card-title">.*?<span lang="pt">(.*?)</span>', content, re.DOTALL))
        return titles
    except Exception as e:
        print(f"Error reading cache: {e}")
        return set()

def fetch_news():
    print("Fetching fresh news from RSS feeds...")
    articles = []
    
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:8]: # Puxa os 8 mais recentes de cada feed
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            articles.append(f"Title: {title}\nSummary: {summary}\n---")
    
    return "\n".join(articles)

def generate_ai_news(news_text):
    print("Sending news to Gemini AI for analysis...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set!")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert financial and tech news editor for a premium Portuguese/English news site called 'Tech & Ouro'.
    Read the following recent news articles and select the 6 to 8 most important and impactful ones for our readers (investors, tech enthusiasts).
    
    For each of the selected articles, generate the following HTML snippet (make sure the category, title, description, and internal link are fully translated into both Portuguese and English using span tags with lang="pt" and lang="en" attributes):
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
                <a href="INTERNAL_LINK" style="color: inherit; text-decoration: none;">
                    <span lang="pt">VER ANÁLISE →</span>
                    <span lang="en">VIEW ANALYSIS →</span>
                </a>
            </span>
        </div>
    </div>
    
    CRITICAL INSTRUCTION FOR INTERNAL_LINK:
    Do NOT link to external websites. The 'INTERNAL_LINK' must be exactly one of the following local files based on the category of the news:
    - 'economia.html' (if category is Economia/Economy)
    - 'mercados.html' (if category is Mercados/Markets)
    - 'ouro.html' (if category is Ouro/Gold)
    - 'ouro.html#bitcoin' (if category is Bitcoin/Crypto)
    - 'desporto.html' (if category is Desporto/Sports)
    - 'tech.html' (if category is Tech/Tecnologia)
    - 'geopolitica.html' (if category is Geopolítica/Geopolitics)
    - 'index.html' (if general or no other category fits)
    
    Return ONLY the HTML code for the 6 to 8 articles. Do not wrap it in markdown code blocks.
    
    Here is the raw articles:
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
            print("Could not find the marker in the HTML file!")
            return
            
        updated_content = re.sub(pattern, r"\1\n" + new_html + r"\n\3", content, flags=re.DOTALL)
        
        with open(HTML_FILE, "w", encoding="utf-8") as f:
            f.write(updated_content)
            
        print("Successfully updated the news!")
        
    except Exception as e:
        print(f"Error updating file: {e}")

if __name__ == "__main__":
    try:
        raw_news = fetch_news()
        if not raw_news.strip():
            print("No new articles found.")
            exit()
            
        ai_html = generate_ai_news(raw_news)
        update_html_file(ai_html)
    except Exception as e:
        print(f"Failed to update news: {e}")
