import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- MOBILE CONFIG ---
st.set_page_config(page_title="Mobile Alpha", layout="centered") # "Centered" looks better on phones

# --- CSS HACKS FOR PHONES ---
# This hides the hamburger menu and footer to make it look like an app
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div.block-container {padding-top: 1rem;} 
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.title("📱 Pocket Scanner")

# --- INPUTS ---
# predefined list for faster mobile typing
default_tickers = ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "TATAMOTORS.NS", "SBIN.NS", "ADANIENT.NS"]
ticker = st.selectbox("Select Asset", default_tickers)
custom_ticker = st.text_input("Or type symbol (e.g. ZOMATO.NS)", "")
if custom_ticker:
    ticker = custom_ticker

def calculate_levels(df):
    # Get latest data
    current_price = df['Close'].iloc[-1]
    
    # Strategy Components
    sma_50 = df['SMA_50'].iloc[-1]
    rsi = df['RSI'].iloc[-1]
    vol_current = df['Volume'].iloc[-1]
    vol_avg = df['VOL_SMA'].iloc[-1]
    
    # Logic
    signal = "WAIT"
    color = "gray"
    stop_loss = 0.0
    target = 0.0
    reason = "No Setup"

    # BUY LOGIC
    if (current_price > sma_50) and (rsi > 50) and (vol_current > vol_avg):
        signal = "BUY"
        color = "green"
        # Swing Low SL: Lowest low of last 5 candles
        stop_loss = df['Low'].tail(5).min()
        risk = current_price - stop_loss
        target = current_price + (risk * 1.5)
        reason = "Trend Up + Momentum + Vol"

    # SELL LOGIC
    elif (current_price < sma_50) and (rsi < 50):
        signal = "SELL"
        color = "red"
        # Swing High SL
        stop_loss = df['High'].tail(5).max()
        risk = stop_loss - current_price
        target = current_price - (risk * 1.5)
        reason = "Trend Down + Momentum Lost"
        
    return signal, color, current_price, stop_loss, target, reason, rsi

if st.button("SCAN NOW", use_container_width=True):
    with st.spinner('Fetching Data...'):
        try:
            # Fetch Data (3 months to get valid 50 SMA)
            df = yf.download(ticker, period="3mo", interval="1d", progress=False)
            
            if df.empty:
                st.error("Invalid Symbol")
            else:
                # Calculate Indicators
                df['SMA_50'] = ta.sma(df['Close'], length=50)
                df['RSI'] = ta.rsi(df['Close'], length=14)
                df['VOL_SMA'] = ta.sma(df['Volume'], length=20)
                
                # Run Logic
                signal, color, price, sl, tgt, reason, rsi = calculate_levels(df)
                
                # --- DISPLAY UI (MOBILE OPTIMIZED) ---
                # Huge Signal Card
                st.markdown(f"""
                    <div style="text-align: center; padding: 10px; background-color: {color}; color: white; border-radius: 10px;">
                        <h1 style='margin:0;'>{signal}</h1>
                        <p style='margin:0;'>{reason}</p>
                    </div>
                    <br>
                """, unsafe_allow_html=True)

                # Data Grid
                c1, c2 = st.columns(2)
                c1.metric("Entry", f"₹{price:.1f}")
                c2.metric("RSI", f"{rsi:.1f}")
                
                c3, c4 = st.columns(2)
                if signal != "WAIT":
                    c3.metric("Target", f"₹{tgt:.1f}", delta=f"{((tgt-price)/price)*100:.1f}%")
                    c4.metric("Stop Loss", f"₹{sl:.1f}", delta=f"-{((price-sl)/price)*100:.1f}%", delta_color="inverse")
                
                # Hidden Chart (Expand to see)
                with st.expander("See Chart"):
                    st.line_chart(df['Close'])

        except Exception as e:
            st.error(f"Error: {e}")

