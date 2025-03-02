"""
    Divar Scraper.
"""

import requests
from bs4 import BeautifulSoup
from pprint import pprint

# from database.models import SessionLocal, Ad
from config import config
import time


def scrape_divar():
    response = requests.get(config.BASE_URL)
    if response.status_code != 200:
        print("خطا در دریافت داده‌ها")
        return

    soup = BeautifulSoup(response.text, "lxml")
    ads = soup.find_all("div", class_="kt-post-card__body")

    # session = SessionLocal()
    for ad in ads:
        title = ad.find("h2").text if ad.find("h2") else "بدون عنوان"
        price = (
            ad.find("div", class_="kt-post-card__description").text
            if ad.find("div", class_="kt-post-card__description")
            else "نامشخص"
        )
        url = ad.find_parent("a")["href"] if ad.find_parent("a") else "#"

        # new_ad = Ad(title=title, price=price, url=f"https://divar.ir{url}")
        pprint(f"title: {title}, price: {price}, url: https://divar.ir{url} ")
    #     session.add(new_ad)

    # session.commit()
    # session.close()


if __name__ == "__main__":
    scrape_divar()
