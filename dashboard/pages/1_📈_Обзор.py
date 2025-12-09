"""
Страница "Обзор" - главная страница дашборда

KPI карточки, круговая диаграмма сегментов, барчарт типов съёмки, таблица топ клиентов, линейный график тренда LTV.
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
    load_companies_summary,
    load_segment_stats,
    load_shooting_type_stats,
    load_top_companies,
    load_ltv_trend
)

st.set_page_config(page_title="Обзор", page_icon="📈", layout="wide")

st.title("📈 Обзор - Ключевые метрики")

# ============================================================================
# KPI КАРТОЧКИ
# ============================================================================

st.markdown("### 📊 Основные показатели")

try:
    summary = load_companies_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="💰 Total LTV",
            value=f"{summary['total_ltv']:,.0f} ₽",
            help="Общая сумма всех заказов (Life Time Value)"
        )

    with col2:
        st.metric(
            label="👥 Клиентов с заказами",
            value=f"{summary['companies_with_orders']:,}",
            delta=f"из {summary['total_companies']:,} всего",
            help="Количество компаний, сделавших хотя бы один заказ"
        )

    with col3:
        st.metric(
            label="📊 Средний LTV",
            value=f"{summary['avg_ltv']:,.0f} ₽",
            help="Средняя сумма заказов на одного клиента"
        )

    with col4:
        st.metric(
            label="📸 Тип съёмки заполнен",
            value=f"{summary['shooting_type_percent']:.1f}%",
            delta=f"{summary['companies_with_shooting_type']:,} клиентов",
            help="Процент клиентов с указанным основным типом съёмки"
        )

    st.divider()

    # ============================================================================
    # КРУГОВАЯ ДИАГРАММА: СЕГМЕНТЫ A/B/C/U
    # ============================================================================

    st.markdown("### 🎯 Распределение по сегментам")

    col_left, col_right = st.columns([1, 1])

    with col_left:
        segment_stats = load_segment_stats()

        # Круговая диаграмма
        fig_segments = px.pie(
            segment_stats,
            values='count',
            names='segment',
            title='Количество клиентов по сегментам',
            color='segment',
            color_discrete_map={
                'A': '#FF6B6B',  # Красный
                'B': '#4ECDC4',  # Бирюзовый
                'C': '#FFE66D',  # Жёлтый
                'U': '#95E1D3'   # Светло-зелёный
            },
            hole=0.4  # Donut chart
        )
        fig_segments.update_traces(
            textposition='inside',
            textinfo='percent+label+value',
            hovertemplate='<b>%{label}</b><br>Клиентов: %{value}<br>Процент: %{percent}<extra></extra>'
        )
        st.plotly_chart(fig_segments, width="stretch")

    with col_right:
        # Таблица со статистикой по сегментам
        st.markdown("#### 📋 Детальная статистика")

        segment_table = segment_stats.copy()
        segment_table['total_ltv'] = segment_table['total_ltv'].apply(lambda x: f"{x:,.0f} ₽")
        segment_table['avg_ltv'] = segment_table['avg_ltv'].apply(lambda x: f"{x:,.0f} ₽")
        segment_table['avg_orders'] = segment_table['avg_orders'].apply(lambda x: f"{x:.1f}")
        segment_table['avg_median'] = segment_table['avg_median'].apply(lambda x: f"{x:.1f}")
        segment_table['avg_mean'] = segment_table['avg_mean'].apply(lambda x: f"{x:.1f}")

        segment_table.columns = [
            'Сегмент',
            'Кол-во',
            'Total LTV',
            'Средний LTV',
            'Средн. заказов',
            'Медиана в год',
            'Среднее в год'
        ]

        st.dataframe(segment_table, width="stretch", hide_index=True)

        st.info("""
        **Сегменты:**
        - 🔴 **A**: LTV ≥ 100,000 ₽ (премиум-клиенты)
        - 🔵 **B**: 20,000 ₽ ≤ LTV < 100,000 ₽
        - 🟡 **C**: 10,000 ₽ ≤ LTV < 20,000 ₽
        - 🟢 **U**: LTV < 10,000 ₽ (новички)
        """)

    st.divider()

    # ============================================================================
    # БАРЧАРТ: ТОП-10 ТИПОВ СЪЁМОК
    # ============================================================================

    st.markdown("### 📸 Топ-10 типов съёмок по популярности")

    shooting_stats = load_shooting_type_stats()
    top_10_shooting = shooting_stats.head(10)

    fig_shooting = px.bar(
        top_10_shooting,
        x='count',
        y='shooting_type',
        orientation='h',
        title='Количество клиентов по типам съёмки',
        labels={'count': 'Количество клиентов', 'shooting_type': 'Тип съёмки'},
        color='count',
        color_continuous_scale='Blues'
    )
    fig_shooting.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False
    )
    fig_shooting.update_traces(
        hovertemplate='<b>%{y}</b><br>Клиентов: %{x}<extra></extra>'
    )
    st.plotly_chart(fig_shooting, width="stretch")

    # Дополнительная статистика по съёмкам
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 💰 Средний чек по типу съёмки")
        top_10_shooting_avg = top_10_shooting.copy()
        top_10_shooting_avg = top_10_shooting_avg.sort_values('avg_ltv', ascending=False)

        fig_avg_ltv = px.bar(
            top_10_shooting_avg,
            x='avg_ltv',
            y='shooting_type',
            orientation='h',
            labels={'avg_ltv': 'Средний LTV (₽)', 'shooting_type': 'Тип съёмки'},
            color='avg_ltv',
            color_continuous_scale='Greens'
        )
        fig_avg_ltv.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        fig_avg_ltv.update_traces(
            hovertemplate='<b>%{y}</b><br>Средний LTV: %{x:,.0f} ₽<extra></extra>'
        )
        st.plotly_chart(fig_avg_ltv, width="stretch")

    with col2:
        st.markdown("#### 📦 Всего заказов по типу съёмки")
        top_10_shooting_orders = top_10_shooting.copy()
        top_10_shooting_orders = top_10_shooting_orders.sort_values('total_orders', ascending=False)

        fig_orders = px.bar(
            top_10_shooting_orders,
            x='total_orders',
            y='shooting_type',
            orientation='h',
            labels={'total_orders': 'Всего заказов', 'shooting_type': 'Тип съёмки'},
            color='total_orders',
            color_continuous_scale='Oranges'
        )
        fig_orders.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            showlegend=False
        )
        fig_orders.update_traces(
            hovertemplate='<b>%{y}</b><br>Заказов: %{x}<extra></extra>'
        )
        st.plotly_chart(fig_orders, width="stretch")

    st.divider()

    # ============================================================================
    # ТАБЛИЦА: ТОП-20 КЛИЕНТОВ ПО LTV
    # ============================================================================

    st.markdown("### 🏆 Топ-20 клиентов по LTV")

    top_companies = load_top_companies(limit=20)
    top_df = pd.DataFrame(top_companies)

    # Форматирование для отображения
    top_df_display = top_df.copy()
    top_df_display['ltv'] = top_df_display['ltv'].apply(lambda x: f"{x:,.0f} ₽")
    top_df_display['orders_count_median'] = top_df_display['orders_count_median'].apply(lambda x: f"{x:.1f}")
    top_df_display['orders_count_mean'] = top_df_display['orders_count_mean'].apply(lambda x: f"{x:.1f}")

    top_df_display.columns = [
        'Bitrix ID',
        'Компания',
        'LTV',
        'Сегмент',
        'Заказов',
        'Медиана в год',
        'Среднее в год',
        'Тип съёмки',
        'URL'
    ]

    # Убираем URL из отображения
    top_df_display = top_df_display.drop(columns=['URL'])

    st.dataframe(
        top_df_display,
        width="stretch",
        hide_index=True,
        column_config={
            "Сегмент": st.column_config.TextColumn(
                "Сегмент",
                help="A/B/C/U сегмент",
                width="small"
            )
        }
    )

    st.divider()

    # ============================================================================
    # ЛИНЕЙНЫЙ ГРАФИК: ТРЕНД LTV ПО ГОДАМ
    # ============================================================================

    st.markdown("### 📉 Тренд выручки по годам")

    ltv_trend = load_ltv_trend()

    if not ltv_trend.empty:
        fig_trend = go.Figure()

        fig_trend.add_trace(go.Scatter(
            x=ltv_trend['year'],
            y=ltv_trend['total_revenue'],
            mode='lines+markers',
            name='Выручка',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=10),
            hovertemplate='<b>%{x}</b><br>Выручка: %{y:,.0f} ₽<br><extra></extra>'
        ))

        fig_trend.update_layout(
            title='Динамика выручки по годам (на основе дат закрытия сделок)',
            xaxis_title='Год',
            yaxis_title='Выручка (₽)',
            hovermode='x unified'
        )

        st.plotly_chart(fig_trend, width="stretch")

        # Дополнительная статистика
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label="📅 Всего лет",
                value=len(ltv_trend),
                help="Количество лет с данными о заказах"
            )

        with col2:
            latest_year = ltv_trend.iloc[-1]
            st.metric(
                label=f"💰 Выручка {latest_year['year']}",
                value=f"{latest_year['total_revenue']:,.0f} ₽",
                help="Выручка за последний год с данными"
            )

        with col3:
            if len(ltv_trend) > 1:
                prev_year = ltv_trend.iloc[-2]['total_revenue']
                current_year = latest_year['total_revenue']
                growth = ((current_year - prev_year) / prev_year * 100) if prev_year > 0 else 0
                st.metric(
                    label="📈 Рост год к году",
                    value=f"{growth:+.1f}%",
                    delta=f"{current_year - prev_year:,.0f} ₽",
                    help="Процентное изменение выручки относительно предыдущего года"
                )
    else:
        st.warning("⚠️ Нет данных о трендах (возможно, не заполнены даты закрытия сделок)")

except Exception as e:
    st.error(f"❌ Ошибка загрузки данных: {e}")
    st.exception(e)
