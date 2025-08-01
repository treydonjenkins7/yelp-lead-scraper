import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup

# ---------- Business Categories & Cities ----------

industries = [
    "barber", "auto repair", "cleaning service", "personal trainer",
    "cafe", "towing", "hvac", "electrician", "landscaping", "tattoo"
]

cities = [
    "Boston, MA", "New York, NY", "Los Angeles, CA", "Chicago, IL",
    "Houston, TX", "Phoenix, AZ", "Philadelphia, PA", "San Antonio, TX",
    "San Diego, CA", "Dallas, TX", "San Jose, CA", "Austin, TX",
    "Jacksonville, FL", "Fort Worth, TX", "Columbus, OH", "Charlotte, NC",
    "San Francisco, CA", "Indianapolis, IN", "Seattle, WA", "Denver, CO", "Miami, FL"
]

# ---------- Scraper Function ----------

def scrape_yelp(industry, city, max_pages=3):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    leads = []
    base_url = "https://www.yelp.com/search"
    city_encoded = city.replace(", ", "%2C+").replace(" ", "+")

    for page in range(0, max_pages * 10, 10):
        url = f"{base_url}?find_desc={industry.replace(' ', '+')}&find_loc={city_encoded}&start={page}"
        res = requests.get(url, headers=headers)
        soup = BeautifulSoup(res.text, "html.parser")

        listings = soup.find_all("div", {"class": "container__09f24__21w3G"})

        for listing in listings:
            try:
                name_tag = listing.find("a", {"class": "css-19v1rkv"})
                phone_tag = listing.find("p", {"class": "css-8jxw1i"})

                name = name_tag.text.strip() if name_tag else None
                phone = phone_tag.text.strip() if phone_tag else None

                if name and phone:
                    leads.append({
                        "Name": name,
                        "Phone": phone,
                        "City": city
                    })

            except:
                continue

    return pd.DataFrame(leads)

# ---------- Streamlit UI ----------

st.title("📞 Local Lead Scraper (Yelp Edition)")

industry = st.selectbox("Select Industry", industries)
city = st.selectbox("Select City", cities)

if st.button("Start Scraping"):
    with st.spinner("Scraping Yelp..."):
        df = scrape_yelp(industry, city)
        st.success(f"Found {len(df)} leads with phone numbers!")

        if len(df) > 0:
            st.dataframe(df)
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download CSV", csv, f"{industry}_{city}_leads.csv", "text/csv")
