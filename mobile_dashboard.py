import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Alpha Screener V5", layout="centered")

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
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        white-space: pre-wrap;
        background-color: #333;
        border-radius: 8px 8px 0 0;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0068C9;
    }
    .stMetric {
        background-color: #2a2a2a;
        padding: 10px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔥 Alpha Screener V5")

# --- NIFTY 100 STOCK LIST (FOR SCREENER) ---
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

# --- THE "BRAIN" - UPGRADED ANALYSIS FUNCTION ---
@st.cache_data(ttl=900)  # Cache data for 15 minutes
def analyze_ticker(symbol, mode='screener'):
    try:
        df = yf.download(symbol, period="9mo", interval="1d", progress=False) # 9mo for 200SMA
        if df.empty: return None

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- ALL INDICATORS ---
        sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        rsi = ta.rsi(df['Close'], length=14)
        macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
        sma_50 = ta.sma(df['Close'], length=50)
        sma_200 = ta.sma(df['Close'], length=200)

        if sti is None or adx is None or rsi is None or macd is None: return None

        # Append all indicators to the DataFrame
        df['ST_DIR'] = sti[sti.columns[1]]
        df['ST_VAL'] = sti[sti.columns[0]]
        df['ADX'] = adx['ADX_14']
        df['RSI'] = rsi
        df = pd.concat([df, macd], axis=1) # Adds MACD, MACDh, MACDs
        df['SMA_50'] = sma_50
        df['SMA_200'] = sma_200
        
        # Drop NaN values for clean calcs
        df.dropna(inplace=True)
        
        if df.empty: return None # Handle case where all data was NaN

        # --- LATEST VALUES ---
        latest = df.iloc[-1]
        current_price = float(latest['Close'])
        st_dir = int(latest['ST_DIR'])
        st_val = float(latest['ST_VAL'])
        adx_val = float(latest['ADX'])

        # --- SCREENER MODE (FAST) ---
        if mode == 'screener':
            st_previous = int(df.iloc[-2]['ST_DIR'])
            is_crossover = (st_dir == 1 and st_previous == -1)
            signal = "WAIT"
            
            if (st_dir == 1) and (adx_val > 25):
                signal = "BUY"
            
            return {
                "symbol": symbol, "price": current_price, "signal": signal,
                "adx": adx_val, "crossover": is_crossover
            }

        # --- MANUAL MODE (DETAILED) ---
        elif mode == 'manual':
            signal, reason, color = "WAIT", "Sideways", "gray"
            stop_loss, target = 0.0, 0.0

            if adx_val < 25:
                reason = f"Sideways (ADX {adx_val:.1f})"
            else:
                if st_dir == 1: # BUY SIGNAL
                    signal, reason, color = "BUY", f"Strong Uptrend (ADX {adx_val:.1f})", "green"
                    stop_loss = st_val
                    risk = current_price - stop_loss
                    if risk > 0:
                        target = current_price + (risk * 1.5) # 1.5R Target
                elif st_dir == -1: # SELL SIGNAL
                    signal, reason, color = "SELL", f"Strong Downtrend (ADX {adx_val:.1f})", "red"
                    stop_loss = st_val
                    risk = stop_loss - current_price
                    if risk > 0:
                        target = current_price - (risk * 1.5) # 1.5R Target
            
            # Create full analysis dictionary
            analysis = {
                "symbol": symbol, "price": current_price, "signal": signal,
                "reason": reason, "color": color, "adx": adx_val,
                "stop_loss": stop_loss, "target": target, "df": df,
                "rsi": float(latest['RSI']),
                "sma_50": float(latest['SMA_50']),
                "sma_200": float(latest['SMA_200']),
                "macd": float(latest[macd.columns[0]]), # MACD line
                "macd_s": float(latest[macd.columns[2]]) # Signal line
            }
            return analysis

    except Exception as e:
        st.error(f"Error processing {symbol}: {e}")
        return None

# --- UI TABS ---
tab1, tab2 = st.tabs(["🔥 NIFTY 100 Screener", "📊 Full Analysis"])

# --- TAB 1: NIFTY 100 SCREENER ---
with tab1:
    st.subheader("Find Top 5 'BUY' Signals")
    st.caption("Scans 100 stocks for Supertrend + ADX > 25. This will take 2-3 minutes.")
    
    if st.button("🚀 SCAN NIFTY 100"):
        progress_bar = st.progress(0, text="Initializing scan...")
        all_results = []
        total_stocks = len(NIFTY_100_TICKERS)
        
        for i, ticker in enumerate(NIFTY_100_TICKERS):
            progress_bar.progress((i + 1) / total_stocks, text=f"Analyzing: {ticker}")
            data = analyze_ticker(ticker, mode='screener')
            if data and data['signal'] == "BUY":
                all_results.append(data)
        
        progress_bar.empty()

        sorted_results = sorted(all_results, key=lambda x: (x['crossover'], x['adx']), reverse=True)
        top_5 = sorted_results[:5]
        
        st.subheader(f"🔥 Top {len(top_5)} Signals:")
        if not top_5:
            st.warning("No strong 'BUY' signals found in the NIFTY 100 right now.")
        
        for res in top_5:
            with st.container(border=True):
                if res['crossover']:
                    st.success(f"**{res['symbol']} (NEW CROSSOVER!)**")
                else:
                    st.markdown(f"**{res['symbol']}**")
                c1, c2 = st.columns(2)
                c1.metric("Price", f"₹{res['price']:.1f}")
                c2.metric("ADX (Strength)", f"₹{res['adx']:.1f}")

# --- TAB 2: FULL ANALYSIS ---
with tab2:
    st.subheader("Get Detailed Stock Analysis")
    manual_ticker = st.text_input("Enter any symbol (e.g., ZOMATO.NS)", "").upper()
    
    if st.button("Analyze Stock", key="manual_analyze"):
        if not manual_ticker:
            st.error("Please enter a stock symbol.")
        else:
            with st.spinner(f"Analyzing {manual_ticker}..."):
                data = analyze_ticker(manual_ticker, mode='manual')
                
                if data:
                    # --- 1. Signal Card ---
                    st.markdown(f"""
                        <div style="text-align: center; padding: 15px; background-color: {data['color']}; color: white; border-radius: 10px; margin-bottom: 20px;">
                            <h1 style='margin:0; font-size: 40px;'>{data['signal']}</h1>
                            <p style='margin:0;'>{data['reason']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # --- 2. Actionable Levels ---
                    st.markdown("---")
                    st.subheader("Actionable Levels")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("Entry Price", f"₹{data['price']:.2f}")
                    if data['signal'] != "WAIT":
                        c2.metric("Stop Loss (SL)", f"₹{data['stop_loss']:.2f}", delta_color="inverse")
                        c3.metric("Target (1.5R)", f"₹{data['target']:.2f}", delta_color="normal")
                    else:
                        c2.metric("Stop Loss", "N/A")
                        c3.metric("Target", "N/A")

                    # --- 3. Indicator Dashboard ---
                    st.markdown("---")
                    st.subheader("Indicator Dashboard")
                    
                    # Row 1: RSI & ADX
                    col1, col2 = st.columns(2)
                    col1.metric("RSI (14)", f"{data['rsi']:.2f}")
                    col2.metric("ADX (14)", f"{data['adx']:.2f}")
                    
                    # Row 2: Trend
                    col3, col4 = st.columns(2)
                    sma_delta = f"₹{(data['price'] - data['sma_50']):.2f} vs 50SMA"
                    col3.metric("Price vs 50SMA", "ABOVE" if data['price'] > data['sma_50'] else "BELOW", delta=sma_delta)
                    sma_delta_200 = f"₹{(data['price'] - data['sma_200']):.2f} vs 200SMA"
                    col4.metric("Price vs 200SMA", "ABOVE" if data['price'] > data['sma_200'] else "BELOW", delta=sma_delta_200)

                    # --- 4. Charts ---
                    st.markdown("---")
                    st.subheader("Charts")
                    
                    df_chart = data['df']
                    
                    with st.expander("Price + Supertrend + SMAs"):
                        st.line_chart(df_chart[['Close', 'ST_VAL', 'SMA_50', 'SMA_200']].tail(150)) # Last 150 days

                    with st.expander("RSI (Relative Strength Index)"):
                        st.line_chart(df_chart['RSI'].tail(150))
                        
                    with st.expander("ADX (Trend Strength)"):
                        st.line_chart(df_chart['ADX'].tail(150))

                    with st.expander("MACD (Moving Average Convergence Divergence)"):
                        st.line_chart(df_chart[[macd.columns[0], macd.columns[2]]].tail(150)) # MACD & Signal
                        st.bar_chart(df_chart[macd.columns[1]].tail(150)) # Histogram
                
                else:
                    st.error(f"Could not fetch data for {manual_ticker}. Check symbol or data availability.")

st.caption("Disclaimer: Delayed data. For educational use only. Do not trade real money.")
