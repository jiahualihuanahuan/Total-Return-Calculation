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
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    # Store processed data for individual and comparison charts
    drip_comparison = {}
    individual_histories = {}

    for ticker in tickers:
        tkr = yf.Ticker(ticker)
        try:
            hist = tkr.history(period="max", auto_adjust=False, actions=True)
        except Exception as e:
            st.error(f"Failed to download data for {ticker}: {e}")
            continue
            
        if hist.empty:
            st.warning(f"No pricing data found for {ticker}.")
            continue
            
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
        
        for i in range(1, len(hist)):
            div_paid = hist['Dividends'].iloc[i] * current_shares
            if div_paid > 0:
                current_shares += (div_paid / hist['Close'].iloc[i])
            dr_shares_series.append(current_shares)
            
        hist['DRIP Shares'] = dr_shares_series
        hist['Reinvested Dividends'] = hist['Close'] * hist['DRIP Shares']
        
        # Save results
        drip_comparison[ticker] = hist['Reinvested Dividends']
        individual_histories[ticker] = hist

    # --- Comparison Section ---
    if len(drip_comparison) > 1:
        st.header("📊 Total Return Comparison (DRIP)")
        
        comp_fig = go.Figure()
        for ticker, series in drip_comparison.items():
            comp_fig.add_trace(go.Scatter(
                x=series.index, 
                y=series, 
                mode='lines', 
                name=ticker
            ))
            
        comp_fig.update_layout(
            title=f"Total Return Comparison — Growth of ${initial_investment:,.2f}",
            yaxis_title="Portfolio Value ($)",
            xaxis_title="Date",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(comp_fig, use_container_width=True)
        st.divider()

    # --- Individual Breakdowns ---
    for ticker, hist in individual_histories.items():
        st.subheader(f"Performance Breakdown: {ticker}")
        
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
