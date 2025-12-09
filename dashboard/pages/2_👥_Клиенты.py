"""
Страница "Клиенты" - список клиентов с фильтрами

Интерактивная таблица с фильтрами по сегменту, типу съёмки, LTV, поиск по названию.
Экспорт в Excel.
"""
import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from io import BytesIO

# Добавить корневую директорию в PYTHONPATH
ROOT_DIR = Path(__file__).parent.parent.parent
sys.path.insert(0, str(ROOT_DIR))

from dashboard.utils import (
    load_companies_dataframe,
    search_companies,
    load_segment_stats,
    load_shooting_type_stats
)

st.set_page_config(page_title="Клиенты", page_icon="👥", layout="wide")

st.title("👥 Клиенты - Полный список с фильтрами")

# ============================================================================
# БОКОВАЯ ПАНЕЛЬ С ФИЛЬТРАМИ
# ============================================================================

st.sidebar.markdown("### 🔍 Фильтры")

# Получить уникальные значения для фильтров
segment_stats = load_segment_stats()
shooting_stats = load_shooting_type_stats()

# Фильтр по сегменту
segments = ['Все'] + segment_stats['segment'].tolist()
selected_segment = st.sidebar.selectbox(
    "Сегмент",
    segments,
    help="Выберите сегмент A/B/C/U"
)

# Фильтр по типу съёмки
shooting_types = ['Все'] + shooting_stats['shooting_type'].tolist()
selected_shooting_type = st.sidebar.selectbox(
    "Тип съёмки",
    shooting_types,
    help="Выберите основной тип съёмки"
)

# Фильтр по LTV (диапазон)
st.sidebar.markdown("**Диапазон LTV (₽)**")
col1, col2 = st.sidebar.columns(2)
with col1:
    min_ltv = st.number_input(
        "От",
        min_value=0,
        max_value=10000000,
        value=0,
        step=10000,
        help="Минимальный LTV"
    )
with col2:
    max_ltv = st.number_input(
        "До",
        min_value=0,
        max_value=10000000,
        value=10000000,
        step=10000,
        help="Максимальный LTV"
    )

# Лимит записей
limit = st.sidebar.slider(
    "Количество записей",
    min_value=10,
    max_value=1000,
    value=100,
    step=10,
    help="Максимальное количество клиентов для отображения"
)

# Поиск по названию
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔎 Поиск по названию")
search_query = st.sidebar.text_input(
    "Введите название компании",
    placeholder="Например: ГЕЙДАРОВ",
    help="Поиск по названию компании (регистронезависимый)"
)

# ============================================================================
# ЗАГРУЗКА ДАННЫХ С ФИЛЬТРАМИ
# ============================================================================

try:
    if search_query:
        # Поиск по названию
        df = search_companies(search_query, limit=limit)
        st.info(f"🔍 Найдено {len(df)} компаний по запросу: **{search_query}**")
    else:
        # Фильтрация по выбранным параметрам
        segment_filter = None if selected_segment == 'Все' else selected_segment
        shooting_filter = None if selected_shooting_type == 'Все' else selected_shooting_type

        df = load_companies_dataframe(
            segment=segment_filter,
            shooting_type=shooting_filter,
            min_ltv=min_ltv if min_ltv > 0 else None,
            max_ltv=max_ltv if max_ltv < 10000000 else None,
            limit=limit
        )

    # ============================================================================
    # СТАТИСТИКА ПО ВЫБОРКЕ
    # ============================================================================

    if not df.empty:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                label="📊 Клиентов в выборке",
                value=f"{len(df):,}",
                help="Количество клиентов, соответствующих фильтрам"
            )

        with col2:
            total_ltv = df['ltv'].sum()
            st.metric(
                label="💰 Total LTV выборки",
                value=f"{total_ltv:,.0f} ₽",
                help="Общая сумма LTV всех клиентов в выборке"
            )

        with col3:
            avg_ltv = df['ltv'].mean()
            st.metric(
                label="📈 Средний LTV",
                value=f"{avg_ltv:,.0f} ₽",
                help="Средний LTV в выборке"
            )

        with col4:
            total_orders = df['orders_count'].sum()
            st.metric(
                label="📦 Всего заказов",
                value=f"{total_orders:,}",
                help="Общее количество заказов в выборке"
            )

        st.divider()

        # ============================================================================
        # ТАБЛИЦА КЛИЕНТОВ
        # ============================================================================

        st.markdown("### 📋 Список клиентов")

        # Форматирование для отображения
        df_display = df.copy()
        df_display['ltv'] = df_display['ltv'].apply(lambda x: f"{x:,.0f} ₽")
        df_display['orders_count_median'] = df_display['orders_count_median'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else "—"
        )
        df_display['orders_count_mean'] = df_display['orders_count_mean'].apply(
            lambda x: f"{x:.1f}" if pd.notna(x) else "—"
        )
        df_display['primary_shooting_type'] = df_display['primary_shooting_type'].fillna('—')

        # Переименование колонок
        df_display.columns = [
            'Bitrix ID',
            'Компания',
            'LTV',
            'Сегмент',
            'Заказов',
            'Медиана в год',
            'Среднее в год',
            'Тип съёмки'
        ]

        # Отображаем таблицу
        st.dataframe(
            df_display,
            width="stretch",
            hide_index=True,
            height=600,
            column_config={
                "Сегмент": st.column_config.TextColumn(
                    "Сегмент",
                    help="A/B/C/U сегмент",
                    width="small"
                ),
                "Заказов": st.column_config.NumberColumn(
                    "Заказов",
                    help="Общее количество заказов",
                    width="small"
                )
            }
        )

        # ============================================================================
        # ЭКСПОРТ В EXCEL
        # ============================================================================

        st.divider()
        st.markdown("### 💾 Экспорт данных")

        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            # Подготовка данных для экспорта (используем исходный df без форматирования)
            df_export = df.copy()

            # Создаём Excel файл в памяти
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_export.to_excel(writer, index=False, sheet_name='Клиенты')

            excel_data = output.getvalue()

            st.download_button(
                label="📥 Скачать в Excel",
                data=excel_data,
                file_name=f"fotofactor_clients_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help="Скачать текущую выборку в формате Excel"
            )

            st.info(f"📊 Будет экспортировано **{len(df)}** записей")

    else:
        st.warning("⚠️ Нет данных, соответствующих выбранным фильтрам")
        st.info("💡 Попробуйте изменить параметры фильтров в боковой панели")

except Exception as e:
    st.error(f"❌ Ошибка загрузки данных: {e}")
    st.exception(e)

# ============================================================================
# ПОДСКАЗКИ
# ============================================================================

with st.expander("💡 Как использовать фильтры"):
    st.markdown("""
    ### Фильтрация клиентов:

    1. **Сегмент** - выберите один из сегментов (A/B/C/U) или "Все"
    2. **Тип съёмки** - выберите конкретный тип или "Все"
    3. **Диапазон LTV** - задайте минимальный и максимальный LTV
    4. **Количество записей** - установите лимит для отображения
    5. **Поиск** - введите часть названия компании для быстрого поиска

    ### Экспорт данных:

    - Нажмите кнопку "Скачать в Excel" для экспорта текущей выборки
    - Файл будет содержать все выбранные записи с полными данными
    - Формат: `.xlsx` (Microsoft Excel)

    ### Советы:

    - Комбинируйте фильтры для точной выборки
    - Используйте поиск для быстрого поиска конкретной компании
    - Увеличьте лимит записей, если нужно больше данных
    """)
