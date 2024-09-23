from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import time

app = Flask(__name__)

# Function to search for the most probable website URL based on the name
def find_website(name):
    try:
        # Use a search engine API to find the most relevant website based on the input name
        search_url = f"https://www.google.com/search?q={name}+official+website"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the first link in the search results that appears to be a website
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'url?q=' in href and 'webcache' not in href:
                probable_url = href.split('url?q=')[1].split('&')[0]
                return probable_url
        return None
    except Exception as e:
        print(f"Error finding website: {e}")
        return None

def scrape_contact_info(url):
    try:
        start_time = time.time()
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract contact information
        contact_info = extract_contact_info(soup)
        location = extract_location(soup)
        role = extract_role(soup)

        # Measure the time taken for scraping
        end_time = time.time()
        scrape_duration = end_time - start_time

        return {
            'contact_info': contact_info if contact_info else 'Not found',
            'location': location if location else 'Not found',
            'role': role if role else 'Not found',
            'time_taken': f"{scrape_duration:.2f} seconds"
        }

    except Exception as e:
        return {'error': f"An error occurred while scraping: {e}"}

def extract_contact_info(soup):
    contact_info = []
    emails = soup.find_all(string=lambda text: '@' in text)
    contact_info.extend([email.strip() for email in emails if email.strip()])
    phones = soup.find_all(string=lambda text: text and ('phone' in text.lower() or 'contact' in text.lower()))
    contact_info.extend([phone.strip() for phone in phones if phone.strip()])
    return ', '.join(contact_info) if contact_info else None

def extract_location(soup):
    locations = soup.find_all('p', string=lambda text: 'address' in text.lower() or 'location' in text.lower())
    return ', '.join([loc.get_text(strip=True) for loc in locations]) if locations else None

def extract_role(soup):
    roles = soup.find_all(['h1', 'h2', 'p'], string=lambda text: 'about' in text.lower() or 'services' in text.lower() or 'what we do' in text.lower())
    return ', '.join([role.get_text(strip=True) for role in roles]) if roles else None

@app.route('/', methods=['GET', 'POST'])
def home():
    scraped_data = None
    if request.method == 'POST':
        name = request.form.get('name')
        # Find the most probable URL based on the input name
        probable_url = find_website(name)
        if probable_url:
            scraped_data = scrape_contact_info(probable_url)
        else:
            scraped_data = {'error': 'Could not find a relevant website for the given name.'}
    return render_template('index.html', scraped_data=scraped_data)

if __name__ == "__main__":
    app.run(debug=True)
