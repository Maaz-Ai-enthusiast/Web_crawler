import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

class SEOCrawler:
    def __init__(self, start_url, max_pages=10):
        self.start_url = start_url
        self.max_pages = max_pages
        self.visited = set()
        self.to_visit = [start_url]
        self.crawled_data = []

    def fetch_page(self, url):
        """Fetches a page and returns its HTML content."""
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (compatible; SEO-Crawler/1.0)'}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_page(self, html, base_url):
        """Parses the HTML and extracts SEO-related data."""
        soup = BeautifulSoup(html, 'html.parser')
        page_data = {'url': base_url, 'title': '', 'meta_description': '', 'h1_tags': [], 'keywords': []}

        # Extract title
        page_data['title'] = soup.title.string if soup.title else 'No title'

        # Extract meta description
        meta_description = soup.find('meta', attrs={'name': 'description'})
        page_data['meta_description'] = meta_description['content'] if meta_description else 'No meta description'

        # Extract H1 tags
        h1_tags = [h1.get_text(strip=True) for h1 in soup.find_all('h1')]
        page_data['h1_tags'] = h1_tags

        # Extract meta keywords (optional as it's less used now)
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            keywords = meta_keywords['content'].split(',')
            page_data['keywords'] = [keyword.strip() for keyword in keywords]

        self.crawled_data.append(page_data)

        # Extract all hyperlinks to continue crawling, but filter disallowed URLs
        links = [urljoin(base_url, a['href']) for a in soup.find_all('a', href=True)]
        allowed_links = [link for link in links if self.is_allowed(link)]
        return allowed_links

    def is_allowed(self, url):
        """Checks if the URL is allowed to be crawled based on W3Schools' robots.txt rules."""
        disallowed_patterns = [
            '/images',
            '/asp/demo_db_edit.asp',
            '.aspx',
            '/code/'
        ]
        return not any(pattern in url for pattern in disallowed_patterns)

    def crawl(self):
        """Main crawling function."""
        count = 0

        while self.to_visit and count < self.max_pages:
            url = self.to_visit.pop(0)
            if url not in self.visited and self.is_allowed(url):
                self.visited.add(url)
                html = self.fetch_page(url)
                
                if html:
                    links = self.parse_page(html, url)
                    self.to_visit.extend(links)
                    count += 1
                    print(f"Crawled: {url}")
                    time.sleep(1)  # Respectful crawling delay

        self.save_to_html()

    def save_to_html(self):
        """Saves crawled data to an HTML file."""
        with open('w3schools_crawled_data.html', 'w', encoding='utf-8') as file:
            file.write(f'''
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta http-equiv="X-UA-Compatible" content="IE=edge">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>SEO Crawler Results</title>
                <link rel="stylesheet" href="styles.css">
            </head>
            <body>
            <div class="main-container">
            ''')

            for data in self.crawled_data:
                file.write(f'''
                <!-- Title Section -->
                <div class="section">
                    <div class="section-title">Title</div>
                    <div class="content">{data['title']}</div>
                </div>

                <!-- Meta Description Section -->
                <div class="section">
                    <div class="section-title">Meta Description</div>
                    <div class="content">{data['meta_description']}</div>
                </div>

                <!-- H1 Tags Section -->
                <div class="section">
                    <div class="section-title">H1 Tags</div>
                    <div class="content">
                        <ul>
                ''')
                for h1 in data['h1_tags']:
                    file.write(f'<li>{h1}</li>')
                file.write('''
                        </ul>
                    </div>
                </div>

                <!-- Keywords Section -->
                <div class="section">
                    <div class="section-title">Keywords</div>
                    <div class="content">
                ''')
                file.write(', '.join(data['keywords']) if data['keywords'] else 'No keywords')
                file.write('''
                    </div>
                </div>
                ''')

            file.write('''
            </div>
            </body>
            </html>
            ''')

if __name__ == "__main__":
    start_url = "https://www.w3schools.com/"  # W3Schools starting URL
    crawler = SEOCrawler(start_url, max_pages=10)  # Adjust max_pages as needed
    crawler.crawl()
