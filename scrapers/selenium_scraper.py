# فایل: divar_scraper.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from database import init_db, SessionLocal, Ad
from bs4 import BeautifulSoup
from config import config
from utils import games, provinces_list
from pathlib import Path
import time


# دریافت مسیر chromedriver در پوشه پروژه
BASE_DIR = Path(__file__).resolve().parent
CHROMEDRIVER_PATH = BASE_DIR / "chromedriver" / "chromedriver"


def save_to_db(ads, game_name, province_name):
    """
    ذخیره آگهی‌ها در دیتابیس
    """
    session = SessionLocal()
    for ad in ads:
        try:
            # بررسی وجود آگهی با url مشابه در دیتابیس
            existing_ad = session.query(Ad).filter(Ad.url == ad["url"]).first()
            if existing_ad:
                print(f"⚠️ آگهی با url تکراری یافت شد: {ad['url']}")
                continue  # اگر آگهی وجود دارد، از ذخیره‌سازی مجدد صرف‌نظر کنید

            # ایجاد رکورد جدید
            new_ad = Ad(
                title=ad["title"],
                game=game_name,
                price=ad["price"],
                location=province_name,
                url=ad["url"],
            )
            session.add(new_ad)
            session.commit()
            print(f"✅ آگهی ذخیره شد: {ad['title']}")
        except Exception as e:
            session.rollback()  # اگر خطایی رخ دهد، تغییرات را لغو می‌کند
            print(f"❌ خطا در ذخیره آگهی: {ad['title']} - {e}")
        finally:
            session.close()


def scrape_divar():
    # تنظیمات مرورگر
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-features=NetworkService")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--allow-insecure-localhost")
    chrome_options.add_argument("--incognito")
    # chrome_options.add_argument("--user-data-dir=D:/temp_chrome_user_data")

    # print(f"{CHROMEDRIVER_PATH}.exe")

    chrome_driver_path = r"D:\Files\Project\StartUp\NoName\DataCurl\divar_scraper\chromedriver\chromedriver.exe"
    service = Service(chrome_driver_path)
    # نصب و راه‌اندازی درایور کروم
    # service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # بررسی و ایجاد دیتابیس در صورت نیاز
    init_db()

    # شروع کرولینگ
    for province in provinces_list.iran_provinces:
        print(f"\n🔹 Scraping province: {province['name']}")

        for game in games.games_list:
            search_url = f"{province['url']}?q={game['query']}"
            print(
                f"  🎮 Searching for {game['name']} in {province['name']} - {search_url}"
            )
            driver.get(search_url)
            time.sleep(10)

            # بررسی و کلیک روی دکمه تأیید در صورت وجود
            try:
                confirmation_button = driver.find_element(
                    By.XPATH, "/html/body/div[3]/div/div[2]/footer/button[2]"
                )
                if confirmation_button.is_displayed():
                    print("  ✅ Clicking confirmation button...")
                    confirmation_button.click()
                    time.sleep(5)
            except:
                print("  ❌ No confirmation button found.")

            last_height = driver.execute_script("return document.body.scrollHeight")
            ads_data = []  # لیست برای ذخیره موقت آگهی‌ها

            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(5)

                # بررسی دکمه "بارگذاری بیشتر"
                try:
                    load_more_button = driver.find_element(
                        By.XPATH, '//*[@id="post-list-container-id"]/div[2]/div/button'
                    )
                    if load_more_button.is_displayed():
                        print("  🔄 Clicking 'Load More' button...")
                        load_more_button.click()
                        time.sleep(5)
                except:
                    print("  🚫 No 'Load More' button found.")

                new_height = driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    print(
                        f"  ✅ Finished searching {game['name']} in {province['name']}.\n"
                    )
                    break
                last_height = new_height

                # استخراج آگهی‌ها
                soup = BeautifulSoup(driver.page_source, "lxml")
                ads = soup.find_all("div", class_="kt-post-card__body")

                for ad in ads:
                    title = ad.find("h2").text if ad.find("h2") else "No title"
                    price = (
                        ad.find("div", class_="kt-post-card__description").text
                        if ad.find("div", class_="kt-post-card__description")
                        else "Unknown"
                    )
                    url = ad.find_parent("a")["href"] if ad.find_parent("a") else "#"

                    ads_data.append(
                        {
                            "title": title,
                            "price": price,
                            "url": f"https://divar.ir{url}",
                        }
                    )

                    print(
                        f"    🏷️ title: {title}, 💰 price: {price}, 🔗 url: https://divar.ir{url}"
                    )

                print(
                    f"  🔎 Total ads found for {game['name']} in {province['name']}: {len(ads)}"
                )

            # ذخیره آگهی‌ها در دیتابیس
            save_to_db(ads_data, game["name"], province["name"])

    # بستن مرورگر
    driver.quit()


if __name__ == "__main__":
    scrape_divar()
