import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Alpha Screener V8", layout="centered")

# --- PRO UI STYLING (UNCHANGED) ---
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
    .card h3 {
        font-size: 18px !important;
        font-weight: 600 !important;
        margin: 0 0 10px 0 !important;
        color: #111827 !important;
    }
    .card p {
        font-size: 14px !important;
        color: #4B5563 !important;
        margin-bottom: 5px !important;
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
    .signal-new { background-color: #EFF6FF !important; } /* Blue for IPOs */
    
    .signal-card h1 {
        font-size: 32px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .signal-buy h1 { color: #059669 !important; }
    .signal-sell h1 { color: #DC2626 !important; }
    .signal-wait h1 { color: #6B7280 !important; }
    .signal-new h1 { color: #2563EB !important; }

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
    .metric-box h4 {
        font-size: 11px !important;
        font-weight: 600 !important;
        color: #6B7280 !important;
        margin: 0 0 4px 0 !important;
        text-transform: uppercase;
    }
    .metric-box p {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #111827 !important;
        margin: 0 !important;
    }
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

st.title("Alpha Screener")

# --- DEFAULT LIST (BACKUP) ---
DEFAULT_TICKERS = [
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

# --- THE "BRAIN" - V8.0 (ADAPTIVE LOGIC) ---
@st.cache_data(ttl=900)
def analyze_ticker(symbol, mode='screener'):
    try:
        # --- 1. ADAPTIVE DATA FETCHING ---
        # Try to get max history available
        df = yf.download(symbol, period="2y", interval="1d", progress=False) 
        
        if df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # Clean data
        df.dropna(how='all', inplace=True)
        data_len = len(df)
        
        # Check if we have ANY data
        if data_len < 2: return None

        latest = df.iloc[-1]
        current_price = float(latest['Close'])
        
        # --- 2. ADAPTIVE INDICATOR CALCULATION ---
        # We only calculate what we have data for.
        
        st_dir, adx_val, rsi_val = 0, 0.0, 0.0
        sma_50_val, sma_200_val = None, None
        macd_bullish = False
        
        # Supertrend needs ~10 days minimum
        if data_len > 10:
            sti = ta.supertrend(df['High'], df['Low'], df['Close'], length=7, multiplier=3)
            if sti is not None and not sti.empty:
                df['ST_DIR'] = sti[sti.columns[1]]
                df['ST_VAL'] = sti[sti.columns[0]]
                st_dir = int(df['ST_DIR'].iloc[-1])
        
        # ADX & RSI need ~15 days
        if data_len > 15:
            adx = ta.adx(df['High'], df['Low'], df['Close'], length=14)
            if adx is not None:
                df['ADX'] = adx['ADX_14']
                adx_val = float(df['ADX'].iloc[-1])
            
            rsi = ta.rsi(df['Close'], length=14)
            if rsi is not None:
                df['RSI'] = rsi
                rsi_val = float(df['RSI'].iloc[-1])

        # MACD needs ~35 days
        if data_len > 35:
            macd = ta.macd(df['Close'], fast=12, slow=26, signal=9)
            if macd is not None:
                macd_line = macd[macd.columns[0]]
                macd_sig = macd[macd.columns[2]]
                if macd_line.iloc[-1] > macd_sig.iloc[-1]:
                    macd_bullish = True

        # SMAs need 50 or 200 days
        if data_len > 50:
            df['SMA_50'] = ta.sma(df['Close'], length=50)
            sma_50_val = float(df['SMA_50'].iloc[-1])
        
        if data_len > 200:
            df['SMA_200'] = ta.sma(df['Close'], length=200)
            sma_200_val = float(df['SMA_200'].iloc[-1])

        # --- SCREENER MODE ---
        if mode == 'screener':
            signal = "WAIT"
            is_crossover = False
            
            # IPO Logic: If < 50 days data, we can't trust ADX/Supertrend blindly
            if data_len < 50:
                # For IPOs, just check price momentum
                return {"symbol": symbol, "price": current_price, "signal": "IPO", "adx": 0, "crossover": True, "is_ipo": True}

            # Standard Logic
            if data_len > 15 and 'ST_DIR' in df.columns:
                st_previous = int(df['ST_DIR'].iloc[-2])
                is_crossover = (st_dir == 1 and st_previous == -1)
                
                if (st_dir == 1) and (adx_val > 25):
                    signal = "BUY"
            
            return {"symbol": symbol, "price": current_price, "signal": signal, "adx": adx_val, "crossover": is_crossover, "is_ipo": False}

        # --- MANUAL MODE (ADAPTIVE SUMMARY) ---
        elif mode == 'manual':
            ticker_obj = yf.Ticker(symbol)
            
            # Fundamentals
            fund_summary_points = []
            try:
                info = ticker_obj.info
                sector = info.get("sector", "N/A")
                fund_summary_points.append(f"🏢 **Industry:** {sector}")
                pe = info.get("trailingPE")
                if pe: fund_summary_points.append(f"📊 **P/E Ratio:** {pe:.2f}")
                mcap = info.get("marketCap")
                if mcap: fund_summary_points.append(f"💰 **Market Cap:** {f'{(mcap/10000000):.0f} Cr'}")
            except:
                fund_summary_points = ["Could not load fundamental data."]
            
            fundamental_summary = "\n\n".join(fund_summary_points)

            # Technical Summary
            signal, reason, color_class = "WAIT", "Sideways", "wait"
            stop_loss, target = 0.0, 0.0
            tech_summary_points = []

            # -- IPO / NEW LISTING LOGIC --
            if data_len < 50:
                signal = "NEW"
                color_class = "new"
                reason = "Recently Listed (IPO)"
                tech_summary_points.append(f"🆕 **New Listing:** This stock has only {data_len} days of trading history.")
                tech_summary_points.append("⚠️ **Caution:** Moving Averages (50/200) and other long-term indicators cannot be calculated yet.")
                tech_summary_points.append(f"📈 **Price Action:** Current Price is ₹{current_price:.2f}. Watch for volatility.")
                stop_loss = df['Low'].min() # Simple low of history
                target = current_price * 1.2 
            else:
                # -- STANDARD LOGIC --
                # Trend
                if sma_50_val and sma_200_val:
                    if current_price > sma_50_val and current_price > sma_200_val:
                        tech_summary_points.append("✅ **Trend:** Price > 50 & 200 SMA (Strong Uptrend).")
                    elif current_price < sma_200_val:
                         tech_summary_points.append("❌ **Trend:** Price < 200 SMA (Downtrend).")
                
                # Momentum
                if rsi_val > 0:
                    if rsi_val > 70: tech_summary_points.append(f"⚠️ **RSI:** {rsi_val:.1f} (Overbought)")
                    elif rsi_val > 50: tech_summary_points.append(f"✅ **RSI:** {rsi_val:.1f} (Bullish)")
                    else: tech_summary_points.append(f"❌ **RSI:** {rsi_val:.1f} (Bearish)")
                
                # Signal
                if st_dir == 1 and adx_val > 25:
                    signal, reason, color_class = "BUY", "Strong Uptrend", "buy"
                    stop_loss = df['ST_VAL'].iloc[-1] if 'ST_VAL' in df.columns else 0
                    target = current_price + (current_price - stop_loss) * 1.5 if stop_loss else 0
                elif st_dir == -1:
                    signal, reason, color_class = "SELL", "Downtrend", "sell"
                    stop_loss = df['ST_VAL'].iloc[-1] if 'ST_VAL' in df.columns else 0

            technical_summary = "\n\n".join(tech_summary_points)
            
            analysis = {
                "symbol": symbol, "price": current_price, "signal": signal,
                "reason": reason, "color_class": color_class, "stop_loss": stop_loss, "target": target,
                "technical_summary": technical_summary,
                "fundamental_summary": fundamental_summary,
            }
            return analysis

    except Exception as e:
        return None

# --- UI TABS ---
tab1, tab2 = st.tabs(["🔥 Screener", "📊 Full Analysis"])

# --- TAB 1: SCREENER (DYNAMIC LIST) ---
with tab1:
    st.markdown("### Market Scanner")
    
    # --- NEW FEATURE: CUSTOM LIST INPUT ---
    with st.expander("⚙️ Configure Stock List (Edit Here)", expanded=False):
        default_list_str = ", ".join([t.replace(".NS", "") for t in DEFAULT_TICKERS])
        user_input = st.text_area("Enter stock symbols (comma separated, NSE implied):", default_list_str)
        
        # Process Input
        if user_input:
            raw_list = [x.strip().upper() for x in user_input.split(",")]
            # Ensure .NS suffix
            SCAN_LIST = [f"{x}.NS" if not x.endswith(".NS") else x for x in raw_list if x]
        else:
            SCAN_LIST = DEFAULT_TICKERS

    st.markdown(f"<p style='color: #4B5563; margin-top: -10px;'>Scanning <b>{len(SCAN_LIST)}</b> stocks.</p>", unsafe_allow_html=True)
    
    if st.button("🚀 RUN SCAN", key="scan_nifty"):
        progress_bar = st.progress(0, text="Initializing scan...")
        all_results = []
        
        # Limit scan to first 100 to prevent timeouts if user pastes 500 stocks
        target_list = SCAN_LIST[:100]
        
        for i, ticker in enumerate(target_list):
            progress_bar.progress((i + 1) / len(target_list), text=f"Checking: {ticker}")
            data = analyze_ticker(ticker, mode='screener')
            
            # Filter: BUY signals OR IPOs
            if data and (data['signal'] == "BUY" or data['signal'] == "IPO"):
                all_results.append(data)
        
        progress_bar.empty()
        
        # Sort: IPOs first, then Strength
        sorted_results = sorted(all_results, key=lambda x: (x['signal'] == "IPO", x['crossover'], x['adx']), reverse=True)
        
        st.markdown(f"### 🔥 Found {len(sorted_results)} Opportunities")
        
        if not sorted_results:
            st.warning("No strong signals found.")
        
        for res in sorted_results:
            badge = " ⭐ NEW" if res['crossover'] else ""
            if res['signal'] == "IPO": badge = " 🆕 IPO"
            
            with st.expander(f"{res['symbol']}{badge}  |  ₹{res['price']:.2f}"):
                with st.spinner("Loading details..."):
                    data = analyze_ticker(res['symbol'], mode='manual')
                if data:
                    st.markdown(f"""
                        <div class='signal-card signal-{data['color_class']}'>
                            <h1>{data['signal']}</h1>
                            <p>{data['reason']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='card' style='margin-top: 10px;'>
                            <h3>Technical Summary</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['technical_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='card' style='margin-top: 10px;'>
                            <h3>Fundamentals</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['fundamental_summary'].replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

# --- TAB 2: FULL ANALYSIS (UNCHANGED) ---
with tab2:
    st.markdown("### Manual Stock Analysis")
    st.markdown("<p style='color: #4B5563 !important; margin-top: -10px;'>Enter any symbol (e.g., PWL.NS, ZOMATO.NS)</p>", unsafe_allow_html=True)
    
    manual_ticker = st.text_input("Stock Symbol", "").upper()
    if not manual_ticker.endswith(".NS") and manual_ticker:
        manual_ticker += ".NS"
    
    if st.button("Analyze Stock", key="manual_analyze"):
        if not manual_ticker:
            st.error("Please enter a symbol.")
        else:
            with st.spinner(f"Analyzing {manual_ticker}..."):
                data = analyze_ticker(manual_ticker, mode='manual')
                
                if data:
                    st.markdown(f"""
                        <div class='signal-card signal-{data['color_class']}'>
                            <h1>{data['signal']}</h1>
                            <p>{data['reason']}</p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    if data['stop_loss'] > 0:
                         st.markdown(f"""
                            <div class='card'>
                                <h3>Levels</h3>
                                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>
                                    <div class='metric-box metric-box-red'><h4>Stop Loss</h4><p>₹{data['stop_loss']:.2f}</p></div>
                                    <div class='metric-box metric-box-green'><h4>Target</h4><p>₹{data['target']:.2f}</p></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"""
                        <div class='card'>
                            <h3>Technical Summary</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['technical_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='card'>
                            <h3>Fundamentals</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['fundamental_summary'].replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.error("Could not fetch data. Symbol might be invalid or delisted.")

st.caption("Disclaimer: Delayed data. For educational use only. Do not trade real money.")
