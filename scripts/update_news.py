import os
import re
import feedparser
from google import genai

# List your RSS feeds here for Tech & Ouro (Markets, Crypto, Tech/Business)
# Using highly reliable Google News RSS queries to get fresh news from the best global sources
RSS_FEEDS = [
    "https://feeds.a.dj.com/rss/RSSMarketsMain.xml", # WSJ Markets
    "https://feeds.a.dj.com/rss/RSSWorldNews.xml", # WSJ World News
    "https://news.google.com/rss/search?q=when:24h+source:marketwatch&hl=en-US&gl=US&ceid=US:en", # MarketWatch
    "https://news.google.com/rss/search?q=when:24h+source:barrons&hl=en-US&gl=US&ceid=US:en", # Barron's
    "https://news.google.com/rss/search?q=when:24h+source:reuters&hl=en-US&gl=US&ceid=US:en", # Reuters Global
    "https://news.google.com/rss/search?q=when:24h+source:bloomberg&hl=en-US&gl=US&ceid=US:en", # Bloomberg Markets
    "https://news.google.com/rss/search?q=when:24h+source:financial+times&hl=en-US&gl=US&ceid=US:en" # Financial Times
]

# The files we are going to update
HTML_FILES = ["noticias.html", "index.html"]

def get_existing_links():
    """Lê o ficheiro noticias.html e extrai os links das notícias já publicadas (Cache)."""
    if not os.path.exists(HTML_FILES[0]):
        return set()
    
    try:
        with open(HTML_FILES[0], "r", encoding="utf-8") as f:
            content = f.read()
        
        # Procura por todos os títulos ou descrições para evitar duplicados
        titles = set(re.findall(r'<h2 class="card-title">.*?<span lang="pt">(.*?)</span>', content, re.DOTALL))
        return titles
    except Exception as e:
        print(f"Error reading cache: {e}")
        return set()

def extract_text_from_pdf(pdf_path, max_pages=5):
    print(f"Extracting text from PDF: {pdf_path} (max {max_pages} pages)...")
    try:
        import pypdf
        reader = pypdf.PdfReader(pdf_path)
        num_pages = min(len(reader.pages), max_pages)
        text = []
        for i in range(num_pages):
            page_text = reader.pages[i].extract_text()
            if page_text:
                text.append(f"--- Page {i+1} ---\n{page_text}")
        return "\n".join(text)
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

def fetch_news():
    # 1. Check for manual news drafts, PDF files, or screenshots in the conteudos/ directory
    print("Checking for manual news drafts/PDFs/Images in conteudos/...")
    manual_articles = []
    images_parts = []
    conteudos_dir = "conteudos"
    
    if os.path.exists(conteudos_dir):
        for filename in sorted(os.listdir(conteudos_dir)):
            filepath = os.path.join(conteudos_dir, filename)
            # Support PDF files directly!
            if filename.endswith(".pdf"):
                pdf_text = extract_text_from_pdf(filepath, max_pages=5)
                if pdf_text:
                    manual_articles.append(f"Source PDF File: {filename}\nContent:\n{pdf_text}\n---")
            # Support Text files
            elif filename.endswith(".txt"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read().strip()
                    # Skip files that only contain template/placeholder text or are too short
                    if content and "Insere" not in content and "Insert" not in content and len(content) > 50:
                        manual_articles.append(f"Source Text File: {filename}\nContent:\n{content}\n---")
                except Exception as e:
                    print(f"Error reading local file {filename}: {e}")
            # Support Image files (screenshots!)
            elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
                try:
                    from google.genai import types
                    mime_type = "image/png" if filename.lower().endswith(".png") else "image/jpeg"
                    with open(filepath, "rb") as f:
                        img_data = f.read()
                    part = types.Part.from_bytes(data=img_data, mime_type=mime_type)
                    images_parts.append(part)
                    print(f"Loaded screenshot image: {filename}")
                except Exception as e:
                    print(f"Error loading image {filename}: {e}")
                    
    if manual_articles or images_parts:
        print(f"Found {len(manual_articles)} manual news/PDF files and {len(images_parts)} screenshot images. Using them as source.")
        return "\n".join(manual_articles), images_parts
        
    # 2. Fallback to premium RSS feeds if no manual content is found
    print("No manual drafts/images found. Fetching fresh news from RSS feeds...")
    articles = []
    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:8]: # Puxa os 8 mais recentes de cada feed
            title = entry.get("title", "")
            summary = entry.get("summary", "")
            articles.append(f"Title: {title}\nSummary: {summary}\n---")
    
    return "\n".join(articles), []

def generate_ai_news(news_text, images_parts):
    print("Sending news and images to Gemini AI for analysis...")
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set!")
        
    client = genai.Client(api_key=api_key)
    
    prompt = f"""
    You are an expert financial and tech news editor for a premium Portuguese/English news site called 'Tech & Ouro'.
    Read the following recent news articles and screenshots (if any) and select the 6 to 8 most important and impactful ones for our readers (investors, tech enthusiasts).
    
    If there are attached images/screenshots, read their text content and extract the news from them as well.
    
    CRITICAL TRANSLATION INSTRUCTION:
    If the source news text or screenshot is already in English or Portuguese, keep that original text as the source for that language version (refining it slightly for premium tone if needed) and focus on translating the missing language to complete the bilingual card (e.g., if input is in English, keep the English version and translate it to Portuguese, or vice-versa). Both span tags (lang="pt" and lang="en") must be perfectly filled.
    
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
    
    Here is the raw text articles:
    {news_text}
    """
    
    contents = [prompt]
    for part in images_parts:
        contents.append(part)
        
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=contents,
    )
    
    return response.text.strip()

def update_html_files(new_html):
    for html_file in HTML_FILES:
        print(f"Updating {html_file}...")
        try:
            if not os.path.exists(html_file):
                print(f"File {html_file} not found!")
                continue
                
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # We look for the special marker in the HTML
            pattern = r"(<!-- AI_NEWS_START -->)(.*?)(<!-- AI_NEWS_END -->)"
            
            if not re.search(pattern, content, re.DOTALL):
                print(f"Could not find the marker in the HTML file {html_file}!")
                continue
                
            updated_content = re.sub(pattern, r"\1\n" + new_html + r"\n\3", content, flags=re.DOTALL)
            
            with open(html_file, "w", encoding="utf-8") as f:
                f.write(updated_content)
                
            print(f"Successfully updated {html_file}!")
            
        except Exception as e:
            print(f"Error updating file {html_file}: {e}")

if __name__ == "__main__":
    try:
        raw_news, images_parts = fetch_news()
        if not raw_news.strip() and not images_parts:
            print("No new articles or screenshots found.")
            exit()
            
        ai_html = generate_ai_news(raw_news, images_parts)
        update_html_files(ai_html)
    except Exception as e:
        print(f"Failed to update news: {e}")
