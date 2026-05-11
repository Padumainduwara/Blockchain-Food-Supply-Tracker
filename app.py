import streamlit as st
import hashlib
import time
import json
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Food Supply Chain Blockchain", layout="wide")

# ==========================================
# 1. BLOCKCHAIN CORE
# ==========================================
class Block:
    def __init__(self, index, transactions, previous_hash, difficulty=3):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.mine_block()

    def calculate_hash(self):
        block_string = f"{self.index}{self.timestamp}{json.dumps(self.transactions, sort_keys=True, default=str)}{self.previous_hash}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self):
        target = "0" * self.difficulty
        while not self.calculate_hash().startswith(target):
            self.nonce += 1
        return self.calculate_hash()


class Blockchain:
    def __init__(self, difficulty=3):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "Genesis Block - System Started", "0" * 64, self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, transaction_data):
        new_block = Block(len(self.chain), transaction_data, self.get_latest_block().hash, self.difficulty)
        self.chain.append(new_block)
        return new_block

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]
            if current.hash != current.calculate_hash():
                return False, f"Block {i} hash mismatch - data tampered!"
            if current.previous_hash != previous.hash:
                return False, f"Block {i} chain broken!"
        return True, "Blockchain is valid and secure."

    def tamper_block(self, block_index, fake_data):
        if 0 < block_index < len(self.chain):
            self.chain[block_index].transactions = fake_data
            return True
        return False

# ==========================================
# 2. SMART CONTRACT (Food Safety)
# ==========================================
def check_safety(temp, humidity, temp_max, humidity_max):
    reasons = []
    if temp > temp_max:
        reasons.append(f"Temp {temp}°C > {temp_max}°C")
    if humidity > humidity_max:
        reasons.append(f"Humidity {humidity}% > {humidity_max}%")
    if reasons:
        return f"Rejected ({'; '.join(reasons)})"
    return "Approved (Safe)"

# ==========================================
# 3. INIT STATE
# ==========================================
if 'blockchain' not in st.session_state:
    st.session_state.blockchain = Blockchain(difficulty=3)

if 'simulated_data' not in st.session_state:
    st.session_state.simulated_data = pd.DataFrame(columns=[
        "Batch ID", "Stakeholder", "Action", "Location", "Transport Details",
        "Temperature (C)", "Humidity (%)", "Status", "Block Hash", "Timestamp"
    ])

if 'temp_threshold' not in st.session_state:
    st.session_state.temp_threshold = 8.0

if 'humidity_threshold' not in st.session_state:
    st.session_state.humidity_threshold = 85

if 'tamper_attempts' not in st.session_state:
    st.session_state.tamper_attempts = 0

