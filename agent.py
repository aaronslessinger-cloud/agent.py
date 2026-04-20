import os
import smtplib
from email.mime.text import MIMEText

# Pull secure variables from GitHub Secrets
APP_PASSWORD = os.environ.get("EMAIL_APP_PASSWORD")
SENDER_EMAIL = "aaronslessingeragent@gmail.com"
TARGET_EMAIL = os.environ.get("TARGET_EMAIL")

def get_listings():
    # In a fully deployed version, this is where you call the Apify API 
    # to scrape CarGurus, Autotrader, etc.
    # For now, we are simulating a found match.
    print("Scraping nationwide listings for 2023+ Lexus ES350...")
    
    # Simulated mock data returned from the scraper
    mock_listings = [
        {
            "vin": "JTH123456789",
            "year": 2024,
            "trim": "Ultra Luxury",
            "interior": "Black",
            "price": 49500,
            "url": "https://www.example-car-listing.com/lexus-es350"
        }
    ]
    return mock_listings

def evaluate_listing(listing):
    # The Agent's Brain: Strict Filtering
    if listing["year"] < 2023: return False
    if listing["trim"] != "Ultra Luxury": return False
    if listing["interior"] != "Black": return False
    if listing["price"] > 52000: return False
    return True

def send_email_alert(listing):
    email_body = (
        f"Your agent found a matching Lexus ES350!\n\n"
        f"Year: {listing['year']}\n"
        f"Trim: {listing['trim']}\n"
        f"Interior: {listing['interior']}\n"
        f"Price: ${listing['price']}\n"
        f"Link: {listing['url']}"
    )
    msg = MIMEText(email_body)
    msg['Subject'] = 'Agent Alert: New Lexus ES350 Match'
    msg['From'] = SENDER_EMAIL
    msg['To'] = TARGET_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.send_message(msg)
            print("Alert sent successfully to Hotmail.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def main():
    listings = get_listings()
    for car in listings:
        if evaluate_listing(car):
            print(f"Match found! VIN: {car['vin']}")
            # In a production version, you'd check a database here to ensure 
            # you haven't already emailed about this VIN.
            send_email_alert(car)

if __name__ == "__main__":
    main()
