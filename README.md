# ETF & Stock Total Return Calculator

A Streamlit web application that calculates and visualizes the total return of stocks and ETFs over time, comparing three return scenarios: price appreciation only, dividends held as cash, and fully reinvested dividends (DRIP).

## Overview

This tool helps investors understand the impact of dividend reinvestment on their portfolio returns. By comparing three scenarios:

1. **Price Only** - Capital gains from price appreciation
2. **Dividends as Cash** - Capital gains + dividends kept as cash (not reinvested)
3. **Reinvested Dividends (DRIP)** - Total return including dividend reinvestment for compounding effect

## Features

- **Multi-Ticker Support** - Compare multiple stocks/ETFs simultaneously
- **Flexible Date Range** - Analyze performance over any custom time period
- **Customizable Investment Amount** - See results for any initial investment
- **Interactive Charts** - Plotly-based visualization with hover details
- **Automatic Dividend Calculation** - Accurately calculates dividend payouts and reinvestment
- **Fractional Share Support** - Handles dividend reinvestment as fractional shares

## Requirements

- Python 3.7+
- streamlit
- yfinance
- pandas
- plotly

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd total-return
```

2. Install dependencies:
```bash
pip install streamlit yfinance pandas plotly
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run app.py
```

2. The app will open in your browser at `http://localhost:8501`

3. Configure your analysis in the sidebar:
   - **Enter Tickers** - Comma-separated list of stock/ETF symbols (e.g., `LMAX.TO, TXF.TO, ZWC.TO`)
   - **Start Date** - Beginning of the analysis period
   - **End Date** - End of the analysis period
   - **Initial Investment** - Amount to invest (default: $10,000)

4. Click **Calculate Performance** to generate the analysis

## How It Works

- **Price Only**: Calculates portfolio value based solely on price changes
- **Dividends as Cash**: Adds cumulative dividends to portfolio value without reinvesting
- **Reinvested Dividends (DRIP)**: Automatically reinvests dividends to purchase additional shares at ex-dividend date prices, demonstrating the power of compounding

## Example

With $10,000 invested in `LMAX.TO` from 2020-01-01 to today, the app shows how much more you'd have if you reinvested dividends versus holding them as cash.

## Data Source

Historical stock and ETF data is fetched from Yahoo Finance via the `yfinance` library, including:
- Adjusted and unadjusted prices
- Dividend amounts and ex-dividend dates
- Historical trading data