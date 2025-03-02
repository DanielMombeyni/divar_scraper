import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

# بارگذاری متغیرهای محیطی از فایل .env
load_dotenv()

# تنظیمات پایگاه داده
DB_URL = os.getenv("DATABASE_URL", "sqlite:///divar.db")

# تنظیمات وب‌اسکرپر
BASE_URL = os.getenv("BASE_URL", "https://divar.ir/s/tehran")


def get_engine():
    """ایجاد موتور پایگاه داده بر اساس مقدار تنظیمات"""
    return create_engine(DB_URL, echo=True)