# ==========================================
# 4. HASH CHAIN VISUALIZATION
# ==========================================
def render_hash_chain():
    chain = st.session_state.blockchain.chain
    if len(chain) < 2:
        return None

    # Create node labels and edges
    node_labels = []
    edge_sources = []
    edge_targets = []
    node_colors = []

    chain_valid, _ = st.session_state.blockchain.is_chain_valid()

    for i, block in enumerate(chain):
        if i == 0:
            label = f"Genesis<br>Block 0"
        else:
            short_hash = block.hash[:10] + "..."
            label = f"Block {i}<br>{short_hash}"
        node_labels.append(label)
        node_colors.append("#28a745" if chain_valid else "#dc3545")

        if i > 0:
            edge_sources.append(i - 1)
            edge_targets.append(i)

    # Build the Sankey/flow diagram
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=30,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=node_labels,
            color=node_colors,
            x=[0.1 + 0.8 * i / max(1, len(chain)-1) for i in range(len(chain))],
            y=[0.5] * len(chain)
        ),
        link=dict(
            source=edge_sources,
            target=edge_targets,
            value=[1] * len(edge_sources),
            color=["rgba(40, 167, 69, 0.3)" if chain_valid else "rgba(220, 53, 69, 0.3)"] * len(edge_sources),
            label=[f"Hash: {chain[i].hash[:16]}..." for i in range(1, len(chain))]
        )
    )])

    fig.update_layout(
        title="Blockchain Hash Chain",
        font=dict(size=12),
        height=200 + len(chain) * 30,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig

# ==========================================
# 5. PROCESS TRANSACTION
# ==========================================
def process_transaction(batch_id, stakeholder, action, location, transport, temp, hum):
    status = check_safety(temp, hum, st.session_state.temp_threshold, st.session_state.humidity_threshold)
    timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    transaction = {
        "Batch ID": batch_id, "Stakeholder": stakeholder,
        "Action": action, "Location": location,
        "Transport Details": transport,
        "Temperature (C)": temp, "Humidity (%)": hum,
        "Status": status, "Timestamp": timestamp_str
    }

    new_block = st.session_state.blockchain.add_block(transaction)

    new_row = pd.DataFrame([{
        "Batch ID": batch_id, "Stakeholder": stakeholder,
        "Action": action, "Location": location,
        "Transport Details": transport,
        "Temperature (C)": temp, "Humidity (%)": hum,
        "Status": status,
        "Block Hash": new_block.hash[:16] + "...",
        "Timestamp": timestamp_str
    }])
    st.session_state.simulated_data = pd.concat([st.session_state.simulated_data, new_row], ignore_index=True)

    return status, new_block

# ==========================================
# 6. UI HEADER
# ==========================================
st.title("Blockchain Food Supply Chain Tracker")
st.markdown("A Decentralized Application (DApp) for tracking food products. Ensures transparency, traceability, and food safety using SHA-256 hashing with Proof-of-Work mining.")

chain_valid, chain_msg = st.session_state.blockchain.is_chain_valid()
if chain_valid:
    st.success(f"System Status: {chain_msg}")
else:
    st.error(f"⚠ WARNING: {chain_msg}")
    st.session_state.tamper_attempts += 1

# ==========================================
# 7. SIDEBAR
# ==========================================
with st.sidebar:
    # Smart Contract Configuration
    with st.expander("Smart Contract Rules", expanded=True):
        old_temp = st.session_state.temp_threshold
        old_hum = st.session_state.humidity_threshold
        new_temp = st.slider("Max Temperature (°C)", 0.0, 15.0, st.session_state.temp_threshold, 0.5,
                            help="Transactions exceeding this temp will be rejected")
        new_hum = st.slider("Max Humidity (%)", 50, 100, st.session_state.humidity_threshold, 1,
                           help="Transactions exceeding this humidity will be rejected")
        if new_temp != old_temp or new_hum != old_hum:
            st.session_state.temp_threshold = new_temp
            st.session_state.humidity_threshold = new_hum
            st.info(f"Contract updated: Max Temp={new_temp}°C, Max Humidity={new_hum}%")
        st.caption("These rules act as a smart contract — transactions are validated against them before being added to the blockchain.")

    st.divider()

    # Stakeholder Actions
    st.header("Stakeholder Actions")

    with st.form("tx_form"):
        stakeholder = st.selectbox("Select Role", ["Farmer", "Distributor", "Retailer", "Quality Inspector", "Logistics"])
        action_type = st.selectbox("Select Action", ["Register New Product", "Transfer Ownership", "Quality Inspection", "Shipment Update"])
        batch_id = st.text_input("Batch ID", "BCH-1001")
        location = st.text_input("Location", "Farm, Nuwara Eliya")
        transport = st.selectbox("Transport Method", ["N/A (At Facility)", "Cold Chain Truck", "Air Freight", "Cargo Ship", "Refrigerated Van"])
        temperature = st.slider("Temperature (C)", -5.0, 15.0, 4.0, 0.5)
        humidity = st.slider("Humidity (%)", 30, 100, 60, 1)

        submitted = st.form_submit_button("Submit to Blockchain", use_container_width=True)
        if submitted:
            status, block = process_transaction(batch_id, stakeholder, action_type, location, transport, temperature, humidity)
            if "Approved" in status:
                st.success(f"✅ Block #{block.index} added. Nonce: {block.nonce:,}")
            else:
                st.error(f"❌ Smart contract rejected: {status}")
            st.rerun()

    st.divider()

    # Data Simulation
    st.subheader("Data Simulation")
    with st.expander("Load Sample Scenarios", expanded=False):
        if st.button("Generate Supply Chain Scenarios", use_container_width=True):
            # Batch 1: Successful delivery
            process_transaction("BCH-9001", "Farmer", "Register New Product", "Farm, Dambulla", "N/A (At Facility)", 4.0, 60)
            process_transaction("BCH-9001", "Distributor", "Transfer Ownership", "Transit Highway", "Cold Chain Truck", 4.5, 62)
            process_transaction("BCH-9001", "Retailer", "Quality Inspection", "Supermarket, Colombo", "N/A (At Facility)", 5.0, 65)

            # Batch 2: Temperature abuse (fraud detection demo)
            process_transaction("BCH-9002", "Farmer", "Register New Product", "Farm, Nuwara Eliya", "N/A (At Facility)", 2.0, 50)
            process_transaction("BCH-9002", "Distributor", "Transfer Ownership", "Transit Highway", "Cold Chain Truck", 10.5, 70)
            process_transaction("BCH-9002", "Quality Inspector", "Quality Inspection", "Warehouse, Kandy", "N/A (At Facility)", 9.0, 68)

            # Batch 3: Humidity issue during storage
            process_transaction("BCH-9003", "Farmer", "Register New Product", "Farm, Anuradhapura", "N/A (At Facility)", 3.0, 55)
            process_transaction("BCH-9003", "Logistics", "Transfer Ownership", "Cold Storage, Colombo", "Cold Chain Truck", 5.0, 92)
            process_transaction("BCH-9003", "Retailer", "Quality Inspection", "Supermarket, Colombo", "N/A (At Facility)", 5.5, 80)

            st.success("✅ 3 batch scenarios added (9001=OK, 9002=Temp abuse, 9003=Humidity issue)")
            st.rerun()

    st.divider()

    # Blockchain Security Demo
    st.subheader("Blockchain Security Demo")
    col1, col2 = st.columns(2)
    with col1:
        max_block = len(st.session_state.blockchain.chain) - 1
        tamper_idx = st.number_input("Block to tamper", min_value=1, max_value=max(1, max_block), value=1, disabled=(max_block < 1))
    with col2:
        if st.button("🔨 Simulate Tampering", use_container_width=True, type="primary"):
            chain_len = len(st.session_state.blockchain.chain)
            if tamper_idx >= chain_len:
                st.error(f"❌ Block {tamper_idx} doesn't exist. Chain has only {chain_len} blocks (0 to {chain_len-1}). Add transactions first.")
            else:
                original = st.session_state.blockchain.chain[tamper_idx].transactions
                st.session_state.blockchain.tamper_block(tamper_idx, {"Batch ID": f"TAMPERED-BLOCK-{tamper_idx}", "Status": "FAKE DATA", "Original": str(original)[:50]})
                st.session_state.tamper_attempts += 1
                st.error(f"⚠ Block {tamper_idx} tampered! Chain integrity compromised. See red warning above and Tab 4.")
            st.rerun()

    st.caption("Demonstrates blockchain immutability — any tampering breaks the hash chain and is immediately detected.")

    st.divider()

    # Reset
    if st.button("🔄 Reset & Clear All Data", use_container_width=True):
        st.session_state.blockchain = Blockchain(difficulty=3)
        st.session_state.simulated_data = pd.DataFrame(columns=[
            "Batch ID", "Stakeholder", "Action", "Location", "Transport Details",
            "Temperature (C)", "Humidity (%)", "Status", "Block Hash", "Timestamp"
        ])
        st.session_state.tamper_attempts = 0
        st.success("All data reset.")
        st.rerun()

    st.divider()

    # Data Export
    if not st.session_state.simulated_data.empty:
        st.subheader("Data Export")
        csv = st.session_state.simulated_data.to_csv(index=False)
        st.download_button("📥 Download CSV", csv, "food_supply_chain_data.csv", "text/csv", use_container_width=True)

        # Export blockchain as JSON
        chain_data = []
        for block in st.session_state.blockchain.chain:
            chain_data.append({
                "index": block.index,
                "timestamp": datetime.fromtimestamp(block.timestamp).isoformat(),
                "transactions": block.transactions,
                "previous_hash": block.previous_hash,
                "hash": block.hash,
                "nonce": block.nonce
            })
        json_str = json.dumps(chain_data, indent=2, default=str)
        st.download_button("📥 Download Blockchain (JSON)", json_str, "blockchain_export.json", "application/json", use_container_width=True)

# ==========================================
# 8. TABS
# ==========================================
tab1, tab2, tab3, tab4, = st.tabs(["Product Ledger", "Trace Product", "Data Insights", "Blockchain Structure"])

with tab1:
    st.subheader("Product History (Immutable Ledger)")
    if not st.session_state.simulated_data.empty:
        df = st.session_state.simulated_data

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Transactions", len(df))
        col2.metric("Unique Batches", df["Batch ID"].nunique())
        col3.metric("Approved", len(df[df["Status"].str.contains("Approved")]))
        col4.metric("Rejected", len(df[df["Status"].str.contains("Rejected")]))

        st.divider()

        # Color code status
        def color_status(val):
            if "Approved" in str(val): return "background-color:#d4edda;color:#155724"
            if "Rejected" in str(val): return "background-color:#f8d7da;color:#721c24"
            return ""
        styled = df.style.map(color_status, subset=["Status"])
        st.dataframe(styled, use_container_width=True, height=300)
        st.caption(f"Green = Approved (Safe) | Red = Rejected (Risk detected)")
    else:
        st.info("No transactions yet. Use the sidebar to add data or load sample scenarios.")

with tab2:
    st.subheader("Trace Product by Batch ID")
    if not st.session_state.simulated_data.empty:
        search_id = st.text_input("Enter Batch ID (e.g. BCH-9001):")
        if search_id:
            filtered = st.session_state.simulated_data[st.session_state.simulated_data["Batch ID"] == search_id]
            if not filtered.empty:
                st.markdown(f"**Lifecycle for Batch: {search_id}**")
                for _, row in filtered.iterrows():
                    emoji = "✅" if "Approved" in str(row["Status"]) else "❌"
                    st.markdown(f"- {emoji} **{row['Timestamp']}** | {row['Action']} by **{row['Stakeholder']}** at {row['Location']} | Status: **{row['Status']}**")
                st.divider()
                st.dataframe(filtered, use_container_width=True)
            else:
                st.warning(f"Batch ID '{search_id}' not found.")
    else:
        st.info("Add data first using the sidebar.")

with tab3:
    st.subheader("Supply Chain Analytics & Fraud Detection")
    if len(st.session_state.simulated_data) > 0:
        df = st.session_state.simulated_data

        # Row 1: Temperature and Humidity charts
        col1, col2 = st.columns(2)
        with col1:
            fig_temp = px.line(df, x="Timestamp", y="Temperature (C)", color="Batch ID", markers=True,
                             title="Temperature Monitoring Across Supply Chain",
                             labels={"Timestamp": "Time", "Temperature (C)": "Temperature (°C)"})
            fig_temp.add_hline(y=st.session_state.temp_threshold, line_dash="dot", line_color="red",
                             annotation_text=f"Max Allowed: {st.session_state.temp_threshold}°C")
            fig_temp.update_layout(hovermode="x unified")
            st.plotly_chart(fig_temp, use_container_width=True)

        with col2:
            fig_hum = px.line(df, x="Timestamp", y="Humidity (%)", color="Batch ID", markers=True,
                            title="Humidity Monitoring Across Supply Chain",
                            labels={"Timestamp": "Time", "Humidity (%)": "Humidity (%)"})
            fig_hum.add_hline(y=st.session_state.humidity_threshold, line_dash="dot", line_color="orange",
                            annotation_text=f"Max Allowed: {st.session_state.humidity_threshold}%")
            fig_hum.update_layout(hovermode="x unified")
            st.plotly_chart(fig_hum, use_container_width=True)

        # Row 2: Distribution charts
        col3, col4 = st.columns(2)
        with col3:
            fig_status = px.pie(df, names="Status", title="Transaction Safety Status Distribution",
                              color="Status",
                              color_discrete_map={
                                  "Approved (Safe)": "#28a745",
                                  "Rejected (High Temp Risk)": "#dc3545",
                                  "Rejected (High Humidity Risk)": "#fd7e14",
                                  "Rejected (Temp; Humidity)": "#e83e8c"
                              })
            st.plotly_chart(fig_status, use_container_width=True)

        with col4:
            # Temperature distribution histogram
            fig_hist = px.histogram(df, x="Temperature (C)", color="Status",
                                  title="Temperature Distribution by Safety Status",
                                  nbins=15,
                                  labels={"Temperature (C)": "Temperature (°C)", "count": "Frequency"},
                                  color_discrete_map={
                                      "Approved (Safe)": "#28a745",
                                      "Rejected (High Temp Risk)": "#dc3545",
                                      "Rejected (High Humidity Risk)": "#fd7e14"
                                  })
            fig_hist.add_vline(x=st.session_state.temp_threshold, line_dash="dot", line_color="red",
                             annotation_text=f"Threshold: {st.session_state.temp_threshold}°C")
            st.plotly_chart(fig_hist, use_container_width=True)

        # Row 3: Stakeholder performance
        st.subheader("Stakeholder Performance")
        stakeholder_stats = df.groupby("Stakeholder").agg(
            Total=("Status", "count"),
            Approved=("Status", lambda x: sum("Approved" in str(v) for v in x)),
            Rejected=("Status", lambda x: sum("Rejected" in str(v) for v in x)),
            Avg_Temp=("Temperature (C)", "mean"),
            Avg_Humidity=("Humidity (%)", "mean")
        ).reset_index()
        stakeholder_stats["Pass Rate"] = (stakeholder_stats["Approved"] / stakeholder_stats["Total"] * 100).round(1).astype(str) + "%"
        st.dataframe(stakeholder_stats, use_container_width=True)

        # Fraud Detection
        st.subheader("Fraud & Anomaly Detection")
        anomalies = df[df["Status"].str.contains("Rejected")]
        if not anomalies.empty:
            st.warning(f"⚠ Anomalous transactions detected: {len(anomalies)} out of {len(df)}")
            st.dataframe(anomalies[["Timestamp", "Batch ID", "Stakeholder", "Temperature (C)", "Humidity (%)", "Status"]], use_container_width=True)
            affected = anomalies["Batch ID"].unique()
            st.error(f"🚨 Affected product batches: {', '.join(affected)}")

            with st.expander("Investigation Report"):
                st.markdown("""
                **Potential causes of anomalies:**
                - **Cold chain equipment failure**: Refrigeration breakdown during transit leads to temperature spikes
                - **Improper storage**: Warehouses exceeding safe humidity thresholds
                - **Transport delay**: Extended transit time without proper temperature control
                - **Human error**: Incorrect handling or monitoring equipment malfunction

                **Recommendations:**
                - Implement real-time IoT temperature monitoring
                - Set up automatic alerts when thresholds are approached
                - Regular maintenance of cold chain equipment
                - Staff training on proper handling procedures
                """)
        else:
            st.success("✅ No anomalies detected. All transactions passed safety checks.")

        # Supply chain performance
        st.subheader("Supply Chain Performance Summary")
        safe_rate = round((len(df) - len(anomalies)) / len(df) * 100, 1) if len(df) > 0 else 0
        col_a, col_b, col_c, col_d = st.columns(4)
        col_a.metric("Safety Rate", f"{safe_rate}%",
                    delta=f"{safe_rate - 100:.1f}%" if safe_rate < 100 else "Perfect")
        col_b.metric("Avg Temperature", f"{df['Temperature (C)'].mean():.1f}°C")
        col_c.metric("Avg Humidity", f"{df['Humidity (%)'].mean():.0f}%")
        col_d.metric("Tamper Attempts", st.session_state.tamper_attempts)
    else:
        st.info("Add data first using the sidebar to see analytics.")

with tab4:
    st.subheader("Blockchain Blocks (SHA-256 + Proof-of-Work)")

    # Hash chain visualization
    fig_chain = render_hash_chain()
    if fig_chain:
        st.plotly_chart(fig_chain, use_container_width=True)
        st.divider()

    # Block details
    for block in st.session_state.blockchain.chain:
        if block.index == 0:
            with st.expander(f"🗃 Block #{block.index} (Genesis Block)"):
                st.code(f"Hash: {block.hash}", language="text")
        else:
            # Check if this block is tampered
            is_tampered = block.hash != block.calculate_hash()
            icon = "⚠" if is_tampered else "✅"
            label = f"{icon} Block #{block.index} - Hash: {block.hash[:16]}... (Nonce: {block.nonce:,})"
            if is_tampered:
                label = f"🚨 {label} [TAMPERED]"
            with st.expander(label):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write(f"**Previous Hash:** `{block.previous_hash}`")
                    st.write(f"**Current Hash:** `{block.hash}`")
                    st.write(f"**Nonce (mining attempts):** {block.nonce:,}")
                    st.write(f"**Timestamp:** {datetime.fromtimestamp(block.timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
                with col_b:
                    expected_hash = block.calculate_hash()
                    if block.hash != expected_hash:
                        st.error("⚠ HASH MISMATCH — Block has been tampered!")
                        st.write(f"Expected hash: `{expected_hash}`")
                        st.write(f"Actual hash:   `{block.hash}`")
                    else:
                        st.success("✅ Hash verified — Block is intact")
                st.divider()
                st.json(block.transactions)

    # Mining stats
    if len(st.session_state.blockchain.chain) > 1:
        st.divider()
        st.subheader("Mining Statistics")
        total_nonce = sum(b.nonce for b in st.session_state.blockchain.chain[1:])
        avg_nonce = total_nonce // max(1, len(st.session_state.blockchain.chain) - 1)
        col_x, col_y, col_z = st.columns(3)
        col_x.metric("Total Mining Effort", f"{total_nonce:,} hashes")
        col_y.metric("Avg per Block", f"{avg_nonce:,} hashes")
        col_z.metric("Total Blocks", len(st.session_state.blockchain.chain))
