import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import timedelta

# Streamlit Page Configuration
st.set_page_config(page_title="Total Return Calculator", layout="wide")
st.title("ETF & Stock Total Return Calculator")
st.markdown("Compare the performance of holding a stock vs. holding and keeping dividends as cash vs. fully reinvesting dividends (DRIP).")

# ==========================================
# 💾 CACHED DATA FETCHER
# ==========================================
@st.cache_data(ttl="1d", show_spinner=False)
def fetch_ticker_data(ticker_symbol):
    tkr = yf.Ticker(ticker_symbol)
    hist = tkr.history(period="max", auto_adjust=False, actions=True)
    
    if hist.empty:
        return None
        
    if 'Dividends' not in hist.columns:
        hist['Dividends'] = 0.0
        
    if hist.index.tz is not None:
        hist.index = hist.index.tz_localize(None)
        
    return hist[['Close', 'Dividends']].copy()

# ==========================================
# 🧮 PERFORMANCE CALCULATOR
# ==========================================
def calculate_performance(hist, initial_inv):
    df = hist.copy()
    if df.empty:
        return df
        
    initial_price = df['Close'].iloc[0]
    initial_shares = initial_inv / initial_price
    df['Price Only'] = df['Close'] * initial_shares
    
    df['Cumulative Dividends Per Share'] = df['Dividends'].cumsum()
    df['Dividends as Cash'] = df['Price Only'] + (df['Cumulative Dividends Per Share'] * initial_shares)
    
    current_shares = initial_shares
    dr_shares_series = [current_shares]
    
    for i in range(1, len(df)):
        div_paid = df['Dividends'].iloc[i] * current_shares
        if div_paid > 0:
            current_shares += (div_paid / df['Close'].iloc[i])
        dr_shares_series.append(current_shares)
        
    df['DRIP Shares'] = dr_shares_series
    df['Reinvested Dividends'] = df['Close'] * df['DRIP Shares']
    
    return df

# ==========================================
# UI AND CONFIGURATION
# ==========================================
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "HYLD.TO, USCL.TO, QDAY.NE, TXF.TO"

st.sidebar.header("Configuration")
st.sidebar.subheader("Popular Covered Call ETFs")
col1, col2, col3 = st.sidebar.columns(3)

with col1:
    if st.button("HYLD"):
        st.session_state.selected_ticker = "HYLD.TO"
    if st.button("HDIV"):
        st.session_state.selected_ticker = "HDIV.TO"
    if st.button("BMAX"):
        st.session_state.selected_ticker = "BMAX.TO"

with col2:
    if st.button("HDIF"):
        st.session_state.selected_ticker = "HDIF.TO"
    if st.button("USCL"):
        st.session_state.selected_ticker = "USCL.TO"
    if st.button("QQCL"):
        st.session_state.selected_ticker = "QQCL.TO"

st.sidebar.divider()

tickers_input = st.sidebar.text_input(
    "Enter Tickers (comma-separated)", 
    st.session_state.selected_ticker
)
initial_investment = st.sidebar.number_input("Initial Investment ($)", value=10000, step=1000)

# ==========================================
# MAIN EXECUTION
# ==========================================
if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    raw_data = {}
    with st.spinner("Loading data (using local cache if available)..."):
        for ticker in tickers:
            try:
                hist = fetch_ticker_data(ticker)
                if hist is not None:
                    raw_data[ticker] = hist
                else:
                    st.warning(f"⚠️ No pricing data found for {ticker}.")
            except Exception as e:
                st.error(f"Failed to fetch data for {ticker}: {e}")

    if raw_data:
        # Find common start date for the unified comparison chart
        start_dates = [df.index.min() for df in raw_data.values()]
        common_start_date = max(start_dates)
        
        st.info(f"🗓️ **Note on Dates:** The top comparison chart aligns all funds to start on **{common_start_date.strftime('%Y-%m-%d')}** (inception of the newest fund) for a fair race. The individual breakdowns below show the **maximum available history** for each fund.")
        
        drip_comparison = {}
        individual_histories = {}

        # Process the calculations
        for ticker, full_hist in raw_data.items():
            
            # 1. Calculate Maximum History (for the individual dropdowns)
            ind_calc = calculate_performance(full_hist, initial_investment)
            individual_histories[ticker] = ind_calc
            
            # 2. Calculate Common History (for the unified comparison chart)
            sliced_hist = full_hist[full_hist.index >= common_start_date].copy()
            if not sliced_hist.empty:
                comp_calc = calculate_performance(sliced_hist, initial_investment)
                drip_comparison[ticker] = comp_calc['Reinvested Dividends']

        # ==========================================
        # PLOT 1: THE UNIFIED COMPARISON CHART
        # ==========================================
        if drip_comparison:
            st.header("📊 Total Return Comparison (Fair Start)")
            
            comp_fig = go.Figure()
            for ticker, series in drip_comparison.items():
                comp_fig.add_trace(go.Scatter(
                    x=series.index, 
                    y=series, 
                    mode='lines', 
                    name=ticker,
                    hovertemplate='%{x|%Y-%m-%d}<br>Value: $%{y:,.2f}<extra></extra>'
                ))
                
            comp_fig.update_layout(
                title=f"DRIP Comparison — Growth of ${initial_investment:,.2f} since {common_start_date.strftime('%Y-%m-%d')}",
                yaxis_title="Portfolio Value ($)",
                xaxis_title="Date",
                hovermode="x unified",
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(comp_fig, use_container_width=True)
            
            st.divider()

        # ==========================================
        # PLOT 2: INDIVIDUAL BREAKDOWNS (MAX PERIOD)
        # ==========================================
        st.header("🔍 Individual Breakdown (Max History)")
        for ticker, hist in individual_histories.items():
            fund_start_date = hist.index.min().strftime('%Y-%m-%d')
            
            with st.expander(f"Show details for {ticker} (Since {fund_start_date})", expanded=False):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Price Only'], mode='lines', name='Price Only', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Dividends as Cash'], mode='lines', name='+ Dividends as Cash', line=dict(color='orange')))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Reinvested Dividends'], mode='lines', name='+ Reinvested Dividends (DRIP)', line=dict(color='green')))
                
                fig.update_layout(
                    title=f"{ticker} Internal Growth Dynamics — Growth of ${initial_investment:,.2f} since {fund_start_date}",
                    yaxis_title="Portfolio Value ($)",
                    xaxis_title="Date",
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
