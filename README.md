# Blockchain-Based Food Supply Chain Tracker

![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B.svg)
![Blockchain](https://img.shields.io/badge/Technology-Blockchain-orange.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)

## 📌 Project Overview
The **Blockchain Food Supply Chain Tracker** is a Decentralized Application (DApp) designed to ensure data accuracy, transparency, and traceability in the food industry. Built using Python and Streamlit, this application implements a custom blockchain using **SHA-256 cryptographic hashing** and **Proof-of-Work (PoW)** consensus. 

It provides an immutable ledger to track food products from farm to retail, utilizes automated smart contracts to enforce food safety thresholds (temperature and humidity), and features built-in data science analytics dashboards for fraud detection and supply chain optimization.

---

## ✨ Key Features
- **⛓️ Immutable Ledger:** Core blockchain architecture ensuring data integrity. Once a transaction is recorded, it cannot be altered without breaking the hash chain.
- **🛡️ Automated Smart Contracts:** Real-time validation of food safety conditions. Transactions exceeding maximum safe temperature or humidity thresholds are automatically rejected.
- **🔍 Full Traceability:** Track the complete lifecycle of a specific product batch from origin (farm) to destination (supermarket).
- **📊 Data Analytics & Insights:** Interactive dashboards using Plotly to monitor supply chain performance, temperature distributions, and stakeholder pass/fail rates.
- **🚨 Fraud & Anomaly Detection:** Automated detection of anomalous transactions, identifying compromised cold-chain transport or storage issues.
- **🔨 Security Demonstration:** A built-in tamper simulation tool to visually demonstrate how blockchain immediately detects data modification.
- **📥 Data Exporting:** Export simulated blockchain data to CSV for further data science modeling or download the complete hash chain in JSON format.

---

## 👥 Stakeholder Roles
The system is designed for four primary participants in the food supply chain:
1. **🧑‍🌾 Farmer:** Registers new product batches into the blockchain at the point of origin.
2. **🚚 Distributor:** Transfers ownership and records transport environmental conditions (e.g., Cold Chain Truck).
3. **🏪 Retailer:** Receives the products and performs final quality inspections upon arrival at the supermarket.
4. **🕵️ Quality Inspector:** Verifies product conditions at various checkpoints (e.g., Warehouses) to ensure compliance.

---

## 💻 Technology Stack
- **Backend & Core Logic:** Python 3 (Object-Oriented Programming for `Block` and `Blockchain` classes).
- **Frontend / UI:** Streamlit (For building the interactive web-based DApp interface).
- **Cryptography:** `hashlib` (SHA-256 hashing algorithm).
- **Data Manipulation:** Pandas & NumPy.
- **Data Visualization:** Plotly Graph Objects.

---

## ⚙️ Installation & Setup

Follow these steps to run the application locally on your machine.

**1. Clone the repository**
```bash
https://github.com/Padumainduwara/Blockchain-Food-Supply-Tracker.git
