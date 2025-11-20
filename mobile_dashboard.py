import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Alpha Screener V12", layout="centered")

# --- PRO UI STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #F0F2F6 !important; 
        color: #111827 !important; 
    }
    .stMarkdown, .stText, h1, h2, h3, p, li, span, div {
        color: #111827 !important; 
    }
    #MainMenu, footer, header { visibility: hidden; }
    div.block-container { padding: 1rem 1rem 2rem 1rem; }
    
    .card {
        background-color: #FFFFFF !important;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 12px;
        border: 1px solid #E5E7EB;
    }
    .signal-card {
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 16px;
        border: 1px solid #E5E7EB;
    }
    .signal-buy { background-color: #ECFDF5 !important; }
    .signal-sell { background-color: #FEF2F2 !important; }
    .signal-wait { background-color: #FFFFFF !important; }
    .signal-gem { background-color: #F0F9FF !important; } /* Blue for Gems */

    .signal-card h1 { margin: 0 !important; font-size: 28px !important; font-weight: 700 !important; }
    .signal-buy h1 { color: #059669 !important; }
    .signal-sell h1 { color: #DC2626 !important; }
    .signal-wait h1 { color: #6B7280 !important; }
    .signal-gem h1 { color: #0284C7 !important; }

    .signal-card p {
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-top: 5px !important;
    }
    .metric-box {
        background-color: #F9FAFB !important;
        border: 1px solid #E5E7EB !important;
        padding: 10px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-box h4 { font-size: 11px !important; color: #6B7280 !important; margin: 0 0 4px 0 !important; }
    .metric-box p { font-size: 16px !important; font-weight: 700 !important; color: #111827 !important; margin: 0 !important; }
    .metric-box-green p { color: #059669 !important; }
    .metric-box-red p { color: #DC2626 !important; }
    
    .stTextInput input, .stTextArea textarea {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px !important;
        background-color: #2563EB !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #2563EB !important;
        color: #2563EB !important;
    }
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border-radius: 8px;
        margin-bottom: 10px;
        border: none !important;
    }
    div[data-testid="stExpanderDetails"] {
        background-color: #FFFFFF !important;
        border-radius: 0 0 8px 8px;
        border: 1px solid #E5E7EB;
        border-top: none;
        color: #111827 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Alpha Screener V12")

# --- EXPANDED DEFAULT LIST (150+ Stocks) ---
# Added Midcaps and F&O stocks to solve "Same stocks everyday" issue
DEFAULT_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "BHARTIARTL.NS", "SBIN.NS", "INFY.NS", "LICI.NS", 
    "ITC.NS", "LT.NS", "HCLTECH.NS", "MARUTI.NS", "SUNPHARMA.NS", "ADANIENT.NS", "KOTAKBANK.NS", "TITAN.NS", 
    "ONGC.NS", "TATAMOTORS.NS", "NTPC.NS", "AXISBANK.NS", "ADANIPORTS.NS", "ULTRACEMCO.NS", "WIPRO.NS", 
    "M&M.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "POWERGRID.NS", "COALINDIA.NS", "NESTLEIND.NS", "IOC.NS", 
    "JSWSTEEL.NS", "TATASTEEL.NS", "HINDUNILVR.NS", "GRASIM.NS", "TECHM.NS", "HINDALCO.NS", "EICHERMOT.NS", 
    "DRREDDY.NS", "CIPLA.NS", "SBILIFE.NS", "BPCL.NS", "BRITANNIA.NS", "APOLLOHOSP.NS", "TATACONSUM.NS", 
    "DIVISLAB.NS", "HEROMOTOCO.NS", "ASIANPAINT.NS", "BAJAJ-AUTO.NS", "LTIM.NS", "INDUSINDBK.NS", 
    # Added Midcaps & F&O
    "ZOMATO.NS", "DLF.NS", "HAL.NS", "BEL.NS", "VBL.NS", "TRENT.NS", "SIEMENS.NS", "ABB.NS", "PIDILITIND.NS", 
    "INDIGO.NS", "CHOLAFIN.NS", "TVSMOTOR.NS", "HAVELLS.NS", "JINDALSTEL.NS", "GAIL.NS", "AMBUJACEM.NS", 
    "SHRIRAMFIN.NS", "BANKBARODA.NS", "CANBK.NS", "VEDL.NS", "PNB.NS", "RECLTD.NS", "PFC.NS", "ADANIENSOL.NS", 
    "ADANIGREEN.NS", "ATGL.NS", "LODHA.NS", "SRF.NS", "ICICIPRULI.NS", "ICICIGI.NS", "BERGEPAINT.NS", 
    "DABUR.NS", "GODREJCP.NS", "MARICO.NS", "MCDOWELL-N.NS", "NAUKRI.NS", "COLPAL.NS", "BOSCHLTD.NS", 
    "ALKEM.NS", "MUTHOOTFIN.NS", "PIIND.NS", "TORRENTPHARM.NS", "MANKIND.NS", "IRCTC.NS", "CUMMINSIND.NS", 
    "POLYCAB.NS", "ASTRAL.NS", "SCHAEFFLER.NS", "PERSISTENT.NS", "MPHASIS.NS", "TATACOMM.NS", "ASHOKLEY.NS", 
    "BALKRISIND.NS", "MRF.NS", "PAGEIND.NS", "JUBLFOOD.NS", "UBL.NS", "CONCOR.NS", "AUBANK.NS", "IDFCFIRSTB.NS", 
    "FEDERALBNK.NS", "BANDHANBNK.NS", "ABCAPITAL.NS", "MFSL.NS", "MAXHEALTH.NS", "LALPATHLAB.NS", "SYNGENE.NS"
]

# --- THE BRAIN (V12.0 - Value Squeeze Logic) ---
@st.cache_data(ttl=900)
def analyze_ticker(symbol, mode='screener', scan_type='trend'):
    try:
        # Technicals (Fast)
        df = yf.download(symbol, period="2y", interval="1d", progress=False)
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df.dropna(how='all', inplace=True)
        data_len = len(df)
        if data_len < 20: return None 

        latest = df.iloc[-1]
        current_price = float(latest['Close'])
        
        # Indicators
        adx_val = 0.0
        sma_200_val = None
        
        if data_len > 200:
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            sma_200_val = float(df['SMA_200'].iloc[-1])
        
        if data_len > 15:
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None: adx_val = float(adx['ADX_14'].iloc[-1])

        # --- SCREENER MODE ---
        if mode == 'screener':
            # 1. BASIC TECHNICAL FILTER (Fast)
            # Only fetch fundamentals if technicals pass to save time
            is_technical_pass = False
            
            if scan_type == 'value_squeeze':
                # Bullish (Price > 200SMA) AND Consolidating (ADX < 25)
                if sma_200_val and current_price > sma_200_val and adx_val < 25:
                    is_technical_pass = True
            else:
                # Default Trend Scan (Supertrend > ADX)
                sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
                if sti is not None and int(sti[sti.columns[1]].iloc[-1]) == 1 and adx_val > 25:
                    return {"symbol": symbol, "price": current_price, "signal": "BUY"}

            # 2. FUNDAMENTAL CHECK (Slow - Only if Tech Pass)
            if is_technical_pass:
                try:
                    ticker_obj = yf.Ticker(symbol)
                    info = ticker_obj.info
                    eps = info.get("forwardEPS", 0)
                    pe = info.get("trailingPE", 100)
                    
                    # Criteria: Profitable (EPS > 0) AND Reasonable Valuations (PE < 80)
                    if eps is not None and eps > 0 and pe is not None and pe < 80:
                        return {
                            "symbol": symbol, 
                            "price": current_price, 
                            "signal": "GEM",
                            "pe": pe,
                            "adx": adx_val
                        }
                except:
                    pass # Skip if fundamental fetch fails
            
            return None

        # --- MANUAL MODE ---
        elif mode == 'manual':
            ticker_obj = yf.Ticker(symbol)
            fund_summary = []
            try:
                info = ticker_obj.info
                fund_summary.append(f"🏢 **Industry:** {info.get('sector', 'N/A')}")
                pe = info.get("trailingPE")
                if pe: fund_summary.append(f"📊 **P/E Ratio:** {pe:.2f}")
                eps = info.get("forwardEPS")
                if eps: fund_summary.append(f"💰 **Forward EPS:** ₹{eps}")
            except: fund_summary = ["No fundamentals."]
            fundamental_text = "\n\n".join(fund_summary)

            tech_text_list = []
            if sma_200_val and current_price > sma_200_val:
                tech_text_list.append("✅ **Long Term Trend:** Bullish (Above 200 SMA).")
            else:
                tech_text_list.append("❌ **Long Term Trend:** Bearish (Below 200 SMA).")
            
            if adx_val < 25:
                tech_text_list.append(f"⏳ **Volatility:** Low ({adx_val:.1f}). Stock is resting.")
            else:
                tech_text_list.append(f"🔥 **Volatility:** High ({adx_val:.1f}). Stock is trending.")

            technical_text = "\n\n".join(tech_text_list)

            return {
                "symbol": symbol, "price": current_price,
                "signal": "GEM" if (sma_200_val and current_price > sma_200_val and adx_val < 25) else "WAIT",
                "color_class": "gem" if (sma_200_val and current_price > sma_200_val and adx_val < 25) else "wait",
                "technical_summary": technical_text,
                "fundamental_summary": fundamental_text,
                "target": current_price * 1.15,
                "stop_loss": df['Low'].tail(20).min()
            }

    except Exception as e:
        return None

# --- UI TABS ---
tab1, tab2, tab3 = st.tabs(["💎 Value Squeeze", "🔥 Trend Scan", "📊 Analysis"])

# --- TAB 1: VALUE SQUEEZE (NEW) ---
with tab1:
    st.markdown("### Fundamental Gems in Consolidation")
    st.markdown("""
    <div style='background-color: #EFF6FF; padding: 10px; border-radius: 8px; font-size: 13px; color: #1E3A8A; margin-bottom: 10px;'>
    <b>Strategy:</b> Finds stocks that are:<br>
    1. 📈 <b>Bullish Trend:</b> Price > 200 SMA.<br>
    2. ⏳ <b>Consolidating:</b> ADX < 25 (Quietly building a base).<br>
    3. 💎 <b>Strong Fundamentals:</b> Profitable (EPS > 0) & Not Overvalued (P/E < 80).
    </div>
    """, unsafe_allow_html=True)
    
    # Configurable list
    with st.expander("⚙️ Configure List (Default: Top 150 Stocks)", expanded=False):
        default_str = ", ".join([t.replace(".NS", "") for t in DEFAULT_TICKERS])
        user_input = st.text_area("Edit List:", default_str)
        SCAN_LIST = [f"{x.strip().upper()}.NS" if not x.strip().upper().endswith(".NS") else x.strip().upper() for x in user_input.split(",")] if user_input else DEFAULT_TICKERS

    if st.button("💎 FIND GEMS"):
        progress_bar = st.progress(0, text="Scanning Fundamentals & Technicals...")
        results = []
        target_list = SCAN_LIST[:100] # Limit to prevent timeout
        
        for i, ticker in enumerate(target_list):
            progress_bar.progress((i + 1) / len(target_list), text=f"Analyzing: {ticker}")
            # Pass scan_type='value_squeeze' to trigger fundamental check
            data = analyze_ticker(ticker, mode='screener', scan_type='value_squeeze')
            if data: results.append(data)
        
        progress_bar.empty()
        
        # Sort by P/E (Value)
        results = sorted(results, key=lambda x: x['pe'])
        
        st.markdown(f"### Found {len(results)} Gems")
        if not results: st.info("No stocks match the 'Value + Consolidation' criteria today.")
        
        for res in results:
            with st.expander(f"{res['symbol']} 💎 P/E: {res['pe']:.1f} | ₹{res['price']:.2f}"):
                with st.spinner("Loading full report..."):
                    data = analyze_ticker(res['symbol'], mode='manual')
                if data:
                    st.markdown(f"""
                        <div class='signal-card signal-gem'>
                            <h1>STRONG SETUP</h1>
                            <p>Bullish + Profitable + Squeeze</p>
                        </div>
                        <div class='card'>
                            <h3>Why this stock?</h3>
                            <div style='font-size:14px; color:#374151;'>
                                {data['technical_summary'].replace("✅", "🟢").replace("⏳", "⚡").replace("\\n", "<br>")}
                                <br><br>
                                {data['fundamental_summary'].replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# --- TAB 2: TREND SCAN (OLD SCREENER) ---
with tab2:
    st.markdown("### Trend Scanner")
    if st.button("🚀 START TREND SCAN"):
        progress_bar = st.progress(0, text="Scanning...")
        results = []
        target_list = SCAN_LIST[:100]
        for i, ticker in enumerate(target_list):
            progress_bar.progress((i + 1) / len(target_list), text=f"Checking {ticker}")
            data = analyze_ticker(ticker, mode='screener', scan_type='trend')
            if data: results.append(data)
        progress_bar.empty()
        
        st.markdown(f"### Found {len(results)} Trending Stocks")
        for res in results:
            with st.expander(f"{res['symbol']} 🚀 | ₹{res['price']:.2f}"):
                with st.spinner("Analyzing..."):
                    data = analyze_ticker(res['symbol'], mode='manual')
                if data:
                    st.markdown(f"""
                        <div class='card' style='border-left: 5px solid #059669;'>
                            <p style='font-size:18px; font-weight:bold; color:#059669;'>BUY SIGNAL</p>
                            <div style='font-size:14px; color:#374151;'>{data['technical_summary'].replace("\\n", "<br>")}</div>
                        </div>
                    """, unsafe_allow_html=True)

# --- TAB 3: ANALYSIS ---
with tab3:
    st.markdown("### Deep Dive")
    manual_ticker = st.text_input("Symbol (e.g. ZOMATO.NS)", "").upper()
    if manual_ticker and not manual_ticker.endswith(".NS"): manual_ticker += ".NS"
    
    if st.button("Analyze"):
        with st.spinner("Processing..."):
            data = analyze_ticker(manual_ticker, mode='manual')
            if data:
                st.markdown(f"""
                    <div class='signal-card signal-{data['color_class']}'>
                        <h1>{data['signal']}</h1>
                    </div>
                    <div class='card'>
                        <h3>Technical View</h3>
                        <div style='color:#374151;'>{data['technical_summary'].replace("\\n", "<br>")}</div>
                    </div>
                    <div class='card'>
                        <h3>Fundamental Data</h3>
                        <div style='color:#374151;'>{data['fundamental_summary'].replace("\\n", "<br>")}</div>
                    </div>
                """, unsafe_allow_html=True)
            else: st.error("Not found.")
