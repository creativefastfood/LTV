"""
Генератор демо-данных для LTV Dashboard

Создаёт синтетические данные для демонстрации дашборда на Streamlit Cloud.
"""
import sqlite3
import random
from datetime import datetime, timedelta
from pathlib import Path


def create_demo_database(db_path: str = None):
    """
    Создаёт демо-базу данных с синтетическими данными.

    Args:
        db_path: Путь к файлу базы данных (по умолчанию platrum.db в корне)
    """
    if db_path is None:
        db_path = Path(__file__).parent.parent.parent / "platrum.db"

    print(f"Creating demo database at: {db_path}")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Создаём таблицы
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_companies (
            id INTEGER PRIMARY KEY,
            bitrix_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            ltv REAL DEFAULT 0,
            segment TEXT,
            orders_count INTEGER DEFAULT 0,
            orders_count_median REAL,
            orders_count_mean REAL,
            primary_shooting_type TEXT,
            title_normalized TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bitrix_deals (
            id INTEGER PRIMARY KEY,
            bitrix_id TEXT UNIQUE NOT NULL,
            company_id TEXT,
            title TEXT,
            opportunity REAL,
            close_date TEXT,
            stage TEXT
        )
    """)

    # Генерируем демо-данные
    companies_data = generate_demo_companies(200)
    deals_data = generate_demo_deals(companies_data, 800)

    # Вставляем компании
    cursor.executemany("""
        INSERT OR REPLACE INTO bitrix_companies
        (bitrix_id, title, ltv, segment, orders_count, orders_count_median,
         orders_count_mean, primary_shooting_type, title_normalized)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, companies_data)

    # Вставляем сделки
    cursor.executemany("""
        INSERT OR REPLACE INTO bitrix_deals
        (bitrix_id, company_id, title, opportunity, close_date, stage)
        VALUES (?, ?, ?, ?, ?, ?)
    """, deals_data)

    conn.commit()
    conn.close()

    print(f"✅ Demo database created successfully!")
    print(f"   - {len(companies_data)} companies")
    print(f"   - {len(deals_data)} deals")


def generate_demo_companies(count: int = 200):
    """Генерирует список демо-компаний"""

    # Реалистичные названия компаний
    company_names = [
        "ООО «Альфа»", "ЗАО «Бета»", "ИП Иванов", "ООО «Гамма»", "ООО «Дельта»",
        "ООО «Эпсилон»", "ООО «Зета»", "ООО «Эта»", "ООО «Тета»", "ООО «Йота»",
        "ООО «Каппа»", "ООО «Лямбда»", "ООО «Мю»", "ООО «Ню»", "ООО «Кси»",
        "ООО «Омикрон»", "ООО «Пи»", "ООО «Ро»", "ООО «Сигма»", "ООО «Тау»"
    ]

    # Типы съёмок
    shooting_types = [
        "Предметная", "Каталожная", "Имиджевая", "Интерьерная", "Портретная",
        "Рекламная", "Fashion", "Food-съёмка", "Ювелирная", "Техническая"
    ]

    companies = []

    for i in range(count):
        # Генерируем LTV с распределением по сегментам
        ltv_base = random.choice([
            random.uniform(1000, 9999),     # Сегмент U (40%)
            random.uniform(10000, 19999),    # Сегмент C (30%)
            random.uniform(20000, 99999),    # Сегмент B (25%)
            random.uniform(100000, 500000)   # Сегмент A (5%)
        ])

        ltv = round(ltv_base, 2)

        # Определяем сегмент
        if ltv >= 100000:
            segment = 'A'
        elif ltv >= 20000:
            segment = 'B'
        elif ltv >= 10000:
            segment = 'C'
        else:
            segment = 'U'

        # Количество заказов коррелирует с LTV
        if segment == 'A':
            orders_count = random.randint(20, 50)
        elif segment == 'B':
            orders_count = random.randint(10, 25)
        elif segment == 'C':
            orders_count = random.randint(5, 15)
        else:
            orders_count = random.randint(1, 8)

        # Генерируем название
        if i < len(company_names):
            title = company_names[i]
        else:
            title = f"{random.choice(company_names)} {i + 1}"

        companies.append((
            f"DEMO_{i+1}",                          # bitrix_id
            title,                                   # title
            ltv,                                     # ltv
            segment,                                 # segment
            orders_count,                           # orders_count
            round(orders_count / 2.5, 1),           # orders_count_median
            round(orders_count / 2.0, 1),           # orders_count_mean
            random.choice(shooting_types),          # primary_shooting_type
            title.lower()                           # title_normalized
        ))

    return companies


def generate_demo_deals(companies_data, total_deals: int = 800):
    """Генерирует список демо-сделок"""

    deals = []

    # Распределяем сделки по компаниям
    for i in range(total_deals):
        # Выбираем случайную компанию
        company = random.choice(companies_data)
        company_bitrix_id = company[0]

        # Генерируем сумму сделки (opportunity)
        opportunity = random.uniform(5000, 50000)

        # Генерируем дату закрытия (последние 3 года)
        days_ago = random.randint(0, 1095)  # 3 года
        close_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

        deals.append((
            f"DEAL_{i+1}",          # bitrix_id
            company_bitrix_id,      # company_id
            f"Заказ #{i+1}",        # title
            round(opportunity, 2),  # opportunity
            close_date,             # close_date
            "WON"                   # stage
        ))

    return deals


if __name__ == "__main__":
    # Тест: создаём демо-базу
    create_demo_database()
