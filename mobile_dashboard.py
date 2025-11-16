import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Alpha Screener", layout="centered")

# --- PRO UI STYLING (V5.5) ---
st.markdown("""
    <style>
    /* ... (All CSS from V5.5 is unchanged) ... */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    body, .stApp, .stButton>button, .stTextInput>div>div>input, .stSelectbox>div>div>div {
        font-family: 'Inter', sans-serif;
    }
    body { background-color: #F0F2F6; }
    .stApp { background-color: #F0F2F6; }
    #MainMenu, footer { visibility: hidden; }
    div.block-container { padding: 1rem 1rem 2rem 1rem; }
    .card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        margin-bottom: 12px;
    }
    .card h3 {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 15px 0;
    }
    .card p {
        font-size: 14px;
        color: #4B5563;
        margin-bottom: 5px;
    }
    .stButton>button {
        width: 100%;
        font-weight: 600;
        border-radius: 8px;
        background-color: #0068C9;
        color: white;
        border: none;
        padding: 10px 0;
    }
    .stButton>button:hover {
        background-color: #0058AD;
        color: white;
    }
    .stTextInput>div>div>input {
        background-color: #FFFFFF;
        border-radius: 8px;
        border: 1px solid #D1D5DB;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #E5E7EB;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        padding: 0 10px;
        background-color: transparent;
        border-bottom: 2px solid transparent;
        color: #6B7280;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: transparent;
        border-bottom: 2px solid #0068C9;
        color: #0068C9;
        font-weight: 600;
    }
    .signal-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 16px;
    }
    .signal-buy { background-color: #ECFDF5; }
    .signal-sell { background-color: #FEF2F2; }
    .signal-wait { background-color: #F9FAFB; }
    
    .signal-card h1 {
        font-size: 36px;
        font-weight: 700;
        margin: 0 0 5px 0;
    }
    .signal-buy h1 { color: #10B981; }
    .signal-sell h1 { color: #EF4444; }
    .signal-wait h1 { color: #6B7280; }
    
    .signal-card p {
        font-size: 14px;
        font-weight: 500;
        margin: 0;
    }
    .signal-buy p { color: #059669; }
    .signal-sell p { color: #DC2626; }
    .signal-wait p { color: #4B5563; }
    
    .metric-box {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-box h4 {
        font-size: 12px;
        font-weight: 500;
        color: #6B7280;
        margin: 0 0 5px 0;
        text-transform: uppercase;
    }
    .metric-box p {
        font-size: 18px;
        font-weight: 600;
        color: #111827;
        margin: 0;
    }
    .metric-box-green p { color: #10B981; }
    .metric-box-red p { color: #EF4444; }
    
    .st-expander-header {
        background-color: #FFFFFF;
        border-radius: 12px;
        font-size: 16px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }
    .st-expander-body {
        background-color: #FFFFFF;
        border-bottom-left-radius: 12px;
        border-bottom-right-radius: 12px;
        padding-top: 0px;
        margin-top: -10px;
    }
    /* --- News Link Style --- */
    .news-item {
        font-size: 13px;
        line-height: 1.5;
        margin-bottom: 10px;
        padding-bottom: 10px;
        border-bottom: 1px solid #F0F2F6;
    }
    .news-item a {
        text-decoration: none;
        font-weight: 600;
        color: #111827;
    }
    .news-item a:hover {
        color: #0068C9;
    }
    .news-item span {
        font-size: 12px;
        color: #6B7280;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Alpha Screener V6.1")

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

# --- THE "BRAIN" - V6.1 (FUNCTIONAL UPDATE) ---
@st.cache_data(ttl=900)  # Cache data for 15 minutes
def analyze_ticker(symbol, mode='screener'):
    try:
        # --- TECHNICAL DATA (FAST) ---
        df = yf.download(symbol, period="2y", interval="1d", progress=False) 
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
        adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
        rsi = ta.rsi(df['Close'], length=14)
        fast_len, slow_len, sig_len = 12, 26, 9
        macd = ta.macd(df['Close'], fast=fast_len, slow=slow_len, signal=sig_len)
        macd_line_col = f"MACD_{fast_len}_{slow_len}_{sig_len}"
        macd_sig_col = f"MACDs_{fast_len}_{slow_len}_{sig_len}"
        sma_50 = ta.sma(df['Close'], length=50)
        sma_200 = ta.sma(df['Close'], length=200)

        df['ST_DIR'] = sti[sti.columns[1]]
        df['ST_VAL'] = sti[sti.columns[0]]
        df['ADX'] = adx['ADX_14']
        df['RSI'] = rsi
        df = pd.concat([df, macd], axis=1)
        df['SMA_50'] = sma_50
        df['SMA_200'] = sma_200
        
        df.dropna(inplace=True)
        if df.empty: return None 

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
            return {"symbol": symbol, "price": current_price, "signal": signal, "adx": adx_val, "crossover": is_crossover}

        # --- MANUAL MODE (HEAVY - V6.1 UPDATE) ---
        elif mode == 'manual':
            # --- FUNDAMENTAL & NEWS DATA (SLOWER) ---
            ticker_obj = yf.Ticker(symbol)
            info = ticker_obj.info
            
            # 1. Get Fundamentals
            fundamentals = {
                "pe": info.get("trailingPE"),
                "eps": info.get("forwardEPS"),
                "mcap": info.get("marketCap"),
                "sector": info.get("sector")
            }
            
            # 2. Get News
            headlines = []
            raw_news = ticker_obj.news
            if raw_news:
                for item in raw_news[:3]: # Get top 3
                    headlines.append({
                        "title": item.get('title'),
                        "link": item.get('link'),
                        "publisher": item.get('publisher')
                    })

            # --- TECHNICAL ANALYSIS (UNCHANGED) ---
            signal, reason, color_class = "WAIT", "Sideways", "wait"
            stop_loss, target = 0.0, 0.0
            summary_points = []
            
            if latest['Close'] > latest['SMA_50'] and latest['Close'] > latest['SMA_200']:
                summary_points.append("✅ **Trend:** Price is above both the 50-day and 200-day moving averages, confirming a strong long-term uptrend.")
            elif latest['Close'] > latest['SMA_50'] and latest['Close'] < latest['SMA_200']:
                summary_points.append("⚠️ **Trend:** Short-term uptrend (above 50-day) but in a long-term downtrend (below 200-day).")
            else:
                summary_points.append("❌ **Trend:** Price is below its key moving averages, signaling a clear downtrend.")

            rsi_val = float(latest['RSI'])
            if rsi_val > 70: summary_points.append(f"⚠️ **Momentum:** RSI is {rsi_val:.1f} (Overbought).")
            elif rsi_val > 50: summary_points.append(f"✅ **Momentum:** RSI is {rsi_val:.1f} (Bullish).")
            elif rsi_val < 30: summary_points.append(f"⚠️ **Momentum:** RSI is {rsi_val:.1f} (Oversold).")
            else: summary_points.append(f"❌ **Momentum:** RSI is {rsi_val:.1f} (Bearish).")
            
            if latest[macd_line_col] > latest[macd_sig_col]:
                summary_points.append("✅ **MACD:** The MACD line is above its signal line, reinforcing positive momentum.")
            else:
                summary_points.append("❌ **MACD:** The MACD line is below its signal line, indicating selling pressure.")

            if adx_val < 25:
                reason = f"Sideways (ADX {adx_val:.1f})"
                summary_points.append(f"⚠️ **Trend Strength:** The ADX is {adx_val:.1f}, indicating a weak or sideways market. **No clear trend.**")
            else:
                summary_points.append(f"✅ **Trend Strength:** The ADX is {adx_val:.1f}, confirming a **strong trend**.")

            if adx_val > 25:
                if st_dir == 1:
                    signal, reason, color_class = "BUY", f"Strong Uptrend (ADX {adx_val:.1f})", "buy"
                    stop_loss = st_val
                    risk = current_price - stop_loss
                    if risk > 0: target = current_price + (risk * 1.5)
                elif st_dir == -1:
                    signal, reason, color_class = "SELL", f"Strong Downtrend (ADX {adx_val:.1f})", "sell"
                    stop_loss = st_val
                    risk = stop_loss - current_price
                    if risk > 0: target = current_price - (risk * 1.5)
            
            final_summary = "\n\n".join(summary_points)
            
            analysis = {
                "symbol": symbol, "price": current_price, "signal": signal,
                "reason": reason, "color_class": color_class, "stop_loss": stop_loss, "target": target,
                "summary": final_summary,
                "fundamentals": fundamentals, # ADDED
                "headlines": headlines      # ADDED
            }
            return analysis

    except Exception as e:
        # st.error(f"Error in analyze_ticker: {e}") # Suppress for cleaner UI
        return None

# --- UI TABS ---
tab1, tab2 = st.tabs(["🔥 Screener", "📊 Full Analysis"])

# --- TAB 1: NIFTY 100 SCREENER (Unchanged from V6.0) ---
with tab1:
    st.markdown("### NIFTY 100 Screener")
    st.markdown("<p style='color: #4B5563; margin-top: -10px;'>Finds Top 5 'BUY' signals (Supertrend + ADX > 25).</p>", unsafe_allow_html=True)
    
    if st.button("🚀 SCAN NIFTY 100", key="scan_nifty"):
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
        
        st.markdown(f"### 🔥 Top {len(top_5)} Signals")
        if not top_5: st.warning("No strong 'BUY' signals found. Market is sideways.")
        
        for res in top_5:
            crossover_badge = " <span style='background-color: #DBEAFE; color: #1E40AF; padding: 2px 6px; border-radius: 5px; font-size: 10px; font-weight: 600;'>NEW</span>" if res['crossover'] else ""
            with st.expander(f"{res['symbol']}{crossover_badge}  |  Price: ₹{res['price']:.2f}  |  ADX: {res['adx']:.1f}"):
                with st.spinner(f"Loading details for {res['symbol']}..."):
                    data = analyze_ticker(res['symbol'], mode='manual')
                if data:
                    st.markdown(f"""
                        <div class='signal-card signal-{data['color_class']}'>
                            <h1>{data['signal']}</h1>
                            <p>{data['reason']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if data['signal'] != "WAIT":
                        st.markdown(f"""
                            <div class='card' style='margin-bottom: 0px;'>
                                <h3>Actionable Levels</h3>
                                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                                    <div class'metric-box'><h4>Entry Price</h4><p>₹{data['price']:.2f}</p></div>
                                    <div class='metric-box metric-box-red'><h4>Stop Loss (SL)</h4><p>₹{data['stop_loss']:.2f}</p></div>
                                    <div class='metric-box metric-box-green'><h4>Target (1.5R)</h4><p>₹{data['target']:.2f}</p></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                    st.markdown(f"""
                        <div class='card' style='margin-bottom: 0px; margin-top: 10px;'>
                            <h3>Technical Summary</h3>
                            <div style='font-size: 14px; color: #374151; line-height: 1.6;'>
                                {data['summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else: st.error("Could not load full analysis.")

# --- TAB 2: FULL ANALYSIS (V6.1 UPDATED) ---
with tab2:
    st.markdown("### Manual Stock Analysis")
    st.markdown("<p style='color: #4B5563; margin-top: -10px;'>Get a full technical summary for any stock.</p>", unsafe_allow_html=True)
    
    manual_ticker = st.text_input("Enter any symbol (e.g., ZOMATO.NS)", "").upper()
    
    if st.button("Analyze Stock", key="manual_analyze"):
        if not manual_ticker:
            st.error("Please enter a stock symbol.")
        else:
            with st.spinner(f"Analyzing {manual_ticker}... (This is now slower)"):
                data = analyze_ticker(manual_ticker, mode='manual')
                
                if data:
                    # --- 1. Signal Card ---
                    st.markdown(f"""
                        <div class='signal-card signal-{data['color_class']}'>
                            <h1>{data['signal']}</h1>
                            <p>{data['reason']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # --- 2. Actionable Levels ---
                    if data['signal'] != "WAIT":
                        st.markdown(f"""
                            <div class='card'>
                                <h3>Actionable Levels</h3>
                                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                                    <div class'metric-box'><h4>Entry Price</h4><p>₹{data['price']:.2f}</p></div>
                                    <div class='metric-box metric-box-red'><h4>Stop Loss (SL)</h4><p>₹{data['stop_loss']:.2f}</p></div>
                                    <div class='metric-box metric-box-green'><h4>Target (1.5R)</h4><p>₹{data['target']:.2f}</p></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    # --- 3. Technical Summary ---
                    st.markdown(f"""
                        <div class='card'>
                            <h3>Technical Summary</h3>
                            <div style='font-size: 14px; color: #374151; line-height: 1.6;'>
                                {data['summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # --- 4. KEY FUNDAMENTALS (NEW) ---
                    st.markdown(f"""
                        <div class='card'>
                            <h3>Key Fundamentals</h3>
                            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                                <div class'metric-box'>
                                    <h4>P/E Ratio</h4>
                                    <p>{data['fundamentals']['pe']:.2f if data['fundamentals']['pe'] else 'N/A'}</p>
                                </div>
                                <div class='metric-box'>
                                    <h4>Forward EPS</h4>
                                    <p>{data['fundamentals']['eps'] if data['fundamentals']['eps'] else 'N/A'}</p>
                                </div>
                                <div class='metric-box'>
                                    <h4>Market Cap</h4>
                                    <p>{f"{(data['fundamentals']['mcap']/1000000000000):.2f}L Cr" if data['fundamentals']['mcap'] else 'N/A'}</p>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                    # --- 5. LATEST HEADLINES (NEW) ---
                    st.markdown(f"""
                        <div class='card'>
                            <h3>Latest Headlines (The Noise)</h3>
                            {''.join([f"""
                                <div class='news-item'>
                                    <a href='{item['link']}' target='_blank'>{item['title']}</a>
                                    <span> - {item['publisher']}</span>
                                </div>
                            """ for item in data['headlines']]) if data['headlines'] else "<p>No recent news found.</p>"}
                        </div>
                    """, unsafe_allow_html=True)
                
                else:
                    st.error(f"Could not fetch data for {manual_ticker}. Check symbol or data availability.")

st.caption("Disclaimer: Delayed data. For educational use only. Do not trade real money.")
