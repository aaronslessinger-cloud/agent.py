import os
import smtplib
import cloudscraper
from bs4 import BeautifulSoup
from email.mime.text import MIMEText

# Secure variables
APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
SENDER_EMAIL = "aaronslessingeragent@gmail.com"
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

def get_listings():
    print("Equipping anti-bot stealth. Fetching live Cars.com inventory...")
    
    # The Magic URL: Pre-filtered for 2023+ Lexus ES 350 Ultra Luxury, Black Interior, Max $52k
    url = "https://www.cars.com/shopping/results/?interior_colors[]=black&list_price_max=52000&makes[]=lexus&maximum_distance=all&models[]=lexus-es_350&trims[]=lexus-es_350-ultra_luxury&year_min=2023&zip=98607"
    
    # Cloudscraper mimics a real Chrome browser on a Windows desktop to bypass security
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'desktop': True
    })
    
    listings = []
    try:
        # Increased timeout to 30 seconds to allow the invisible security handshake
        response = scraper.get(url, timeout=30)
        if response.status_code != 200:
            print(f"Error: Cars.com returned status code {response.status_code}")
            return listings
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find all vehicle cards on the page
        vehicle_cards = soup.find_all('div', class_='vehicle-card')
        print(f"Scraped {len(vehicle_cards)} raw listings from the live page.")
        
        for card in vehicle_cards:
            link_tag = card.find('a', class_='vehicle-card-link')
            url_suffix = link_tag['href'] if link_tag else None
            if not url_suffix:
                continue
                
            full_url = f"https://www.cars.com{url_suffix}"
            
            title_tag = card.find('h2', class_='title')
            title = title_tag.text.strip() if title_tag else "Lexus ES 350"
            
            price_tag = card.find('span', class_='primary-price')
            price = price_tag.text.strip() if price_tag else "Price not listed"
            
            listings.append({
                "title": title,
                "price": price,
                "url": full_url
            })
    except Exception as e:
        print(f"Scraping failed: {e}")
        
    return listings

def send_email_alert(listings):
    email_body = f"Your agent found {len(listings)} LIVE matching Lexus ES350s!\n\n"
    
    for car in listings:
        email_body += f"- {car['title']}\n"
        email_body += f"  Price: {car['price']}\n"
        email_body += f"  Link: {car['url']}\n\n"
        
    msg = MIMEText(email_body)
    msg['Subject'] = f'Agent Alert: {len(listings)} LIVE Lexus Matches Found'
    msg['From'] = SENDER_EMAIL
    msg['To'] = TARGET_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print("Alert successfully sent to Hotmail!")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    listings = get_listings()
    
    if len(listings) > 0:
        print(f"Perfect Match(es) found! Emailing {len(listings)} links...")
        send_email_alert(listings)
    else:
        print("No cars matched your strict criteria today.")

if __name__ == "__main__":
    main()
    
