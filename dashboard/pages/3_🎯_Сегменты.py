"""
Страница "Сегменты" - детальный анализ сегментов A/B/C/U

Сравнение сегментов, основные типы съёмок, прогноз перехода в следующий сегмент.
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

from dashboard.utils import (
    load_segment_stats,
    load_companies_dataframe
)
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Сегменты", page_icon="🎯", layout="wide")

st.title("🎯 Сегментный анализ A/B/C/U")

# ============================================================================
# СРАВНЕНИЕ СЕГМЕНТОВ
# ============================================================================

st.markdown("### 📊 Сравнение сегментов")

try:
    segment_stats = load_segment_stats()

    # Добавляем процентное соотношение
    total_companies = segment_stats['count'].sum()
    segment_stats['percent'] = (segment_stats['count'] / total_companies * 100).round(1)

    # Отображаем таблицу статистики
    col1, col2 = st.columns([2, 1])

    with col1:
        # Форматируем для отображения
        display_stats = segment_stats.copy()
        display_stats['count'] = display_stats['count'].apply(lambda x: f"{x:,}")
        display_stats['percent'] = display_stats['percent'].apply(lambda x: f"{x:.1f}%")
        display_stats['total_ltv'] = display_stats['total_ltv'].apply(lambda x: f"{x:,.0f} ₽")
        display_stats['avg_ltv'] = display_stats['avg_ltv'].apply(lambda x: f"{x:,.0f} ₽")
        display_stats['avg_orders'] = display_stats['avg_orders'].apply(lambda x: f"{x:.1f}")
        display_stats['avg_median'] = display_stats['avg_median'].apply(lambda x: f"{x:.1f}")
        display_stats['avg_mean'] = display_stats['avg_mean'].apply(lambda x: f"{x:.1f}")

        display_stats.columns = [
            'Сегмент',
            'Кол-во',
            'Total LTV',
            'Средний LTV',
            'Средн. заказов',
            'Медиана в год',
            'Среднее в год',
            '% от всех'
        ]

        st.dataframe(display_stats, use_container_width=True, hide_index=True, height=250)

    with col2:
        st.markdown("#### 📝 Критерии сегментации")
        st.markdown("""
        **🔴 Сегмент A** (Премиум):
        - LTV ≥ 100,000 ₽
        - Топовые клиенты

        **🔵 Сегмент B** (Активные):
        - 20,000 ₽ ≤ LTV < 100,000 ₽
        - Стабильные клиенты

        **🟡 Сегмент C** (Средние):
        - 10,000 ₽ ≤ LTV < 20,000 ₽
        - Растущие клиенты

        **🟢 Сегмент U** (Новички):
        - LTV < 10,000 ₽
        - Потенциал роста
        """)

    st.divider()

    # ============================================================================
    # ГРАФИКИ СРАВНЕНИЯ
    # ============================================================================

    st.markdown("### 📈 Визуальное сравнение сегментов")

    col1, col2 = st.columns(2)

    with col1:
        # Барчарт: Средний LTV по сегментам
        fig_avg_ltv = px.bar(
            segment_stats,
            x='segment',
            y='avg_ltv',
            title='Средний LTV по сегментам',
            labels={'segment': 'Сегмент', 'avg_ltv': 'Средний LTV (₽)'},
            color='segment',
            color_discrete_map={
                'A': '#FF6B6B',
                'B': '#4ECDC4',
                'C': '#FFE66D',
                'U': '#95E1D3'
            }
        )
        fig_avg_ltv.update_traces(
            hovertemplate='<b>%{x}</b><br>Средний LTV: %{y:,.0f} ₽<extra></extra>'
        )
        st.plotly_chart(fig_avg_ltv, use_container_width=True)

    with col2:
        # Барчарт: Среднее заказов в год по сегментам
        fig_avg_mean = px.bar(
            segment_stats,
            x='segment',
            y='avg_mean',
            title='Среднее заказов в год по сегментам',
            labels={'segment': 'Сегмент', 'avg_mean': 'Среднее заказов в год'},
            color='segment',
            color_discrete_map={
                'A': '#FF6B6B',
                'B': '#4ECDC4',
                'C': '#FFE66D',
                'U': '#95E1D3'
            }
        )
        fig_avg_mean.update_traces(
            hovertemplate='<b>%{x}</b><br>Среднее заказов в год: %{y:.1f}<extra></extra>'
        )
        st.plotly_chart(fig_avg_mean, use_container_width=True)

    # Барчарт: Total LTV по сегментам (на всю ширину)
    fig_total_ltv = px.bar(
        segment_stats,
        x='segment',
        y='total_ltv',
        title='Total LTV по сегментам',
        labels={'segment': 'Сегмент', 'total_ltv': 'Total LTV (₽)'},
        color='segment',
        color_discrete_map={
            'A': '#FF6B6B',
            'B': '#4ECDC4',
            'C': '#FFE66D',
            'U': '#95E1D3'
        }
    )
    fig_total_ltv.update_traces(
        hovertemplate='<b>%{x}</b><br>Total LTV: %{y:,.0f} ₽<extra></extra>'
    )
    st.plotly_chart(fig_total_ltv, use_container_width=True)

    st.divider()

    # ============================================================================
    # ТИПЫ СЪЁМОК ПО СЕГМЕНТАМ
    # ============================================================================

    st.markdown("### 📸 Топ-5 типов съёмок по сегментам")

    # Загрузить данные по типам съёмок для каждого сегмента
    DB_PATH = ROOT_DIR / "platrum.db"
    DATABASE_URL = f"sqlite:///{DB_PATH}"
    engine = create_engine(DATABASE_URL)

    tabs = st.tabs(['🔴 Сегмент A', '🔵 Сегмент B', '🟡 Сегмент C', '🟢 Сегмент U'])

    segments = ['A', 'B', 'C', 'U']
    colors = ['#FF6B6B', '#4ECDC4', '#FFE66D', '#95E1D3']

    for idx, (tab, segment, color) in enumerate(zip(tabs, segments, colors)):
        with tab:
            query = """
                SELECT
                    primary_shooting_type as shooting_type,
                    COUNT(*) as count,
                    AVG(ltv) as avg_ltv,
                    SUM(orders_count) as total_orders
                FROM bitrix_companies
                WHERE segment = :segment
                  AND primary_shooting_type IS NOT NULL
                  AND primary_shooting_type != ''
                GROUP BY primary_shooting_type
                ORDER BY count DESC
                LIMIT 5
            """

            with engine.connect() as conn:
                df_shooting = pd.read_sql_query(text(query), conn, params={'segment': segment})

            if not df_shooting.empty:
                col1, col2 = st.columns([2, 1])

                with col1:
                    fig = px.bar(
                        df_shooting,
                        x='count',
                        y='shooting_type',
                        orientation='h',
                        title=f'Топ-5 типов съёмок для сегмента {segment}',
                        labels={'count': 'Количество клиентов', 'shooting_type': 'Тип съёмки'},
                        color_discrete_sequence=[color]
                    )
                    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
                    fig.update_traces(
                        hovertemplate='<b>%{y}</b><br>Клиентов: %{x}<extra></extra>'
                    )
                    st.plotly_chart(fig, use_container_width=True)

                with col2:
                    st.markdown("#### 📊 Статистика")
                    st.metric("Клиентов", f"{df_shooting['count'].sum():,}")
                    st.metric("Средний LTV", f"{df_shooting['avg_ltv'].mean():,.0f} ₽")
                    st.metric("Всего заказов", f"{df_shooting['total_orders'].sum():,}")
            else:
                st.warning(f"⚠️ Нет данных по типам съёмок для сегмента {segment}")

    st.divider()

    # ============================================================================
    # ПРОГНОЗ: КТО МОЖЕТ ПЕРЕЙТИ В СЛЕДУЮЩИЙ СЕГМЕНТ
    # ============================================================================

    st.markdown("### 🚀 Прогноз: Клиенты на грани перехода в следующий сегмент")

    st.info("""
    💡 **Логика прогноза**: Клиенты, которые близки к порогу следующего сегмента.

    - **C → B**: LTV от 18,000 до 20,000 ₽ (осталось < 2,000 ₽)
    - **B → A**: LTV от 90,000 до 100,000 ₽ (осталось < 10,000 ₽)
    - **U → C**: LTV от 9,000 до 10,000 ₽ (осталось < 1,000 ₽)
    """)

    col1, col2, col3 = st.columns(3)

    # C → B (18-20K)
    with col1:
        st.markdown("#### 🟡 → 🔵 C → B")
        df_c_to_b = load_companies_dataframe(segment='C', min_ltv=18000, max_ltv=20000, limit=20)
        if not df_c_to_b.empty:
            st.metric("Клиентов на грани", len(df_c_to_b))
            st.dataframe(
                df_c_to_b[['title', 'ltv', 'orders_count']].head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'title': 'Компания',
                    'ltv': st.column_config.NumberColumn('LTV', format="%.0f ₽"),
                    'orders_count': 'Заказов'
                }
            )
        else:
            st.info("Нет клиентов на грани перехода")

    # B → A (90-100K)
    with col2:
        st.markdown("#### 🔵 → 🔴 B → A")
        df_b_to_a = load_companies_dataframe(segment='B', min_ltv=90000, max_ltv=100000, limit=20)
        if not df_b_to_a.empty:
            st.metric("Клиентов на грани", len(df_b_to_a))
            st.dataframe(
                df_b_to_a[['title', 'ltv', 'orders_count']].head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'title': 'Компания',
                    'ltv': st.column_config.NumberColumn('LTV', format="%.0f ₽"),
                    'orders_count': 'Заказов'
                }
            )
        else:
            st.info("Нет клиентов на грани перехода")

    # U → C (9-10K)
    with col3:
        st.markdown("#### 🟢 → 🟡 U → C")
        df_u_to_c = load_companies_dataframe(segment='U', min_ltv=9000, max_ltv=10000, limit=20)
        if not df_u_to_c.empty:
            st.metric("Клиентов на грани", len(df_u_to_c))
            st.dataframe(
                df_u_to_c[['title', 'ltv', 'orders_count']].head(10),
                use_container_width=True,
                hide_index=True,
                column_config={
                    'title': 'Компания',
                    'ltv': st.column_config.NumberColumn('LTV', format="%.0f ₽"),
                    'orders_count': 'Заказов'
                }
            )
        else:
            st.info("Нет клиентов на грани перехода")

except Exception as e:
    st.error(f"❌ Ошибка загрузки данных: {e}")
    st.exception(e)
