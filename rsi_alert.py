import yfinance as yf
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import time
import threading


# Configuration
DEFAULT_STOCKS = yahoo_symbols = [
    "ABSLBANETF.NS",
    "ABSLNN50ET.NS",
    "ALPHA.NS",
    "ALPHAETF.NS",
    "ALPL30IETF.NS",
    "AUTOBEES.NS",
    "AUTOIETF.NS",
    "AXISGOLD.NS",
    "AXISILVER.NS",
    "AXISNIFTY.NS",
    "AXISTECETF.NS",
    "BANKBEES.NS",
    "BANKBETF.NS",
    "BANKIETF.NS",
    "BANKNIFTY1.NS",
    "BFSI.NS",
    "BSE500IETF.NS",
    "BSLGOLDETF.NS",
    "BSLNIFTY.NS",
    "COMMOIETF.NS",
    "CONSUMBEES.NS",
    "CONSUMIETF.NS",
    "CPSEETF.NS",
    "DIVOPPBEES.NS",
    "EQUAL50ADD.NS",
    "FINIETF.NS",
    "FMCGIETF.NS",
    "GOLDBEES.NS",
    "GOLDCASE.NS",
    "GOLDETF.NS",
    "GOLDETFADD.NS",
    "GOLDIETF.NS",
    "GOLDSHARE.NS",
    "HDFCBSE500.NS",
    "HDFCGOLD.NS",
    "HDFCLOWVOL.NS",
    "HDFCMID150.NS",
    "HDFCMOMENT.NS",
    "HDFCNEXT50.NS",
    "HDFCNIF100.NS",
    "HDFCNIFBAN.NS",
    "HDFCNIFIT.NS",
    "HDFCNIFTY.NS",
    "HDFCPSUBK.NS",
    "HDFCPVTBAN.NS",
    "HDFCSENSEX.NS",
    "HDFCSILVER.NS",
    "HDFCSML250.NS",
    "HEALTHIETF.NS",
    "HEALTHY.NS",
    "ICICIB22.NS",
    "INFRABEES.NS",
    "INFRAIETF.NS",
    "IT.NS",
    "ITBEES.NS",
    "ITETF.NS",
    "ITETFADD.NS",
    "ITIETF.NS",
    "JUNIORBEES.NS",
    "KOTAKGOLD.NS",
    "KOTAKSILVE.NS",
    "LOWVOLIETF.NS",
    "MAFANG.NS",
    "MAKEINDIA.NS",
    "MASPTOP50.NS",
    "MID150BEES.NS",
    "MIDCAP.NS",
    "MIDCAPETF.NS",
    "MIDCAPIETF.NS",
    "MIDQ50ADD.NS",
    "MIDSELIETF.NS",
    "MNC.NS",
    "MOHEALTH.NS",
    "MOM100.NS",
    "MOM30IETF.NS",
    "MOMENTUM.NS",
    "MOMOMENTUM.NS",
    "MON100.NS",
    "MONIFTY500.NS",
    "MONQ50.NS",
    "MOREALTY.NS",
    "MOSMALL250.NS",
    "MOVALUE.NS",
    "NEXT50IETF.NS",
    "NIF100BEES.NS",
    "NIF100IETF.NS",
    "NIFITETF.NS",
    "NIFMID150.NS",
    "NIFTY1.NS",
    "NIFTY50ADD.NS",
    "NIFTYBEES.NS",
    "NIFTYETF.NS",
    "NIFTYIETF.NS",
    "NIFTYQLITY.NS",
    "NV20.NS",
    "NV20BEES.NS",
    "NV20IETF.NS",
    "PHARMABEES.NS",
    "PSUBANK.NS",
    "PSUBNKBEES.NS",
    "PSUBNKIETF.NS",
    "PVTBANIETF.NS",
    "PVTBANKADD.NS",
    "QGOLDHALF.NS",
    "SBIETFCON.NS",
    "SBIETFIT.NS",
    "SBIETFPB.NS",
    "SENSEXETF.NS",
    "SETFGOLD.NS",
    "SETFNIF50.NS",
    "SETFNIFBK.NS",
    "SETFNN50.NS",
    "SILVER.NS",
    "SILVERADD.NS",
    "SILVERBEES.NS",
    "SILVERETF.NS",
    "SILVERIETF.NS",
    "SILVRETF.NS",
    "SMALLCAP.NS",
    "TATAGOLD.NS",
    "TATSILV.NS",
    "TECH.NS",
    "TNIDETF.NS",
    "UTIBANKETF.NS",
    "UTINEXT50.NS",
    "UTINIFTETF.NS",
    "UTISENSETF.NS"
]
INTERVAL = '60m'  # 60 minutes (1 hour)
PERIOD = '5d'  # Data period (5 days should be enough for RSI calculation)
RSI_PERIOD = 14  # Typical RSI period
RSI_THRESHOLD = 30  # Alert when RSI goes below this value
CHECK_INTERVAL = 60  # Check every 60 seconds for demo purposes (change to 3600 for hourly)
# Sound configuration
ALERT_SOUND_FILE = 'alert.wav'  # Provide path to your sound file
BEEP_FREQUENCY = 1000  # Frequency in Hz (for Windows beep)
BEEP_DURATION = 1000  # Duration in ms (for Windows beep)

