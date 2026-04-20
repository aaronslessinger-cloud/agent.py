import os
import re
import smtplib
from email.mime.text import MIMEText
from duckduckgo_search import DDGS

# Secure variables
APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
SENDER_EMAIL = "aaronslessingeragent@gmail.com"
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

def get_listings():
    print("Bypassing Apify paywalls. Searching the web directly via DuckDuckGo...")
    
    # We use targeted search operators to pinpoint the exact car on Cars.com
    search_query = 'site:cars.com/vehicledetail "Lexus ES 350" "Ultra Luxury" "Black"'
    
    listings = []
    try:
        # Fetch the top 15 results
        results = DDGS().text(search_query, max_results=15)
        
        print(f"Search complete. Found {len(results)} potential links. Parsing data...")
        for result in results:
            # Combine the title and the snippet text to search for price and year
            text_blob = result.get('title', '') + " " + result.get('body', '')
            
            # Extract Year (Looking for 2023, 2024, or 2025)
            year_match = re.search(r'(202[3-5])', text_blob)
            year = int(year_match.group(1)) if year_match else 0
            
            # Extract Price (Looking for $xx,xxx)
            price_match = re.search(r'\$(\d{2},\d{3})', text_blob)
            price = int(price_match.group(1).replace(',', '')) if price_match else 999999
            
            listings.append({
                "year": year,
                "price": price,
                "url": result.get('href', '')
            })
    except Exception as e:
        print(f"Search failed: {e}")
        
    return listings

def evaluate_listing(listing):
    # The Agent's Brain: Strict Filtering
    if listing["year"] < 2023: return False
    if listing["price"] > 52000: return False
    # We already filtered for the Ultra Luxury trim and Black interior in the search query itself!
    return True

def send_email_alert(listing):
    email_body = (
        f"Your agent found a live matching Lexus ES350!\n\n"
        f"Year: {listing['year']}\n"
        f"Price: ${listing['price']}\n"
        f"Link: {listing['url']}"
    )
    msg = MIMEText(email_body)
    msg['Subject'] = 'Agent Alert: LIVE Lexus ES350 Match'
    msg['From'] = SENDER_EMAIL
    msg['To'] = TARGET_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print(f"Alert sent successfully for: {listing['url']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    listings = get_listings()
    
    match_count = 0
    for car in listings:
        if evaluate_listing(car):
            print(f"Perfect Match found! Emailing link: {car['url']}")
            send_email_alert(car)
            match_count += 1
            
    if match_count == 0:
        print("No cars matched your strict criteria today.")

if __name__ == "__main__":
    main()
    
