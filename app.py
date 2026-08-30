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

# Calculate automatically whenever tickers exist in the text box
if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    # 1. Fetch raw data first to determine the common start date
    raw_data = {}
    with st.spinner("Fetching data from Yahoo Finance..."):
        for ticker in tickers:
            tkr = yf.Ticker(ticker)
            try:
                hist = tkr.history(period="max", auto_adjust=False, actions=True)
                if not hist.empty:
                    if 'Dividends' not in hist.columns:
                        hist['Dividends'] = 0.0
                    
                    # Remove timezone info to prevent plotting alignment issues
                    hist.index = hist.index.tz_localize(None) 
                    raw_data[ticker] = hist[['Close', 'Dividends']].copy()
                else:
                    st.warning(f"⚠️ No pricing data found for {ticker}. It will be excluded.")
            except Exception as e:
                st.error(f"Failed to download data for {ticker}: {e}")

    # 2. Proceed only if we have valid data
    if raw_data:
        # Find the latest start date among all valid tickers for a fair comparison
        start_dates = [df.index.min() for df in raw_data.values()]
        common_start_date = max(start_dates)
        
        st.info(f"🗓️ **Fair Comparison Mode:** All calculations are aligned to start on **{common_start_date.strftime('%Y-%m-%d')}** (the inception date of the newest selected fund).")
        
        drip_comparison = {}
        individual_histories = {}

        # 3. Process each ticker from the common start date
        for ticker, hist in raw_data.items():
            # Slice the dataframe to only include data from the common start date onwards
            hist = hist[hist.index >= common_start_date].copy()
            
            if hist.empty:
                continue
                
            # --- Perform Calculations ---
            initial_price = hist['Close'].iloc[0]
            initial_shares = initial_investment / initial_price
            hist['Price Only'] = hist['Close'] * initial_shares
            
            hist['Cumulative Dividends Per Share'] = hist['Dividends'].cumsum()
            hist['Dividends as Cash'] = hist['Price Only'] + (hist['Cumulative Dividends Per Share'] * initial_shares)
            
            current_shares = initial_shares
            dr_shares_series = [current_shares]
            
            for i in range(1, len(hist)):
                div_paid = hist['Dividends'].iloc[i] * current_shares
                if div_paid > 0:
                    current_shares += (div_paid / hist['Close'].iloc[i])
                dr_shares_series.append(current_shares)
                
            hist['DRIP Shares'] = dr_shares_series
            hist['Reinvested Dividends'] = hist['Close'] * hist['DRIP Shares']
            
            drip_comparison[ticker] = hist['Reinvested Dividends']
            individual_histories[ticker] = hist

        # --- COMPARISON SECTION (Always shows if at least 1 valid ticker exists) ---
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
            title=f"Total Return (DRIP) Comparison — Growth of ${initial_investment:,.2f}",
            yaxis_title="Portfolio Value ($)",
            xaxis_title="Date",
            hovermode="x unified",
            margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(comp_fig, use_container_width=True)
        st.divider()

        # --- INDIVIDUAL BREAKDOWNS ---
        for ticker, hist in individual_histories.items():
            with st.expander(f"🔍 Detailed Breakdown: {ticker}", expanded=False):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Price Only'], mode='lines', name='Price Only', line=dict(color='blue')))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Dividends as Cash'], mode='lines', name='+ Dividends as Cash', line=dict(color='orange')))
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Reinvested Dividends'], mode='lines', name='+ Reinvested Dividends', line=dict(color='green')))
                
                fig.update_layout(
                    title=f"{ticker} Internal Growth Dynamics",
                    yaxis_title="Portfolio Value ($)",
                    xaxis_title="Date",
                    hovermode="x unified",
                    margin=dict(l=0, r=0, t=40, b=0)
                )
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.error("Could not fetch data for any of the selected tickers.")
