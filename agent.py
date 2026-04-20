import os
import smtplib
from email.mime.text import MIMEText
from apify_client import ApifyClient

# Secure variables
APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
SENDER_EMAIL = "aaronslessingeragent@gmail.com"
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")
APIFY_TOKEN = os.environ.get("APIFY_API_TOKEN")

def get_listings():
    print("Waking up Apify to scrape live Cars.com listings...")
    client = ApifyClient(APIFY_TOKEN)
    
    # The exact search URL for 2023+ Lexus ES350 under $52k, nationwide
    search_url = "https://www.cars.com/shopping/results/?makes[]=lexus&models[]=lexus-es_350&maximum_distance=all&zip=98607&year_min=2023&list_price_max=52000"
    
    run_input = {
        "startUrls": [{"url": search_url}]
    }
    
    # Triggering the scraper
    print("Scraping in progress. This may take a minute or two...")
    run = client.actor("voyn/cars-scraper").call(run_input=run_input)
    
    listings = []
    print("Scrape complete. Formatting data...")
    # Read the data Apify hands back
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        listings.append({
            "vin": item.get("vin", "Unknown"),
            "year": int(item.get("year", 0)) if item.get("year") else 0,
            "trim": str(item.get("trim", "")),
            "interior": str(item.get("interior_color", "")),
            "price": int(item.get("price", 999999)) if item.get("price") else 999999,
            "url": item.get("list_url", "") or item.get("url", "")
        })
    
    return listings

def evaluate_listing(listing):
    # The Agent's Brain: Strict Filtering
    if listing["year"] < 2023: return False
    if "Ultra Luxury" not in listing["trim"]: return False
    if "Black" not in listing["interior"]: return False
    if listing["price"] > 52000: return False
    return True

def send_email_alert(listing):
    email_body = (
        f"Your agent found a live matching Lexus ES350!\n\n"
        f"Year: {listing['year']}\n"
        f"Trim: {listing['trim']}\n"
        f"Interior: {listing['interior']}\n"
        f"Price: ${listing['price']}\n"
        f"VIN: {listing['vin']}\n"
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
            print(f"Alert sent successfully for VIN: {listing['vin']}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    listings = get_listings()
    print(f"Found {len(listings)} total vehicles matching base criteria. Evaluating...")
    
    match_count = 0
    for car in listings:
        if evaluate_listing(car):
            print(f"Perfect Match found! VIN: {car['vin']}")
            send_email_alert(car)
            match_count += 1
            
    if match_count == 0:
        print("No cars matched your strict Ultra Luxury / Black Interior criteria today.")

if __name__ == "__main__":
    main()
