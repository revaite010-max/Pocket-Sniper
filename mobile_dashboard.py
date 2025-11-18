import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Alpha Screener", layout="centered")

# --- PRO UI STYLING (V6.3 - UNCHANGED) ---
st.markdown("""
    <style>
    /* ... (All V6.3 CSS is unchanged) ... */
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
    .card div, .card span {
        color: #374151 !important;
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
    .signal-card h1 {
        font-size: 32px !important;
        font-weight: 700 !important;
        margin: 0 !important;
    }
    .signal-buy h1 { color: #059669 !important; }
    .signal-sell h1 { color: #DC2626 !important; }
    .signal-wait h1 { color: #6B7280 !important; }
    .signal-card p {
        font-size: 14px !important;
        font-weight: 500 !important;
        margin-top: 5px !important;
    }
    .signal-buy p { color: #047857 !important; }
    .signal-sell p { color: #B91C1C !important; }
    .signal-wait p { color: #4B5563 !important; }
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
    .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border: 1px solid #D1D5DB !important;
        border-radius: 8px !important;
    }
    .stTextInput label {
        color: #374151 !important;
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
    .stButton>button:hover {
        background-color: #1D4ED8 !important;
    }
    .stButton>button p {
        color: white !important;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #6B7280 !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] p {
        color: #2563EB !important;
    }
    .stTabs [aria-selected="true"] {
        border-bottom-color: #2563EB !important;
    }
    .streamlit-expanderHeader {
        background-color: #FFFFFF !important;
        color: #111827 !important;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
    }
    .streamlit-expanderHeader p {
        color: #111827 !important;
        font-weight: 600 !important;
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

# --- NIFTY 100 STOCK LIST ---
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

# --- THE "BRAIN" - V7.0 (NO NOISE) ---
@st.cache_data(ttl=900)
def analyze_ticker(symbol, mode='screener'):
    try:
        # --- 1. TECHNICAL ENGINE (ROBUST) ---
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

        # --- MANUAL MODE (DECOUPLED) ---
        elif mode == 'manual':
            ticker_obj = yf.Ticker(symbol)
            
            # --- 2. SUBSTANCE: FUNDAMENTALS (ISOLATED) ---
            fund_summary_points = []
            try:
                info = ticker_obj.info
                sector = info.get("sector", "N/A")
                fund_summary_points.append(f"🏢 **Industry:** {sector}")
                
                pe = info.get("trailingPE")
                if pe:
                    if pe > 100: fund_summary_points.append(f"❌ **Valuation:** Extremely Overvalued (P/E {pe:.2f})")
                    elif pe > 50: fund_summary_points.append(f"⚠️ **Valuation:** High Valuation (P/E {pe:.2f})")
                    elif pe > 25: fund_summary_points.append(f"🟡 **Valuation:** Fairly Valued (P/E {pe:.2f})")
                    elif pe > 0: fund_summary_points.append(f"✅ **Valuation:** Good Value (P/E {pe:.2f})")
                    else: fund_summary_points.append(f"❌ **Valuation:** Negative P/E (P/E {pe:.2f})")
                else: fund_summary_points.append("🟡 **Valuation:** P/E Ratio not available.")

                eps = info.get("forwardEPS")
                if eps:
                    if eps > 0: fund_summary_points.append(f"✅ **Profitability:** Company is profitable (EPS {eps:.2f})")
                    else: fund_summary_points.append(f"❌ **Profitability:** Company is unprofitable (EPS {eps:.2f})")
                else: fund_summary_points.append("🟡 **Profitability:** EPS not available.")
            
            except Exception as e:
                fund_summary_points = ["Could not load fundamental data."]
            
            fundamental_summary = "\n\n".join(fund_summary_points)

            # --- 3. NOISE: NEWS (REMOVED) ---
            # Headlines have been completely removed.

            # --- 4. BUILD ANALYSIS (NOW SAFE) ---
            signal, reason, color_class = "WAIT", "Sideways", "wait"
            stop_loss, target = 0.0, 0.0
            tech_summary_points = []
            
            if latest['Close'] > latest['SMA_50'] and latest['Close'] > latest['SMA_200']:
                tech_summary_points.append("✅ **Trend:** Price is above both the 50-day and 200-day moving averages, confirming a strong long-term uptrend.")
            elif latest['Close'] > latest['SMA_50'] and latest['Close'] < latest['SMA_200']:
                tech_summary_points.append("⚠️ **Trend:** Short-term uptrend (above 50-day) but in a long-term downtrend (below 200-day).")
            else:
                tech_summary_points.append("❌ **Trend:** Price is below its key moving averages, signaling a clear downtrend.")

            rsi_val = float(latest['RSI'])
            if rsi_val > 70: tech_summary_points.append(f"⚠️ **Momentum:** RSI is {rsi_val:.1f} (Overbought).")
            elif rsi_val > 50: tech_summary_points.append(f"✅ **Momentum:** RSI is {rsi_val:.1f} (Bullish).")
            elif rsi_val < 30: tech_summary_points.append(f"⚠️ **Momentum:** RSI is {rsi_val:.1f} (Oversold).")
            else: tech_summary_points.append(f"❌ **Momentum:** RSI is {rsi_val:.1f} (Bearish).")
            
            if latest[macd_line_col] > latest[macd_sig_col]:
                tech_summary_points.append("✅ **MACD:** The MACD line is above its signal line, reinforcing positive momentum.")
            else:
                tech_summary_points.append("❌ **MACD:** The MACD line is below its signal line, indicating selling pressure.")

            if adx_val < 25:
                reason = f"Sideways (ADX {adx_val:.1f})"
                tech_summary_points.append(f"⚠️ **Trend Strength:** The ADX is {adx_val:.1f}, indicating a weak or sideways market. **No clear trend.**")
            else:
                tech_summary_points.append(f"✅ **Trend Strength:** The ADX is {adx_val:.1f}, confirming a **strong trend**.")

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
            
            technical_summary = "\n\n".join(tech_summary_points)
            
            analysis = {
                "symbol": symbol, "price": current_price, "signal": signal,
                "reason": reason, "color_class": color_class, "stop_loss": stop_loss, "target": target,
                "technical_summary": technical_summary,
                "fundamental_summary": fundamental_summary,
            }
            return analysis

    except Exception as e:
        return None # Main technical analysis failed

# --- UI TABS ---
tab1, tab2 = st.tabs(["🔥 Screener", "📊 Full Analysis"])

# --- TAB 1: NIFTY 100 SCREENER (UI FIX) ---
with tab1:
    st.markdown("### NIFTY 100 Screener")
    st.markdown("<p style='color: #4B5563 !important; margin-top: -10px;'>Finds Top 5 'BUY' signals (Supertrend + ADX > 25).</p>", unsafe_allow_html=True)
    
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
        
        for res in top_Dos:
            crossover_badge = " ⭐ NEW" if res['crossover'] else ""
            expander_title = f"{res['symbol']}{crossover_badge}  |  Price: ₹{res['price']:.2f}  |  ADX: {res['adx']:.1f}"
            
            with st.expander(expander_title):
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
                            <h3>Technical Summary (The Signal)</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['technical_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='card' style='margin-top: 10px;'>
                            <h3>Fundamental Summary (The Substance)</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['fundamental_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else: 
                    st.error("Could not load full analysis.")

# --- TAB 2: FULL ANALYSIS ---
with tab2:
    st.markdown("### Manual Stock Analysis")
    st.markdown("<p style='color: #4B5563 !important; margin-top: -10px;'>Get a full summary for any stock.</p>", unsafe_allow_html=True)
    
    manual_ticker = st.text_input("Enter any symbol (e.g., ZOMATO.NS)", "").upper()
    
    if st.button("Analyze Stock", key="manual_analyze"):
        if not manual_ticker:
            st.error("Please enter a stock symbol.")
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
                    
                    if data['signal'] != "WAIT":
                        st.markdown(f"""
                            <div class='card'>
                                <h3>Actionable Levels</h3>
                                <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px;'>
                                    <div class'metric-box'><h4>Entry Price</h4><p>₹{data['price']:.2f}</p></div>
                                    <div class='metric-box metric-box-red'><h4>Stop Loss (SL)</h4><p>₹{data['stop_loss']:.2f}</p></div>
                                    <div class'metric-box metric-box-green'><h4>Target (1.5R)</h4><p>₹{data['target']:.2f}</p></div>
                                </div>
                            </div>
                        """, unsafe_allow_html=True)

                    st.markdown(f"""
                        <div class='card'>
                            <h3>Technical Summary (The Signal)</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['technical_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    st.markdown(f"""
                        <div class='card'>
                            <h3>Fundamental Summary (The Substance)</h3>
                            <div style='font-size: 14px; color: #374151 !important; line-height: 1.6;'>
                                {data['fundamental_summary'].replace("✅", "🟢 ").replace("⚠️", "🟡 ").replace("❌", "🔴 ").replace("\\n", "<br>")}
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                else: 
                    st.error(f"Could not fetch data for {manual_ticker}.")

st.caption("Disclaimer: Delayed data. For educational use only. Do not trade real money.")
