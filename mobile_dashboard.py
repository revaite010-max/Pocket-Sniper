import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="NIFTY 100 Screener", layout="centered")

# --- CSS STYLING ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    div.block-container {padding-top: 1rem;} 
    .stButton>button {
        width: 100%;
        font-weight: bold;
        border-radius: 10px;
        background-color: #4CAF50; /* Green */
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 NIFTY 100 Screener")

# --- NIFTY 100 STOCK LIST ---
# This is our "universe". We will scan all of them.
NIFTY_100_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", 
    "SBIN.NS", "INFY.NS", "LICI.NS", "HINDUNILVR.NS", "ITC.NS", "LT.NS", 
    "BAJFINANCE.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS", 
    "KOTAKBANK.NS", "TITAN.NS", "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS", 
    "AXISBANK.NS", "DMART.NS", "ADANIPORTS.NS", "ASIANPAINT.NS", "ADANIPOWER.NS", 
    "NESTLEIND.NS", "BAJAJFINSV.NS", "WIPRO.NS", "M&M.NS", "POWERGRID.NS", 
    "ULTRACEMCO.NS", "COALINDIA.NS", "IOC.NS", "JSWSTEEL.NS", "TATASTEEL.NS", 
    "VEDL.NS", "INDUSINDBK.NS", "GRASIM.NS", "PIDILITIND.NS", "SIEMENS.NS", 
    "SBILIFE.NS", "BPCL.NS", "HINDALCO.NS", "TECHM.NS", "EICHERMOT.NS", 
    "GAIL.NS", "HDFCLIFE.NS", "DIVISLAB.NS", "CIPLA.NS", "ABB.NS", "LTIM.NS", 
    "BAJAJ-AUTO.NS", "TRENT.NS", "PFC.NS", "CHOLAFIN.NS", "SHRIRAMFIN.NS", 
    "DRREDDY.NS", "HEROMOTOCO.NS", "ZOMATO.NS", "HINDZINC.NS", "HAL.NS", 
    "BRITANNIA.NS", "REC.NS", "TATACONSUM.NS", "SHREECEM.NS", "APOLLOHOSP.NS", 
    "INDIGO.NS", "BEL.NS", "TATAPOWER.NS", "BANKBARODA.NS", "GODREJCP.NS", 
    "BOSCHLTD.NS", "ICICIPRULI.NS", "ICICILOMB.NS", "HAVELLS.NS", "PNB.NS", 
    "INDUSTOWER.NS", "MANKIND.NS", "MARICO.NS", "AMBUJACEM.NS", 
    "AUROPHARMA.NS", "COLPAL.NS", "LUPIN.NS", "MUTHOOTFIN.NS", "PATANJALI.NS", 
    "UPL.NS", "ACC.NS", "DLF.NS", "GLAND.NS", "JUBLFOOD.NS", "PGHH.NS", 
    "TORRENTPOWER.NS", "NMDC.NS", "SAMVARDHANA.NS", "BERGEPAINT.NS", 
    "CANBK.NS", "MRF.NS", "NYKAA.NS", "TIINDIA.NS"
]

# --- THE BRAIN (LOGIC) ---
@st.cache_data(ttl=900)  # Cache data for 15 minutes
def analyze_ticker(symbol):
    try:
        df = yf.download(symbol, period="3mo", interval="1d", progress=False)
        if df.empty: return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # 1. Supertrend (7, 3)
        sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
        if sti is None or sti.empty: return None
        df['ST_DIR'] = sti[sti.columns[1]]

        # 2. ADX (14)
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        if adx is None or adx.empty: return None
        df['ADX'] = adx['ADX_14']

        # Get Latest Values
        current_price = float(df['Close'].iloc[-1])
        st_dir = int(df['ST_DIR'].iloc[-1])
        adx_val = float(df['ADX'].iloc[-1])
        
        # Check if this is a NEW crossover
        st_previous = int(df['ST_DIR'].iloc[-2])
        is_crossover = (st_dir == 1 and st_previous == -1)

        # DEFINE SIGNALS
        signal = "WAIT"
        
        # BUY LOGIC: Supertrend must be UP (1) AND Trend must be strong (ADX > 25)
        if (st_dir == 1) and (adx_val > 25):
            signal = "BUY"
        
        return {
            "symbol": symbol,
            "price": current_price,
            "signal": signal,
            "adx": adx_val,
            "crossover": is_crossover
        }
    except Exception as e:
        return None

# --- UI ---
if st.button("🚀 SCAN NIFTY 100"):
    
    progress_bar = st.progress(0, text="Initializing scan...")
    st.markdown("---")
    
    all_results = []
    total_stocks = len(NIFTY_100_TICKERS)
    
    for i, ticker in enumerate(NIFTY_100_TICKERS):
        progress_bar.progress((i + 1) / total_stocks, text=f"Analyzing: {ticker}")
        data = analyze_ticker(ticker)
        if data and data['signal'] == "BUY":
            all_results.append(data)
    
    progress_bar.empty()

    # --- RANKING ---
    # Sort by ADX (strongest trend) first, then by Crossover (new signals)
    sorted_results = sorted(all_results, key=lambda x: (x['crossover'], x['adx']), reverse=True)
    
    top_5 = sorted_results[:5]
    
    st.subheader(f"🔥 Top {len(top_5)} Signals:")
    
    if not top_5:
        st.warning("No strong 'BUY' signals found in the NIFTY 100 right now.")
    
    for res in top_5:
        color = "🟢" if res['signal'] == "BUY" else "🔴"
        
        container = st.container(border=True)
        container.markdown(f"### {color} {res['symbol']}")
        
        c1, c2 = container.columns(2)
        c1.metric("Price", f"₹{res['price']:.1f}")
        c2.metric("ADX (Strength)", f"{res['adx']:.1f}")
        
        if res['crossover']:
            container.success("NEW CROSSOVER SIGNAL!")

st.caption("Disclaimer: Delayed data. For educational use only.")
