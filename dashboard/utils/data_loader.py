"""
Data loader для Streamlit dashboard

Загружает данные из SQLite базы данных аналитики клиентов.
"""
import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import Dict, List, Any
import json

# Путь к базе данных
DB_PATH = Path(__file__).parent.parent.parent / "platrum.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Создаём engine для SQLAlchemy
engine = create_engine(DATABASE_URL)


def load_companies_summary() -> Dict[str, Any]:
    """
    Загружает сводную статистику по компаниям.

    Returns:
        Dict с ключевыми метриками
    """
    with engine.connect() as conn:
        # Общая статистика
        result = conn.execute(text("""
            SELECT
                COUNT(*) as total_companies,
                COUNT(CASE WHEN orders_count > 0 THEN 1 END) as companies_with_orders,
                SUM(ltv) as total_ltv,
                AVG(ltv) as avg_ltv,
                SUM(orders_count) as total_orders,
                AVG(orders_count) as avg_orders_per_company,
                COUNT(CASE WHEN primary_shooting_type IS NOT NULL AND primary_shooting_type != '' THEN 1 END) as companies_with_shooting_type
            FROM bitrix_companies
        """)).fetchone()

        total_companies = result[0]
        companies_with_orders = result[1]
        total_ltv = result[2] or 0
        avg_ltv = result[3] or 0
        total_orders = result[4] or 0
        avg_orders_per_company = result[5] or 0
        companies_with_shooting_type = result[6]

        shooting_type_percent = (companies_with_shooting_type / companies_with_orders * 100) if companies_with_orders > 0 else 0

        return {
            "total_companies": total_companies,
            "companies_with_orders": companies_with_orders,
            "total_ltv": total_ltv,
            "avg_ltv": avg_ltv,
            "total_orders": total_orders,
            "avg_orders_per_company": avg_orders_per_company,
            "companies_with_shooting_type": companies_with_shooting_type,
            "shooting_type_percent": shooting_type_percent
        }


def load_companies_dataframe(
    segment: str = None,
    shooting_type: str = None,
    min_ltv: float = None,
    max_ltv: float = None,
    limit: int = None
) -> pd.DataFrame:
    """
    Загружает список компаний с фильтрами.

    Args:
        segment: Фильтр по сегменту (A, B, C, U)
        shooting_type: Фильтр по типу съёмки
        min_ltv: Минимальный LTV
        max_ltv: Максимальный LTV
        limit: Максимальное количество записей

    Returns:
        DataFrame с данными компаний
    """
    query = """
        SELECT
            bitrix_id,
            title,
            ltv,
            segment,
            orders_count,
            orders_count_median,
            orders_count_mean,
            primary_shooting_type
        FROM bitrix_companies
        WHERE orders_count > 0
    """

    params = {}

    if segment:
        query += " AND segment = :segment"
        params["segment"] = segment

    if shooting_type:
        query += " AND primary_shooting_type = :shooting_type"
        params["shooting_type"] = shooting_type

    if min_ltv is not None:
        query += " AND ltv >= :min_ltv"
        params["min_ltv"] = min_ltv

    if max_ltv is not None:
        query += " AND ltv <= :max_ltv"
        params["max_ltv"] = max_ltv

    query += " ORDER BY ltv DESC"

    if limit:
        query += f" LIMIT {limit}"

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn, params=params)

    return df


def load_segment_stats() -> pd.DataFrame:
    """
    Загружает статистику по сегментам A/B/C/U.

    Returns:
        DataFrame с агрегированной статистикой
    """
    query = """
        SELECT
            segment,
            COUNT(*) as count,
            SUM(ltv) as total_ltv,
            AVG(ltv) as avg_ltv,
            AVG(orders_count) as avg_orders,
            AVG(orders_count_median) as avg_median,
            AVG(orders_count_mean) as avg_mean
        FROM bitrix_companies
        WHERE orders_count > 0
        GROUP BY segment
        ORDER BY
            CASE segment
                WHEN 'A' THEN 1
                WHEN 'B' THEN 2
                WHEN 'C' THEN 3
                WHEN 'U' THEN 4
            END
    """

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)

    return df


def load_shooting_type_stats() -> pd.DataFrame:
    """
    Загружает статистику по типам съёмок.

    Returns:
        DataFrame с агрегированной статистикой
    """
    query = """
        SELECT
            primary_shooting_type as shooting_type,
            COUNT(*) as count,
            SUM(ltv) as total_ltv,
            AVG(ltv) as avg_ltv,
            SUM(orders_count) as total_orders
        FROM bitrix_companies
        WHERE orders_count > 0
          AND primary_shooting_type IS NOT NULL
          AND primary_shooting_type != ''
        GROUP BY primary_shooting_type
        ORDER BY count DESC
    """

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)

    return df


def load_ltv_trend() -> pd.DataFrame:
    """
    Загружает тренд LTV по годам (на основе дат закрытия сделок).

    Returns:
        DataFrame с LTV по годам
    """
    query = """
        SELECT
            strftime('%Y', close_date) as year,
            COUNT(DISTINCT company_id) as companies,
            SUM(opportunity) as total_revenue,
            COUNT(*) as deals_count
        FROM bitrix_deals
        WHERE close_date IS NOT NULL
        GROUP BY year
        ORDER BY year
    """

    with engine.connect() as conn:
        df = pd.read_sql_query(text(query), conn)

    return df


def load_top_companies(limit: int = 20) -> List[Dict[str, Any]]:
    """
    Загружает топ N компаний по LTV.

    Args:
        limit: Количество компаний

    Returns:
        Список словарей с данными компаний
    """
    df = load_companies_dataframe(limit=limit)
    return df.to_dict('records')


def search_companies(query: str, limit: int = 50) -> pd.DataFrame:
    """
    Поиск компаний по названию.

    Args:
        query: Поисковый запрос
        limit: Максимальное количество результатов

    Returns:
        DataFrame с результатами поиска
    """
    sql_query = """
        SELECT
            bitrix_id,
            title,
            ltv,
            segment,
            orders_count,
            primary_shooting_type
        FROM bitrix_companies
        WHERE orders_count > 0
          AND (title_normalized LIKE :query OR title LIKE :query)
        ORDER BY ltv DESC
        LIMIT :limit
    """

    params = {
        "query": f"%{query.lower()}%",
        "limit": limit
    }

    with engine.connect() as conn:
        df = pd.read_sql_query(text(sql_query), conn, params=params)

    return df
