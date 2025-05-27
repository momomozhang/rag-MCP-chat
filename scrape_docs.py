import requests
from bs4 import BeautifulSoup
import os
import time
import json
from urllib.parse import urljoin, urlparse
import html2text

class MCPDocScraper:
    def __init__(self, base_url="https://modelcontextprotocol.io/docs"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        self.visited_urls = set()
        self.h2t = html2text.HTML2Text()
        self.h2t.ignore_links = False
        
    def create_output_dir(self):
        """Create directory structure for scraped content"""
        if not os.path.exists('mcp_docs'):
            os.makedirs('mcp_docs')
        if not os.path.exists('mcp_docs/markdown'):
            os.makedirs('mcp_docs/markdown')
        if not os.path.exists('mcp_docs/html'):
            os.makedirs('mcp_docs/html')
            
    def get_page(self, url):
        """Fetch a page with error handling"""
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
            
    def extract_doc_links(self, soup, current_url):
        """Extract all documentation links from the page"""
        links = set()
        
        # Look for navigation links, sidebar links, and content links
        for a in soup.find_all('a', href=True):
            href = a['href']
            full_url = urljoin(current_url, href)
            
            # Only include links that are part of the docs
            if 'modelcontextprotocol.io/docs' in full_url or href.startswith('/docs'):
                # Normalize the URL
                parsed = urlparse(full_url)
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if not clean_url.endswith('/'):
                    clean_url += '/'
                links.add(clean_url)
                
        return links
        
    def save_page(self, url, soup):
        """Save page content in both HTML and Markdown format"""
        # Create filename from URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        if not path_parts[-1]:
            filename = 'index'
        else:
            filename = path_parts[-1]
            
        # Save HTML
        html_path = f"mcp_docs/html/{filename}.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
            
        # Extract main content (adjust selectors based on actual site structure)
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        
        if main_content:
            # Convert to Markdown
            markdown_content = self.h2t.handle(str(main_content))
            
            # Save Markdown
            md_path = f"mcp_docs/markdown/{filename}.md"
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(f"# {filename}\n\n")
                f.write(f"Source: {url}\n\n")
                f.write(markdown_content)
                
        print(f"Saved: {filename}")
        
    def scrape_site(self):
        """Main scraping function"""
        self.create_output_dir()
        
        # Start with the base URL
        urls_to_visit = {self.base_url}
        
        while urls_to_visit:
            current_url = urls_to_visit.pop()
            
            if current_url in self.visited_urls:
                continue
                
            print(f"Scraping: {current_url}")
            self.visited_urls.add(current_url)
            
            # Get the page
            response = self.get_page(current_url)
            if not response:
                continue
                
            soup = BeautifulSoup(response.content, 'lxml')
            
            # Save the page
            self.save_page(current_url, soup)
            
            # Find more documentation links
            new_links = self.extract_doc_links(soup, current_url)
            urls_to_visit.update(new_links - self.visited_urls)
            
            # Be polite - add a small delay
            time.sleep(0.5)
            
        # Save metadata
        metadata = {
            'total_pages': len(self.visited_urls),
            'urls': list(self.visited_urls),
            'base_url': self.base_url
        }
        
        with open('mcp_docs/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"\nScraping complete! Scraped {len(self.visited_urls)} pages.")
        
if __name__ == "__main__":
    scraper = MCPDocScraper()
    scraper.scrape_site()