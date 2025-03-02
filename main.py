from scrapers.divar_scraper import scrape_divar
from scrapers.selenium_scraper import scrape_divar as selenium_scrape
from database import init_db
import os


def check_db_initialized():
    # بررسی وجود فایل دیتابیس
    if not os.path.exists("divar.db"):  # نام دیتابیس را با نام واقعی جایگزین کنید
        return False
    return True


if __name__ == "__main__":
    if not check_db_initialized():
        print("🔧 Initializing database...")
        init_db()

    print("🚀 Starting scraping...")
    selenium_scrape()
    print("✅ Done!")
