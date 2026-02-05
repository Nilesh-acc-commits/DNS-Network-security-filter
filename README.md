ko# 🛡️ DNS Shield: Python DNS Sinkhole & Ad Blocker

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Educational-orange)

**DNS Shield** is a lightweight, intermediate-level cybersecurity tool that acts as a local DNS server to block advertisements, trackers, and malicious websites at the network level.

Functioning similarly to Pi-hole, this Python-based application intercepts DNS queries, compares them against a real-time threat intelligence blocklist, and sinkholes malicious requests while allowing legitimate traffic to pass through.


## ✨ Key Features

* **Real-Time Traffic Interception:** Captures DNS requests on Port 53 before they leave your machine.
* **Ad & Malware Blocking:** Automatically blocks domains found in the [StevenBlack](https://github.com/StevenBlack/hosts) unified hosts file.
* **Live Web Dashboard:** A Flask-based interface (Port 5000) visualizing blocked vs. allowed traffic in real-time.
* **DNS Sinkholing:** Returns `0.0.0.0` for malicious domains, preventing connections completely.
* **Upstream Forwarding:** Legit traffic is seamlessly forwarded to Google DNS (8.8.8.8).

## 🛠️ Tech Stack

* **Python 3:** Core logic.
* **dnslib:** For parsing and crafting DNS packets.
* **Flask:** For the web-based statistics dashboard.
* **Requests:** For fetching and updating blocklists.

## 🚀 Installation & Usage

### Prerequisites
* Python 3.x installed.
* Administrative/Root privileges (required to bind to Port 53).

### Step 1: Clone the Repository
git clone   [https://github.com/Nilesh-acc-commits/DNS-Network-security-filter]
(https://github.com/Nilesh-acc-commits/DNS-Network-security-filter)


!!Save the index.html in a separate templates directory in the dns_filter directory!!
dns_filter/templates/index.html
