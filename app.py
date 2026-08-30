import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Streamlit Page Configuration
st.set_page_config(page_title="Total Return Comparison", layout="wide")
st.title("ETF & Stock Total Return Comparison (DRIP)")
st.markdown("Compare the fully reinvested dividend (DRIP) performance of multiple tickers over their common available history.")

# Sidebar Inputs
st.sidebar.header("Configuration")
tickers_input = st.sidebar.text_input(
    "Enter Tickers (comma-separated)", 
    "HYLD.TO, USCL.TO, TXF.TO"
)
initial_investment = st.sidebar.number_input("Initial Investment ($)", value=10000, step=1000)

if tickers_input:
    tickers = [t.strip().upper() for t in tickers_input.split(",") if t.strip()]
    
    raw_data = {}
    with st.spinner("Fetching historical data from Yahoo Finance..."):
        for ticker in tickers:
            tkr = yf.Ticker(ticker)
            try:
                hist = tkr.history(period="max", auto_adjust=False, actions=True)
                if not hist.empty:
                    if 'Dividends' not in hist.columns:
                        hist['Dividends'] = 0.0
                    if hist.index.tz is not None:
                        hist.index = hist.index.tz_localize(None)
                    raw_data[ticker] = hist[['Close', 'Dividends']].copy()
                else:
                    st.warning(f"⚠️ No data found for {ticker}.")
            except Exception as e:
                st.error(f"Failed to fetch {ticker}: {e}")

    if raw_data:
        # Determine the common start date (latest inception among selected tickers)
        start_dates = [df.index.min() for df in raw_data.values()]
        common_start_date = max(start_dates)
        
        st.info(f"🗓️ **Common Available Period:** Aligned starting from **{common_start_date.strftime('%Y-%m-%d')}** (inception date of the newest selected ticker).")
        
        drip_comparison = {}

        for ticker, hist in raw_data.items():
            hist = hist[hist.index >= common_start_date].copy()
            if hist.empty:
                continue
            
            # Calculate DRIP performance
            initial_price = hist['Close'].iloc[0]
            current_shares = initial_investment / initial_price
            dr_shares_series = [current_shares]
            
            for i in range(1, len(hist)):
                div_paid = hist['Dividends'].iloc[i] * current_shares
                if div_paid > 0:
                    current_shares += (div_paid / hist['Close'].iloc[i])
                dr_shares_series.append(current_shares)
                
            hist['DRIP Shares'] = dr_shares_series
            hist['Reinvested Dividends'] = hist['Close'] * hist['DRIP Shares']
            drip_comparison[ticker] = hist['Reinvested Dividends']

        # Standalone Comparison Plot
        if drip_comparison:
            st.subheader("📊 Portfolio Value Over Time (DRIP)")
            
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
                title=f"Growth of ${initial_investment:,.2f} with Dividends Reinvested",
                yaxis_title="Portfolio Value ($)",
                xaxis_title="Date",
                hovermode="x unified",
                height=600,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(comp_fig, use_container_width=True)
        else:
            st.warning("No valid data remaining after date alignment.")
    else:
        st.error("Could not fetch data for any of the entered tickers.")
