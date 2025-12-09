# 📊 LTV Analytics Dashboard

Interactive Streamlit dashboard for client LTV (Lifetime Value) analytics with advanced segmentation, trend analysis, and revenue forecasting.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 🚀 Quick Start

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Open in browser: **http://localhost:8501**

## ✨ Features

### 📈 5 Interactive Pages

1. **Overview** - KPI cards, segment distribution, top clients, revenue trends
2. **Clients** - Filterable table with Excel export
3. **Segments** - A/B/C/U comparison with transition forecasting
4. **Shooting Types** - Service popularity and profitability analysis
5. **Trends** - Time-series analysis with ML-based forecasting

### 🎯 Key Capabilities

- **40+ Interactive Widgets** - KPI cards, charts, tables with Plotly
- **Advanced Filtering** - By segment, service type, LTV range
- **Excel Export** - One-click data export
- **Client Segmentation** - A/B/C/U tiers (Premium/Active/Growing/New)
- **Revenue Forecasting** - Linear regression predictions
- **Real-time Search** - Find clients by name instantly

## 📊 Dashboard Preview

### Segments Distribution
```
🔴 Segment A (Premium):  LTV ≥ 100,000 ₽
🔵 Segment B (Active):   20,000 ≤ LTV < 100,000 ₽
🟡 Segment C (Growing):  10,000 ≤ LTV < 20,000 ₽
🟢 Segment U (New):      LTV < 10,000 ₽
```

## 🛠️ Technologies

- **Streamlit** - Web framework for dashboards
- **Plotly** - Interactive visualizations
- **Pandas** - Data processing
- **SQLAlchemy** - Database ORM
- **scikit-learn** - ML forecasting

## 📚 Full Documentation

See [dashboard/README.md](dashboard/README.md) for complete documentation including:
- Detailed feature descriptions
- Installation guide
- Usage examples
- Architecture overview

See [dashboard/QUICKSTART.md](dashboard/QUICKSTART.md) for quick start guide.

## 📦 Requirements

- Python 3.11+
- SQLite database with client data

## 🗂️ Project Structure

```
LTV/
└── dashboard/
    ├── app.py              # Main entry point
    ├── pages/              # Dashboard pages
    │   ├── 1_📈_Обзор.py
    │   ├── 2_👥_Клиенты.py
    │   ├── 3_🎯_Сегменты.py
    │   ├── 4_📸_Типы_съёмок.py
    │   └── 5_📉_Тренды.py
    ├── utils/              # Helper functions
    │   ├── __init__.py
    │   └── data_loader.py
    ├── requirements.txt    # Dependencies
    ├── README.md          # Full documentation
    └── QUICKSTART.md      # Quick start guide
```

## 📈 Statistics

- **6 Pages**: Main + 5 sections
- **40+ Widgets**: Interactive components
- **15+ Charts**: Plotly visualizations
- **20+ Tables**: Data displays
- **1 Export**: Excel functionality

## 🔧 Configuration

The dashboard reads data from `platrum.db` SQLite database. Ensure the database exists and contains tables:
- `bitrix_companies` - Client data with LTV metrics
- `bitrix_deals` - Transaction history

## 🎨 Color Scheme

Segments use consistent colors across all visualizations:
- 🔴 Red (`#FF6B6B`) - Segment A (Premium)
- 🔵 Teal (`#4ECDC4`) - Segment B (Active)
- 🟡 Yellow (`#FFE66D`) - Segment C (Growing)
- 🟢 Green (`#95E1D3`) - Segment U (New)

## 📧 Contact

For questions and suggestions:
- Email: claude@fotofactor.ru
- Platrum: https://fotofactor.platrum.ru

## 📝 License

MIT License - feel free to use and modify.

---

**Version**: 1.0
**Date**: 2025-12-09
**Author**: Claude (AI Assistant for Fotofactor)
