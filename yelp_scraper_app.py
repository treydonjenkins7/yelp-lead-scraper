import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------- Business Categories & Cities ----------
industries = ["barber", "auto repair", "cleaning service", "personal trainer",
              "cafe", "towing", "hvac", "electrician", "landscaping", "tattoo"]

cities = ["Boston, MA", "New York, NY", "Los Angeles, CA", "Chicago, IL",
          "Houston, TX", "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX",
          "San Diego, CA", "Dallas, TX", "San Jose, CA", "Austin, TX",
          "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "Charlotte, NC",
          "San Francisco, CA", "Indianapolis, IN", "Seattle, WA", "Denver, CO"]

# ---------- Scraper Logic ----------
SCRAPER_API_KEY = "4f3e09c8028a06b03f86ba417a9ed8b9"  # Replace with your actual key

def scrape_yellowpages(industry, city, max_pages=1):
    headers = {"User-Agent": "Mozilla/5.0"}
    leads = []

    for page in range(1, max_pages + 1):
        original_url = (f"https://www.yellowpages.com/search"
                        f"?search_terms={industry.replace(' ', '+')}"
                        f"&geo_location_terms={city.replace(' ', '+')}"
                        f"&page={page}")
        
        scraper_url = f"http://api.scraperapi.com/?api_key={SCRAPER_API_KEY}&url={original_url}"
        
        res = requests.get(scraper_url, headers=headers)
        print(f"[DEBUG] Fetched via ScraperAPI: {original_url} | Status: {res.status_code}")

        if res.status_code != 200:
            print("[ERROR] ScraperAPI failed or hit a limit.")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        listings = soup.select("div.result")
        print(f"[DEBUG] Found {len(listings)} business results")

        if listings:
            print("[DEBUG] Sample:\n", listings[0].prettify()[:1000])

        for result in listings:
            try:
                name_tag = result.select_one("a.business-name span")
                phone_tag = result.select_one("div.phones") or result.select_one("div.phone")
                addr_tag = result.select_one("div.adr")

                name = name_tag.text.strip() if name_tag else None
                phone = phone_tag.text.strip() if phone_tag else None
                address = addr_tag.text.strip() if addr_tag else None

                if name and phone:
                    leads.append({
                        "Name": name,
                        "Phone": phone,
                        "Address": address,
                        "City": city
                    })
            except Exception as e:
                print("[DEBUG] Error parsing entry:", e)
                continue

    return pd.DataFrame(leads)

# ---------- Streamlit UI ----------
st.title("📞 Local Lead Scraper (Powered by ScraperAPI)")

industry = st.selectbox("Select Industry", industries)
city = st.selectbox("Select City", cities)

if st.button("Start Scraping"):
    with st.spinner("Scraping via ScraperAPI... please wait"):
        df = scrape_yellowpages(industry, city)
        st.success(f"✅ Found {len(df)} leads!")

        if not df.empty:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, f"{industry}_{city}_leads.csv", "text/csv")
