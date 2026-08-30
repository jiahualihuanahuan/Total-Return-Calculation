# 📈 ETF & Stock Total Return Calculator (DRIP)

A powerful, interactive Streamlit web application designed to visualize the true total return of stocks and ETFs. 

While most financial charts default to showing simple price action, this tool calculates and compares three distinct investment strategies over time:
1. **Price Only:** The standard chart of the asset's underlying price.
2. **Dividends as Cash:** The asset's price plus the cumulative total of uninvested dividend payouts.
3. **Reinvested Dividends (DRIP):** The true total return, simulating the compounding effect of automatically using dividend payouts to purchase fractional shares at that day's closing price.

## ✨ Key Features

* **⚖️ Fair Comparison Engine:** When comparing multiple tickers, the app automatically finds the **common available period**. It aligns all calculations to the inception date of the *newest* fund in your list, ensuring a 1:1 "apples-to-apples" comparison and preventing older funds from showing an unfair compounding advantage.
* **📊 Interactive Plotly Charts:** Features a unified, hoverable comparison chart for DRIP returns across all selected tickers, alongside detailed drop-down breakdowns for each individual asset.
* **🇨🇦 Quick-Select Presets:** Built-in sidebar buttons for popular high-yield Canadian Covered Call ETFs (e.g., HYLD, HDIV, USCL).
* **🌐 Global Ticker Support:** Powered by Yahoo Finance, supporting US equities (e.g., `SPY`, `AAPL`) and international markets via standard suffixes (e.g., `.TO` for TSX).

## 🚀 Installation & Setup

To run this application locally, you will need Python installed on your machine. 

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/Total-Return-Calculation.git](https://github.com/yourusername/Total-Return-Calculation.git)
   cd Total-Return-Calculation
