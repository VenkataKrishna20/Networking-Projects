import streamlit as st
import psutil
import time

# Page Configuration
st.set_page_config(
    page_title="Real-Time Network Monitor",
    page_icon="📡",
    layout="wide"
)

st.title("📡 Real-Time Network Monitoring Tool")
st.caption("A safe, real-time bandwidth monitor querying OS kernel counters via psutil.")

# Initialize Session State
if "monitoring" not in st.session_state:
    st.session_state.monitoring = False

if "logs" not in st.session_state:
    st.session_state.logs = []

# Control Buttons
col_start, col_stop = st.columns(2)

with col_start:
    if st.button("Start Monitoring", use_container_width=True, type="primary"):
        if not st.session_state.monitoring:
            st.session_state.monitoring = True
            st.session_state.logs.append("Monitoring started...")

with col_stop:
    if st.button("Stop Monitoring", use_container_width=True):
        if st.session_state.monitoring:
            st.session_state.monitoring = False
            st.session_state.logs.append("Monitoring stopped.")

# Metric Placeholders
st.markdown("### 📊 Live Traffic Statistics")
m1, m2, m3 = st.columns(3)
m4, m5, m6 = st.columns(3)

up_speed_ph = m1.empty()
down_speed_ph = m2.empty()
pkt_sent_ph = m3.empty()
pkt_recv_ph = m4.empty()
total_up_ph = m5.empty()
total_down_ph = m6.empty()

st.markdown("---")
st.markdown("### 📋 Event Audit Log")
log_box_ph = st.empty()

# Active Polling Loop
if st.session_state.monitoring:
    prev = psutil.net_io_counters()
    prev_time = time.perf_counter()

    while st.session_state.monitoring:
        time.sleep(1)
        
        now = psutil.net_io_counters()
        now_time = time.perf_counter()
        
        dt = now_time - prev_time
        if dt <= 0:
            continue

        # Rate Calculations Normalized Per Second
        upload_bps = int((now.bytes_sent - prev.bytes_sent) / dt)
        download_bps = int((now.bytes_recv - prev.bytes_recv) / dt)
        packets_sent = int((now.packets_sent - prev.packets_sent) / dt)
        packets_recv = int((now.packets_recv - prev.packets_recv) / dt)

        # Baseline Snapshot Reset
        prev = now
        prev_time = now_time

        # Render Metrics
        up_speed_ph.metric("Upload Speed", f"{upload_bps:,} B/s")
        down_speed_ph.metric("Download Speed", f"{download_bps:,} B/s")
        pkt_sent_ph.metric("Packets Sent (last 1s)", f"{packets_sent:,}")
        pkt_recv_ph.metric("Packets Received (last 1s)", f"{packets_recv:,}")
        total_up_ph.metric("Total Bytes Sent", f"{now.bytes_sent:,} B")
        total_down_ph.metric("Total Bytes Received", f"{now.bytes_recv:,} B")

        # Update Event Log Display
        log_box_ph.code("\n".join(st.session_state.logs), language="text")

else:
    # Display Default State When Stopped
    up_speed_ph.metric("Upload Speed", "0 B/s")
    down_speed_ph.metric("Download Speed", "0 B/s")
    pkt_sent_ph.metric("Packets Sent (last 1s)", "0")
    pkt_recv_ph.metric("Packets Received (last 1s)", "0")
    total_up_ph.metric("Total Bytes Sent", "0 B")
    total_down_ph.metric("Total Bytes Received", "0 B")
    
    log_content = "\n".join(st.session_state.logs) if st.session_state.logs else "Monitoring inactive."
    log_box_ph.code(log_content, language="text")
