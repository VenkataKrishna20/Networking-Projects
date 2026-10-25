import streamlit as st

# -----------------------------------------------------------------------------
# Streamlit Page Setup
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Firewall Simulator - Educational",
    page_icon="🔥",
    layout="centered"
)

st.title("Firewall Simulator - Educational")

# -----------------------------------------------------------------------------
# Stateful Session Initialization
# -----------------------------------------------------------------------------
if "event_logs" not in st.session_state:
    st.session_state.event_logs = []

# Predefined rules: top-down priority matching your original script
DEFAULT_RULES = [
    {"action": "ALLOW", "protocol": "TCP", "port": 22},   # Allow SSH
    {"action": "BLOCK", "protocol": "TCP", "port": 80},   # Block HTTP
    {"action": "ALLOW", "protocol": "TCP", "port": 443},  # Allow HTTPS
    {"action": "BLOCK", "protocol": "UDP", "port": 53},   # Block DNS over UDP
]

def append_log(text):
    """Appends messages to the session event log."""
    st.session_state.event_logs.append(text)

def send_packet(src_ip, dst_ip, protocol, port):
    """Core evaluation matching original FirewallSimulator logic."""
    packet = f"Packet[{src_ip} -> {dst_ip}, {protocol}:{port}]"
    append_log(f"[CLIENT] Sending: {packet}")

    # Evaluate packet against rules
    for idx, rule in enumerate(DEFAULT_RULES, 1):
        if rule["protocol"] == protocol and rule["port"] == port:
            action = rule["action"]
            append_log(f"[FIREWALL] Rule #{idx} matched: {action} ({protocol}:{port})")
            append_log(f"[RESULT] {action}ED {packet}\n")
            return

    # Default policy
    append_log(f"[FIREWALL] No matching rule. DEFAULT ALLOW {packet}\n")

# -----------------------------------------------------------------------------
# Web UI Input Form (Replaces Tkinter Entries and Grid)
# -----------------------------------------------------------------------------
with st.form("firewall_form"):
    col1, col2 = st.columns(2)

    with col1:
        src_ip = st.text_input("Source IP:", value="192.168.1.5")
        protocol = st.text_input("Protocol:", value="TCP").strip().upper()

    with col2:
        dst_ip = st.text_input("Destination IP:", value="203.0.113.10")
        port_raw = st.text_input("Port:", value="80")

    submitted = st.form_submit_button("Send Packet", use_container_width=True)

if submitted:
    try:
        port = int(port_raw)
        send_packet(src_ip, dst_ip, protocol, port)
    except ValueError:
        append_log("[ERROR] Invalid port\n")

# -----------------------------------------------------------------------------
# Event Log Display (Replaces tk.Text Log Box)
# -----------------------------------------------------------------------------
st.markdown("### Event Log:")

# Format logs into a scrollable, terminal-style box
formatted_logs = "\n".join(st.session_state.event_logs)
st.code(formatted_logs if formatted_logs else "No events logged yet.", language="text")

if st.button("Clear Log"):
    st.session_state.event_logs = []
    st.rerun()
