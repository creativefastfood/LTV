"""
Страница "Типы съёмок" - анализ популярности типов съёмок

Популярность, средний чек, тренды роста/падения.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys

# Добавить корневую директорию в PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dashboard.utils import load_shooting_type_stats
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Типы съёмок", page_icon="📸", layout="wide")

st.title("📸 Анализ типов съёмок")

# ============================================================================
# СТАТИСТИКА ПО ТИПАМ СЪЁМОК
# ============================================================================

try:
    shooting_stats = load_shooting_type_stats()

    # Добавляем процент
    total_clients = shooting_stats['count'].sum()
    shooting_stats['percent'] = (shooting_stats['count'] / total_clients * 100).round(1)

    st.markdown("### 📊 Общая статистика")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="📋 Типов съёмок",
            value=len(shooting_stats),
            help="Количество уникальных типов съёмок"
        )

    with col2:
        st.metric(
            label="👥 Клиентов с типом съёмки",
            value=f"{total_clients:,}",
            help="Количество клиентов с указанным типом съёмки"
        )

    with col3:
        avg_clients_per_type = shooting_stats['count'].mean()
        st.metric(
            label="📈 Среднее клиентов на тип",
            value=f"{avg_clients_per_type:.0f}",
            help="Среднее количество клиентов на один тип съёмки"
        )

    with col4:
        total_revenue = shooting_stats['total_ltv'].sum()
        st.metric(
            label="💰 Total LTV",
            value=f"{total_revenue:,.0f} ₽",
            help="Общая сумма LTV всех клиентов с типом съёмки"
        )

    st.divider()

    # ============================================================================
    # ТОП-10 ПО ПОПУЛЯРНОСТИ
    # ============================================================================

    st.markdown("### 🏆 Топ-10 типов съёмок по популярности")

    top_10_shooting = shooting_stats.head(10)

    col1, col2 = st.columns([2, 1])

    with col1:
        fig_top = px.bar(
            top_10_shooting,
            x='count',
            y='shooting_type',
            orientation='h',
            title='Количество клиентов по типам съёмки',
            labels={'count': 'Количество клиентов', 'shooting_type': 'Тип съёмки'},
            color='count',
            color_continuous_scale='Blues',
            text='count'
        )
        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        fig_top.update_traces(
            texttemplate='%{text:,}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Клиентов: %{x:,}<extra></extra>'
        )
        st.plotly_chart(fig_top, use_container_width=True)

    with col2:
        st.markdown("#### 📋 Топ-5 детально")
        top_5 = top_10_shooting.head(5).copy()
        top_5['count'] = top_5['count'].apply(lambda x: f"{x:,}")
        top_5['percent'] = top_5['percent'].apply(lambda x: f"{x:.1f}%")
        top_5['avg_ltv'] = top_5['avg_ltv'].apply(lambda x: f"{x:,.0f} ₽")
        top_5.columns = ['Тип съёмки', 'Клиентов', 'Total LTV', 'Средний LTV', 'Заказов', '%']
        st.dataframe(
            top_5[['Тип съёмки', 'Клиентов', '%']],
            use_container_width=True,
            hide_index=True,
            height=250
        )

    st.divider()

    # ============================================================================
    # СРЕДНИЙ ЧЕК ПО ТИПАМ СЪЁМОК
    # ============================================================================

    st.markdown("### 💰 Топ-10 типов съёмок по среднему чеку")

    top_10_avg_ltv = shooting_stats.sort_values('avg_ltv', ascending=False).head(10)

    fig_avg_ltv = px.bar(
        top_10_avg_ltv,
        x='avg_ltv',
        y='shooting_type',
        orientation='h',
        title='Средний LTV по типам съёмки',
        labels={'avg_ltv': 'Средний LTV (₽)', 'shooting_type': 'Тип съёмки'},
        color='avg_ltv',
        color_continuous_scale='Greens',
        text='avg_ltv'
    )
    fig_avg_ltv.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig_avg_ltv.update_traces(
        texttemplate='%{text:,.0f} ₽',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Средний LTV: %{x:,.0f} ₽<extra></extra>'
    )
    st.plotly_chart(fig_avg_ltv, use_container_width=True)

    st.divider()

    # ============================================================================
    # ВСЕГО ЗАКАЗОВ ПО ТИПАМ СЪЁМОК
    # ============================================================================

    st.markdown("### 📦 Топ-10 типов съёмок по количеству заказов")

    top_10_orders = shooting_stats.sort_values('total_orders', ascending=False).head(10)

    fig_orders = px.bar(
        top_10_orders,
        x='total_orders',
        y='shooting_type',
        orientation='h',
        title='Всего заказов по типам съёмки',
        labels={'total_orders': 'Всего заказов', 'shooting_type': 'Тип съёмки'},
        color='total_orders',
        color_continuous_scale='Oranges',
        text='total_orders'
    )
    fig_orders.update_layout(yaxis={'categoryorder': 'total ascending'})
    fig_orders.update_traces(
        texttemplate='%{text:,}',
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Заказов: %{x:,}<extra></extra>'
    )
    st.plotly_chart(fig_orders, use_container_width=True)

    st.divider()

    # ============================================================================
    # ПОЛНАЯ ТАБЛИЦА ВСЕХ ТИПОВ СЪЁМОК
    # ============================================================================

    st.markdown("### 📋 Все типы съёмок (детальная статистика)")

    # Фильтр: минимальное количество клиентов
    min_clients = st.slider(
        "Показать типы съёмок с минимум N клиентов",
        min_value=1,
        max_value=100,
        value=10,
        step=5,
        help="Фильтровать типы съёмок по минимальному количеству клиентов"
    )

    filtered_stats = shooting_stats[shooting_stats['count'] >= min_clients].copy()

    st.info(f"📊 Показано **{len(filtered_stats)}** типов съёмок (из {len(shooting_stats)} всего)")

    # Форматирование для отображения
    display_stats = filtered_stats.copy()
    display_stats['count'] = display_stats['count'].apply(lambda x: f"{x:,}")
    display_stats['total_ltv'] = display_stats['total_ltv'].apply(lambda x: f"{x:,.0f} ₽")
    display_stats['avg_ltv'] = display_stats['avg_ltv'].apply(lambda x: f"{x:,.0f} ₽")
    display_stats['total_orders'] = display_stats['total_orders'].apply(lambda x: f"{x:,}")
    display_stats['percent'] = display_stats['percent'].apply(lambda x: f"{x:.1f}%")

    display_stats.columns = [
        'Тип съёмки',
        'Клиентов',
        'Total LTV',
        'Средний LTV',
        'Всего заказов',
        '% от всех'
    ]

    st.dataframe(
        display_stats,
        use_container_width=True,
        hide_index=True,
        height=600
    )

    st.divider()

    # ============================================================================
    # РАСПРЕДЕЛЕНИЕ КЛИЕНТОВ ПО СЕГМЕНТАМ ДЛЯ ВЫБРАННОГО ТИПА СЪЁМКИ
    # ============================================================================

    st.markdown("### 🎯 Распределение по сегментам для выбранного типа съёмки")

    selected_type = st.selectbox(
        "Выберите тип съёмки",
        shooting_stats['shooting_type'].tolist(),
        help="Выберите тип съёмки для анализа распределения по сегментам"
    )

    if selected_type:
        DB_PATH = ROOT_DIR / "platrum.db"
        DATABASE_URL = f"sqlite:///{DB_PATH}"
        engine = create_engine(DATABASE_URL)

        query = """
            SELECT
                segment,
                COUNT(*) as count,
                AVG(ltv) as avg_ltv,
                SUM(orders_count) as total_orders
            FROM bitrix_companies
            WHERE primary_shooting_type = :shooting_type
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
            df_segments = pd.read_sql_query(text(query), conn, params={'shooting_type': selected_type})

        if not df_segments.empty:
            col1, col2 = st.columns([1, 1])

            with col1:
                # Круговая диаграмма
                fig_pie = px.pie(
                    df_segments,
                    values='count',
                    names='segment',
                    title=f'Распределение клиентов по сегментам: {selected_type}',
                    color='segment',
                    color_discrete_map={
                        'A': '#FF6B6B',
                        'B': '#4ECDC4',
                        'C': '#FFE66D',
                        'U': '#95E1D3'
                    },
                    hole=0.4
                )
                fig_pie.update_traces(
                    textposition='inside',
                    textinfo='percent+label+value',
                    hovertemplate='<b>%{label}</b><br>Клиентов: %{value}<br>Процент: %{percent}<extra></extra>'
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                # Таблица статистики
                st.markdown("#### 📊 Статистика по сегментам")
                display_segments = df_segments.copy()
                display_segments['count'] = display_segments['count'].apply(lambda x: f"{x:,}")
                display_segments['avg_ltv'] = display_segments['avg_ltv'].apply(lambda x: f"{x:,.0f} ₽")
                display_segments['total_orders'] = display_segments['total_orders'].apply(lambda x: f"{x:,}")
                display_segments.columns = ['Сегмент', 'Клиентов', 'Средний LTV', 'Всего заказов']
                st.dataframe(display_segments, use_container_width=True, hide_index=True, height=250)

                # Итого
                st.metric(
                    "Всего клиентов",
                    f"{df_segments['count'].sum():,}",
                    help=f"Общее количество клиентов с типом съёмки '{selected_type}'"
                )
        else:
            st.warning(f"⚠️ Нет данных для типа съёмки: {selected_type}")

except Exception as e:
    st.error(f"❌ Ошибка загрузки данных: {e}")
    st.exception(e)