def initialize_session_state():
    """Initialize all session state variables"""
    if 'stock_data' not in st.session_state:
        st.session_state.stock_data = {}
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    if 'last_update' not in st.session_state:
        st.session_state.last_update = None
    if 'monitor_active' not in st.session_state:
        st.session_state.monitor_active = False
    if 'first_run' not in st.session_state:
        st.session_state.first_run = True


def get_stock_data(symbol, period, interval):
    """Fetch stock data from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        return df
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {e}")
        return None


def calculate_rsi(data, window=14):
    """Calculate RSI for given data"""
    delta = data['Close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def play_alert_sound():
    """Play system alert sound using cross-platform methods"""
    try:
        import os
        os.system('osascript -e "beep"')
    except:
        print('\a', end='', flush=True)  # Fallback to terminal bell


def update_stock_data(symbol):
    """Update data for a single stock"""
    try:
        data = get_stock_data(symbol, PERIOD, INTERVAL)
        if data is None or data.empty:
            return False

        # Calculate RSI
        data['RSI'] = calculate_rsi(data, RSI_PERIOD)
        latest_rsi = data['RSI'].iloc[-1]
        latest_price = data['Close'].iloc[-1]
        current_time = datetime.now()

        # Update session state
        st.session_state.stock_data[symbol] = {
            'rsi': latest_rsi,
            'price': latest_price,
            'time': current_time
        }

        # Check for alert condition
        if latest_rsi < RSI_THRESHOLD:
            play_alert_sound()
            alert_exists = any(
                alert['symbol'] == symbol and
                (current_time - alert['time']) < timedelta(hours=24)
                for alert in st.session_state.alerts
            )

            if not alert_exists:
                new_alert = {
                    'symbol': symbol,
                    'rsi': latest_rsi,
                    'price': latest_price,
                    'time': current_time
                }
                st.session_state.alerts.append(new_alert)
                st.toast(f"New alert for {symbol}: RSI {latest_rsi:.2f}", icon="⚠️")

        return True
    except Exception as e:
        st.error(f"Error processing {symbol}: {e}")
        return False


def monitoring_thread(stock_list):
    """Thread function for continuous monitoring"""
    while st.session_state.monitor_active:
        success_count = 0
        current_time = datetime.now()

        for symbol in stock_list:
            if update_stock_data(symbol):
                success_count += 1

        if success_count > 0:
            st.session_state.last_update = current_time.strftime('%Y-%m-%d %H:%M:%S')
            time.sleep(2)  # Small delay to allow Streamlit to update

        time.sleep(CHECK_INTERVAL)


def start_monitoring(stock_list):
    """Start the monitoring thread"""
    if not st.session_state.monitor_active:
        st.session_state.monitor_active = True
        st.session_state.monitor_thread = threading.Thread(
            target=monitoring_thread,
            args=(stock_list,),
            daemon=True
        )
        st.session_state.monitor_thread.start()
        st.toast("Monitoring started!", icon="✅")


def stop_monitoring():
    """Stop the monitoring thread"""
    if st.session_state.monitor_active:
        st.session_state.monitor_active = False
        if 'monitor_thread' in st.session_state:
            st.session_state.monitor_thread.join(timeout=1)
        st.toast("Monitoring stopped", icon="⏹️")


def main():
    st.set_page_config(page_title="Stock RSI Alert Dashboard", layout="wide")
    initialize_session_state()

    st.title("📈 Stock RSI Alert Dashboard")
    st.markdown("""
    This dashboard monitors the Relative Strength Index (RSI) for selected stocks.
    Alerts are generated when RSI falls below 30 (oversold condition).
    """)

    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        custom_stocks = st.text_area(
            "Enter stock symbols (comma separated)",
            ", ".join(DEFAULT_STOCKS)
        )
        processed_stocks = [s.strip().upper() for s in custom_stocks.split(",") if s.strip()]

        if st.button("Start Monitoring"):
            start_monitoring(processed_stocks)

        if st.button("Stop Monitoring"):
            stop_monitoring()

        st.markdown("---")
        st.markdown("### Current Status")
        if st.session_state.last_update:
            st.write(f"Last update: {st.session_state.last_update}")
        else:
            st.write("Waiting for first update...")

        if st.button("Force Refresh All"):
            for symbol in processed_stocks:
                update_stock_data(symbol)
            st.rerun()

    # Initial data load if first run
    if st.session_state.first_run and processed_stocks:
        with st.spinner("Loading initial data..."):
            for symbol in processed_stocks:
                update_stock_data(symbol)
        st.session_state.first_run = False
        st.rerun()

    # Display current RSI values
    st.header("Current RSI Values")

    if not st.session_state.stock_data:
        st.info("No stock data available. Start monitoring to collect data.")
    else:
        # Create dataframe for display
        display_data = []
        st.session_state.stock_data = dict(sorted(st.session_state.stock_data.items(), key=lambda item: item[1]['rsi']))
        for symbol, data in st.session_state.stock_data.items():
            if symbol in processed_stocks:  # Only show currently selected stocks
                display_data.append({
                    'Symbol': symbol,
                    'Price': f" Rs {data['price']:.2f}",
                    'RSI': data['rsi'],
                    'Status': "⚠️ ALERT" if data['rsi'] < RSI_THRESHOLD else "✅ Normal",
                    'Last Updated': data['time'].strftime('%Y-%m-%d %H:%M:%S')
                })

        if display_data:
            df = pd.DataFrame(display_data)
            st.dataframe(
                df,
                column_config={
                    "Status": st.column_config.TextColumn(
                        "Status",
                        help="Stock RSI status",
                        width="medium"
                    ),
                    "RSI": st.column_config.ProgressColumn(
                        "RSI",
                        help="RSI value",
                        format="%.2f",
                        min_value=0,
                        max_value=100,
                    )
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No data for currently selected stocks.")

    # Display alerts
    st.header("Recent Alerts")

    if not st.session_state.alerts:
        st.info("No alerts generated yet.")
    else:
        # Sort alerts by time (newest first)
        sorted_alerts = sorted(
            st.session_state.alerts,
            key=lambda x: x['time'],
            reverse=True
        )

        for alert in sorted_alerts[:10]:  # Show only last 10 alerts
            if alert['symbol'] in processed_stocks:  # Only show alerts for current stocks
                with st.container(border=True):
                    cols = st.columns([1, 3, 2, 2])
                    cols[0].subheader(alert['symbol'])
                    cols[1].metric(
                        "RSI",
                        f"{alert['rsi']:.2f}",
                        delta="Oversold" if alert['rsi'] < RSI_THRESHOLD else None,
                        delta_color="inverse"
                    )
                    cols[2].metric("Price", f"Rs{alert['price']:.2f}")
                    cols[3].write(alert['time'].strftime('%Y-%m-%d %H:%M:%S'))

    # Add some space at the bottom
    st.markdown("---")
    st.caption(f"Note: Data updates every {CHECK_INTERVAL} seconds. Alerts persist for 24 hours.")


if __name__ == "__main__":
    main()