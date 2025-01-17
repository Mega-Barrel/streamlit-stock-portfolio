
import pandas as pd
import streamlit as st
from itertools import islice
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from streamlit_gsheets import GSheetsConnection

# Set page config
st.set_page_config(layout="wide")
st.html("styles.html")

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

@st.cache_data
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
    def format_currency(val):
        return "$ {:,.2f}".format(val)

    def format_percentage(val):
        return "{:,.2f} %".format(val)

    def apply_odd_row_class(row):
        return [
            "background-color: #f8f8f8" if row.name % 2 != 0
            else "" for _ in row
        ]

    def format_change(val):
        return "color: red;" if (val < 0) else "color: green;"

    styled_df = ticker_df.style.format(
        {
            "last_price": format_currency,
            "change_pct": format_percentage
        }
    ).apply(
        apply_odd_row_class, axis=1
    ).map(
        format_change, subset=["change_pct"]
    )

    st.dataframe(
        styled_df,
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


def filter_history_df(selected_ticker, selected_period, history_dfs):
    history_df = history_dfs[selected_ticker]

    history_df = history_df.set_index("Date")
    mapping_period = {"Week": 7, "Month": 31, "Trimester": 90, "Year": 365}
    today = datetime.today().date()
    delay_days = mapping_period[selected_period]
    history_df = history_df[(today - pd.Timedelta(delay_days, unit="d")) : today]

    return history_df

def plot_canclestick(history_df):
    f_candle = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1
    )

    f_candle.add_trace(
        go.Candlestick(
            x=history_df.index,
            open=history_df['Open'],
            high=history_df['High'],
            low=history_df['Low'],
            close=history_df['Close'],
            name="Inr"
        ),
        row=1,
        col=1
    )
    f_candle.add_trace(
        go.Bar(
            x=history_df.index,
            y=history_df["Volume"],
            name="Volume Traded"
        ),
        row=2,
        col=1
    )
    f_candle.update_layout(
        title='Stock Price Trend',
        showlegend=False,
        xaxis_rangeslider_visible=False,
        yaxis1=dict(title='OHLC'),
        yaxis2=dict(title='Volume'),
        hovermode='x'
    )
    f_candle.update_layout(
        title_font_family="Open Sans",
        title_font_color="#174C4F",
        title_font_size=32,
        font_size=16,
        margin=dict(
            l=80,
            r=80,
            t=100,
            b=80,
            pad=0
        ),
        height=500
    )
    f_candle.update_xaxes(title_text="Date", row=2, col=1)
    f_candle.update_traces(selector=dict(name='INR'), showlegend=True)
    return f_candle

@st.fragment
def display_symbol_history(ticker_df, history_dfs):
    left_widget, right_widget, _ = st.columns([
        1, 1, 1.5
    ])
    selected_ticker = left_widget.selectbox(
        "📑 Currently Showing",
        list(history_dfs.keys())
    )
    selected_period = right_widget.selectbox(
        "⌚ Period",
        (
            "Week",
            "Month",
            "Trimester",
            "Year"
        ), 1
    )

    history_df = filter_history_df(
        selected_ticker=selected_ticker,
        selected_period=selected_period,
        history_dfs=history_dfs
    )

    f_candle = plot_canclestick(history_df)
    left_chart, right_indicator = st.columns([1.5, 1])

    with left_chart:
        st.plotly_chart(f_candle, use_container_width=True)
    
    with right_indicator:
        l, r = st.columns(2)
    
        with l:
            st.html('<span class="low-indicator"></span>')
            st.metric(
                "Lowest Volume Day Trade",
                f'{history_df["Volume"].min():,}',
            )
            st.metric(
                "Lowest Close Price",
                f"₹ {history_df['Close'].min():,}"
            )
        
        with r:
            st.html('<span class="high-indicator"></span>')
            st.metric(
                "Higest Volume Day Trade",
                f"{history_df['Volume'].max():,}"
            )
            st.metric(
                "Higest Close Price",
                f"₹ {history_df['Close'].max():,}"
            )

        with st.container():
            st.html('<span class="bottom-indicator"></span>')
            st.metric(
                "Average Daily Volume",
                f'{int(history_df["Volume"].mean()):,}'
            )
            st.metric(
                "Current Market Cap",
                "₹ {:,}".format(
                    ticker_df[ticker_df["ticker"] == selected_ticker][
                        "market_cap"
                    ].values[0]
                ),
            )

def batched(iterable, n_cols):
    # Batched('ABCDEFG', 3) -> ABC DEF G
    if n_cols < 1:
        raise ValueError("n must be at least one")
    it = iter(iterable)
    while batch:= tuple(islice(it, n_cols)):
        yield batch

def plot_sparkline(data):
    fig_spark = go.Figure(
        data=go.Scatter(
            y=data,
            mode="lines",
            fill="tozeroy",
            line_color="red",
            fillcolor="pink",
        ),
    )
    fig_spark.update_traces(hovertemplate="Price: ₹ %{y:.2f}")
    fig_spark.update_xaxes(visible=False, fixedrange=True)
    fig_spark.update_yaxes(visible=False, fixedrange=True)
    fig_spark.update_layout(
        showlegend=False,
        plot_bgcolor="white",
        height=50,
        margin=dict(
            t=10,
            l=10,
            b=10,
            r=10,
            pad=0
        )
    )
    return fig_spark

def display_watchlist_card(ticker, symbol_name, last_price, change_pct, open):
    with st.container(border=True):
        st.html(f'<span class="watchlist-card"></span>')
        
        tl, tr = st.columns([2, 1])
        bl, br = st.columns([1, 1])

        with tl:
            st.html(f'<span class="watchlist-symbol-name"</span>')
            st.markdown(f"{symbol_name}")
        with tr:
            st.html(f'<span class="watchlist-ticker"</span>')
            st.markdown(f"{ticker}")
            negative_gradient = float(change_pct) < 0
            st.markdown(
                f""":{
                    'red' if negative_gradient
                    else 'green'
                }[{'📉' if negative_gradient else '📈'}
                {change_pct} %]
                """
            )

        with bl:
            with st.container():
                st.html(f'<span class="watchlist-price-label"</span>')
                st.markdown(f"Current Value")
            with st.container():
                st.html(f'<span class="watchlist-price-value"</span>')
                st.markdown(f"₹ {last_price:.2f}")
        with br:
            st.html(f'<span class="watchlist-br"</span>')
            fig_spark = plot_sparkline(open)
            st.plotly_chart(
                fig_spark,
                config=dict(displayModeBar=False),
                use_container_width=True
            )

def display_watchlist(ticker_df):
    n_cols = 4
    
    for row in batched(ticker_df.itertuples(), n_cols):
        cols = st.columns(n_cols)
        for col, ticker in zip(cols, row):
            if ticker:
                with col:
                    display_watchlist_card(
                        ticker.ticker,
                        ticker.symbol_name,
                        ticker.last_price,
                        ticker.change_pct,
                        ticker.Open
                    )

# Gsheet connection object
gsheet_connection = create_gsheet_connection()
ticker_df, history_df = get_data(gsheet_connection)

st.header("Stocks Dashboard")
display_watchlist(ticker_df=ticker_df)
st.divider()
display_symbol_history(ticker_df, history_df)
