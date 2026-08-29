import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Streamlit Page Configuration
st.set_page_config(page_title="Total Return Calculator", layout="wide")
st.title("ETF & Stock Total Return Calculator")
st.markdown("Compare the performance of holding a stock vs. holding and keeping dividends as cash vs. fully reinvesting dividends (DRIP).")

# Initialize session state for ticker selection
if "selected_ticker" not in st.session_state:
    st.session_state.selected_ticker = "HYLD.TO, USCL.TO, QDAY.NE, TXF.TO"

# Sidebar for user inputs
st.sidebar.header("Configuration")

# Quick select buttons for popular Canadian covered call ETFs
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

if st.sidebar.button("Calculate Performance"):
    # Clean up the ticker list
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    for ticker in tickers:
        st.subheader(f"Performance: {ticker}")
        
        # Fetch historical data (auto_adjust=False ensures we get raw prices and real dividend payouts)
        tkr = yf.Ticker(ticker)
        try:
            hist = tkr.history(period="max", auto_adjust=False, actions=True)
        except Exception as e:
            st.error(f"Failed to download data for {ticker}: {e}")
            continue
            
        if hist.empty:
            st.warning(f"No pricing data found for {ticker} in the selected date range.")
            continue
            
        # Ensure we only work with the necessary columns
        hist = hist[['Close', 'Dividends']].copy()
        
        # 1. Price Only
        initial_price = hist['Close'].iloc[0]
        initial_shares = initial_investment / initial_price
        hist['Price Only'] = hist['Close'] * initial_shares
        
        # 2. Dividends as Cash (Held, not reinvested)
        hist['Cumulative Dividends Per Share'] = hist['Dividends'].cumsum()
        hist['Dividends as Cash'] = hist['Price Only'] + (hist['Cumulative Dividends Per Share'] * initial_shares)
        
        # 3. Reinvested Dividends (DRIP)
        current_shares = initial_shares
        dr_shares_series = [current_shares]
        
        # Loop through days to calculate fractional share accumulation on ex-div dates
        for i in range(1, len(hist)):
            div_paid = hist['Dividends'].iloc[i] * current_shares
            if div_paid > 0:
                # Buy more shares at that day's closing price
                current_shares += (div_paid / hist['Close'].iloc[i])
            dr_shares_series.append(current_shares)
            
        hist['DRIP Shares'] = dr_shares_series
        hist['Reinvested Dividends'] = hist['Close'] * hist['DRIP Shares']
        
        # Build the Plotly chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Price Only'], mode='lines', name='Price Only', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Dividends as Cash'], mode='lines', name='+ Dividends as Cash', line=dict(color='orange')))
        fig.add_trace(go.Scatter(x=hist.index, y=hist['Reinvested Dividends'], mode='lines', name='+ Reinvested Dividends (Total Return)', line=dict(color='green')))
        
        fig.update_layout(
            title=f"{ticker} — Growth of ${initial_investment:,.2f}",
            yaxis_title="Portfolio Value ($)",
            xaxis_title="Date",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)