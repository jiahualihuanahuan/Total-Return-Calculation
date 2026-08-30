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
    drip_comparison = {}

    with st.spinner("Fetching historical data..."):
        for ticker in tickers:
            tkr = yf.Ticker(ticker)
            try:
                hist = tkr.history(period="max", auto_adjust=False, actions=True)
                
                if not hist.empty:
                    if 'Dividends' not in hist.columns:
                        hist['Dividends'] = 0.0
                        
                    # Safely handle timezones
                    if hist.index.tz is not None:
                        hist.index = hist.index.tz_localize(None)
                    
                    # Calculate DRIP
                    initial_price = hist['Close'].iloc[0]
                    current_shares = initial_investment / initial_price
                    dr_shares_series = [current_shares]
                    
                    for i in range(1, len(hist)):
                        div_paid = hist['Dividends'].iloc[i] * current_shares
                        if div_paid > 0:
                            current_shares += (div_paid / hist['Close'].iloc[i])
                        dr_shares_series.append(current_shares)
                        
                    hist['DRIP Shares'] = dr_shares_series
                    drip_comparison[ticker] = hist['Close'] * hist['DRIP Shares']
                else:
                    st.warning(f"⚠️ No data found for {ticker}")
            except Exception as e:
                st.error(f"Failed to fetch {ticker}: {e}")

    # Draw the plot as long as we have AT LEAST ONE ticker
    if drip_comparison:
        st.subheader("📊 Portfolio Value Over Time (DRIP)")
        comp_fig = go.Figure()
        
        for ticker, series in drip_comparison.items():
            comp_fig.add_trace(go.Scatter(
                x=series.index, 
                y=series, 
                mode='lines', 
                name=ticker
            ))
            
        comp_fig.update_layout(
            title=f"Growth of ${initial_investment:,.2f} with Dividends Reinvested",
            yaxis_title="Portfolio Value ($)",
            xaxis_title="Date",
            hovermode="x unified",
            height=600,
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(comp_fig, use_container_width=True)f the entered tickers.")
