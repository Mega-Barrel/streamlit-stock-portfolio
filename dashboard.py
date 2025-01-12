
import pandas as pd
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Create a connection object.
@st.cache_resource
def create_gsheet_connection():
    """Create connection to gsheet"""
    _conn = st.connection("gsheets", type=GSheetsConnection)
    return _conn

@st.cache_data
def get_data(_gsheets_connection):
    """Read data from gsheet"""
    # Read the main worksheet
    ticker_df = _gsheets_connection.read(worksheet="ticker")

    history_dfs = {}
    for ticker in list(ticker_df["ticker"]):
        d = _gsheets_connection.read(worksheet=ticker)
        history_dfs[ticker] = d
    return ticker_df, history_dfs

# @st.cache_data
def transform_data(ticker_df, history_dfs):
    """ Function to transform data"""
    ticker_df['last_trade_time'] = pd.to_datetime(
        ticker_df['last_trade_time'],
        dayfirst=True
    )

    for col in [
        "last_price",
        "previous_day_price",
        "change",
        "change_pct",
        "volume",
        "volume_avg",
        "shares",
        "day_high",
        "day_low",
        "market_cap",
        "p/e_ratio",
        "eps"
    ]:
        ticker_df[col] = pd.to_numeric(
            ticker_df[col],
            'coerce'
        )

    for ticker in list(ticker_df['ticker']):
        history_dfs[ticker]['Date'] = pd.to_datetime(
            history_dfs[ticker]['Date'],
            dayfirst=True
        )

        for col in [
            "Open",
            "High",
            "Low",
            "Close",
            "Volume"
        ]:
            history_dfs[ticker][col] = pd.to_numeric(history_dfs[ticker][col])
        ticker_to_open = [list(history_dfs[t]["Open"]) for t in list(ticker_df["ticker"])]
        ticker_df["Open"] = ticker_to_open

    return ticker_df, history_dfs

def display_overview(ticker_df):
    st.dataframe(
        ticker_df,
        column_order=[
            column
            for column in list(ticker_df.columns)
            if column not in [
                "_airbyte_raw_id",
                "_airbyte_extracted_at",
                "_airbyte_meta"
            ]
        ],
        column_config={
            "Open": st.column_config.AreaChartColumn(
                "Last 12 months",
                width="large",
                help="Open Price for last 12 Months"
            )
        },
        hide_index=True,
        height=250
    )

st.title('Stocks Dashboard')

gsheet_connection = create_gsheet_connection()
ticker_df, history_df = get_data(gsheet_connection)

ticker_df, history_df = transform_data(ticker_df=ticker_df, history_dfs=history_df)
display_overview(ticker_df=ticker_df)