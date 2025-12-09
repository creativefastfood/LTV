"""
Страница "Тренды" - временной анализ

LTV по месяцам, количество заказов, сезонность.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from pathlib import Path
import sys
from datetime import datetime

# Добавить корневую директорию в PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dashboard.utils import load_ltv_trend
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Тренды", page_icon="📉", layout="wide")

st.title("📉 Тренды и динамика")

# ============================================================================
# ТРЕНД ВЫРУЧКИ ПО ГОДАМ
# ============================================================================

st.markdown("### 📈 Динамика выручки по годам")

try:
    ltv_trend = load_ltv_trend()

    if not ltv_trend.empty:
        # График с двумя осями: выручка и количество сделок
        fig = go.Figure()

        # Выручка (левая ось)
        fig.add_trace(go.Scatter(
            x=ltv_trend['year'],
            y=ltv_trend['total_revenue'],
            mode='lines+markers',
            name='Выручка',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=10),
            yaxis='y',
            hovertemplate='<b>%{x}</b><br>Выручка: %{y:,.0f} ₽<extra></extra>'
        ))

        # Количество сделок (правая ось)
        fig.add_trace(go.Scatter(
            x=ltv_trend['year'],
            y=ltv_trend['deals_count'],
            mode='lines+markers',
            name='Количество сделок',
            line=dict(color='#FF6B6B', width=3, dash='dash'),
            marker=dict(size=10, symbol='diamond'),
            yaxis='y2',
            hovertemplate='<b>%{x}</b><br>Сделок: %{y:,}<extra></extra>'
        ))

        # Настройка осей
        fig.update_layout(
            title='Тренд выручки и количества сделок по годам',
            xaxis_title='Год',
            yaxis=dict(
                title='Выручка (₽)',
                titlefont=dict(color='#4ECDC4'),
                tickfont=dict(color='#4ECDC4')
            ),
            yaxis2=dict(
                title='Количество сделок',
                titlefont=dict(color='#FF6B6B'),
                tickfont=dict(color='#FF6B6B'),
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            )
        )

        st.plotly_chart(fig, width="stretch")

        # Статистика по годам
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📅 Всего лет",
                value=len(ltv_trend),
                help="Количество лет с данными о заказах"
            )

        with col2:
            if len(ltv_trend) > 0:
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

        with col4:
            total_revenue = ltv_trend['total_revenue'].sum()
            st.metric(
                label="💰 Total выручка",
                value=f"{total_revenue:,.0f} ₽",
                help="Общая выручка за все годы"
            )

        st.divider()

        # ============================================================================
        # ПОМЕСЯЧНЫЙ АНАЛИЗ
        # ============================================================================

        st.markdown("### 📅 Помесячный анализ (последние 24 месяца)")

        DB_PATH = ROOT_DIR / "platrum.db"
        DATABASE_URL = f"sqlite:///{DB_PATH}"
        engine = create_engine(DATABASE_URL)

        query = """
            SELECT
                strftime('%Y-%m', close_date) as month,
                COUNT(DISTINCT company_id) as companies,
                SUM(opportunity) as revenue,
                COUNT(*) as deals_count
            FROM bitrix_deals
            WHERE close_date IS NOT NULL
              AND close_date >= date('now', '-24 months')
            GROUP BY month
            ORDER BY month
        """

        with engine.connect() as conn:
            df_monthly = pd.read_sql_query(text(query), conn)

        if not df_monthly.empty:
            # График помесячной выручки
            fig_monthly = go.Figure()

            fig_monthly.add_trace(go.Bar(
                x=df_monthly['month'],
                y=df_monthly['revenue'],
                name='Выручка',
                marker_color='#4ECDC4',
                hovertemplate='<b>%{x}</b><br>Выручка: %{y:,.0f} ₽<extra></extra>'
            ))

            fig_monthly.update_layout(
                title='Помесячная выручка (последние 24 месяца)',
                xaxis_title='Месяц',
                yaxis_title='Выручка (₽)',
                hovermode='x unified'
            )

            st.plotly_chart(fig_monthly, width="stretch")

            # Статистика по месяцам
            col1, col2, col3 = st.columns(3)

            with col1:
                avg_monthly_revenue = df_monthly['revenue'].mean()
                st.metric(
                    label="💰 Средняя выручка/месяц",
                    value=f"{avg_monthly_revenue:,.0f} ₽",
                    help="Средняя ежемесячная выручка за последние 24 месяца"
                )

            with col2:
                max_month = df_monthly.loc[df_monthly['revenue'].idxmax()]
                st.metric(
                    label="🏆 Лучший месяц",
                    value=max_month['month'],
                    delta=f"{max_month['revenue']:,.0f} ₽",
                    help="Месяц с максимальной выручкой"
                )

            with col3:
                total_deals_monthly = df_monthly['deals_count'].sum()
                st.metric(
                    label="📦 Всего сделок",
                    value=f"{total_deals_monthly:,}",
                    help="Общее количество сделок за последние 24 месяца"
                )

            st.divider()

            # ============================================================================
            # СЕЗОННОСТЬ (СРЕДНЕЕ ПО МЕСЯЦАМ)
            # ============================================================================

            st.markdown("### 🌡️ Сезонность (среднее по месяцам года)")

            # Добавляем номер месяца
            df_monthly['month_num'] = pd.to_datetime(df_monthly['month']).dt.month

            # Группируем по номеру месяца и считаем среднее
            seasonality = df_monthly.groupby('month_num').agg({
                'revenue': 'mean',
                'deals_count': 'mean',
                'companies': 'mean'
            }).reset_index()

            # Названия месяцев
            month_names = {
                1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
                5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
                9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
            }
            seasonality['month_name'] = seasonality['month_num'].map(month_names)

            col1, col2 = st.columns(2)

            with col1:
                # График сезонности выручки
                fig_season_revenue = px.bar(
                    seasonality,
                    x='month_name',
                    y='revenue',
                    title='Средняя выручка по месяцам года',
                    labels={'month_name': 'Месяц', 'revenue': 'Средняя выручка (₽)'},
                    color='revenue',
                    color_continuous_scale='Blues'
                )
                fig_season_revenue.update_traces(
                    hovertemplate='<b>%{x}</b><br>Средняя выручка: %{y:,.0f} ₽<extra></extra>'
                )
                st.plotly_chart(fig_season_revenue, width="stretch")

            with col2:
                # График сезонности количества сделок
                fig_season_deals = px.bar(
                    seasonality,
                    x='month_name',
                    y='deals_count',
                    title='Среднее количество сделок по месяцам года',
                    labels={'month_name': 'Месяц', 'deals_count': 'Среднее кол-во сделок'},
                    color='deals_count',
                    color_continuous_scale='Greens'
                )
                fig_season_deals.update_traces(
                    hovertemplate='<b>%{x}</b><br>Среднее сделок: %{y:.1f}<extra></extra>'
                )
                st.plotly_chart(fig_season_deals, width="stretch")

            # Топ-3 и низ-3 месяца
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("#### 🏆 Топ-3 месяца (по выручке)")
                top_3_months = seasonality.nlargest(3, 'revenue')[['month_name', 'revenue']]
                top_3_months['revenue'] = top_3_months['revenue'].apply(lambda x: f"{x:,.0f} ₽")
                top_3_months.columns = ['Месяц', 'Средняя выручка']
                st.dataframe(top_3_months, width="stretch", hide_index=True)

            with col2:
                st.markdown("#### 📉 Низ-3 месяца (по выручке)")
                bottom_3_months = seasonality.nsmallest(3, 'revenue')[['month_name', 'revenue']]
                bottom_3_months['revenue'] = bottom_3_months['revenue'].apply(lambda x: f"{x:,.0f} ₽")
                bottom_3_months.columns = ['Месяц', 'Средняя выручка']
                st.dataframe(bottom_3_months, width="stretch", hide_index=True)

        else:
            st.warning("⚠️ Нет данных для помесячного анализа (возможно, недостаточно данных за последние 24 месяца)")

    else:
        st.warning("⚠️ Нет данных о трендах (возможно, не заполнены даты закрытия сделок)")

    st.divider()

    # ============================================================================
    # ПРОГНОЗ НА СЛЕДУЮЩИЙ ГОД (ПРОСТОЙ LINEAR TREND)
    # ============================================================================

    if not ltv_trend.empty and len(ltv_trend) >= 3:
        st.markdown("### 🔮 Простой прогноз на следующий год")

        st.info("""
        💡 **Метод прогнозирования**: Линейная регрессия на основе исторических данных.

        Прогноз основан на тренде последних лет и является упрощённым. Для точного прогноза требуется учёт сезонности, экономических факторов и других переменных.
        """)

        # Простая линейная регрессия
        from sklearn.linear_model import LinearRegression
        import numpy as np

        # Преобразуем годы в числа
        ltv_trend['year_num'] = ltv_trend['year'].astype(int)

        X = ltv_trend['year_num'].values.reshape(-1, 1)
        y = ltv_trend['total_revenue'].values

        model = LinearRegression()
        model.fit(X, y)

        # Прогноз на следующий год
        next_year = ltv_trend['year_num'].max() + 1
        forecast_revenue = model.predict([[next_year]])[0]

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                label=f"📅 Прогноз на {next_year}",
                value=f"{forecast_revenue:,.0f} ₽",
                help="Прогнозируемая выручка на следующий год (линейный тренд)"
            )

        with col2:
            if len(ltv_trend) > 0:
                latest_revenue = ltv_trend.iloc[-1]['total_revenue']
                growth_forecast = ((forecast_revenue - latest_revenue) / latest_revenue * 100) if latest_revenue > 0 else 0
                st.metric(
                    label="📈 Прогнозируемый рост",
                    value=f"{growth_forecast:+.1f}%",
                    delta=f"{forecast_revenue - latest_revenue:,.0f} ₽",
                    help="Ожидаемый рост выручки относительно последнего года"
                )

        with col3:
            # R² score
            from sklearn.metrics import r2_score
            y_pred = model.predict(X)
            r2 = r2_score(y, y_pred)
            st.metric(
                label="📊 R² (точность модели)",
                value=f"{r2:.2f}",
                help="Коэффициент детерминации (чем ближе к 1, тем лучше)"
            )

        # График с прогнозом
        fig_forecast = go.Figure()

        # Исторические данные
        fig_forecast.add_trace(go.Scatter(
            x=ltv_trend['year'],
            y=ltv_trend['total_revenue'],
            mode='lines+markers',
            name='Фактическая выручка',
            line=dict(color='#4ECDC4', width=3),
            marker=dict(size=10)
        ))

        # Линия тренда
        trend_line = model.predict(X)
        fig_forecast.add_trace(go.Scatter(
            x=ltv_trend['year'],
            y=trend_line,
            mode='lines',
            name='Линия тренда',
            line=dict(color='#95E1D3', width=2, dash='dash')
        ))

        # Прогноз
        fig_forecast.add_trace(go.Scatter(
            x=[str(next_year)],
            y=[forecast_revenue],
            mode='markers',
            name='Прогноз',
            marker=dict(size=15, color='#FF6B6B', symbol='star')
        ))

        fig_forecast.update_layout(
            title='Выручка с прогнозом на следующий год',
            xaxis_title='Год',
            yaxis_title='Выручка (₽)',
            hovermode='x unified'
        )

        st.plotly_chart(fig_forecast, width="stretch")

        st.warning("⚠️ **Примечание**: Этот прогноз является упрощённым и служит для ориентировочной оценки. Для точного планирования рекомендуется использовать более сложные модели с учётом сезонности, маркетинговых активностей и экономической ситуации.")

except Exception as e:
    st.error(f"❌ Ошибка загрузки данных: {e}")
    st.exception(e)
