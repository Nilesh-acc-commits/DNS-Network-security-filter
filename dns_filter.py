import time
import threading
import datetime
import requests
import sys
from dnslib import *
from dnslib.server import DNSServer, DNSLogger
from flask import Flask, render_template, jsonify

# --- Configuration ---
BLOCKLIST_URL = "https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts"
UPSTREAM_DNS_IP = "8.8.8.8" # Google DNS
UPSTREAM_DNS_PORT = 53
DNS_PORT = 53               # Standard DNS port (Requires Admin/Sudo)
WEB_PORT = 5000             # Port for the Web Dashboard
BLOCKED_DOMAINS = set()

# --- Global Stats for Dashboard ---
STATS = {
    "total_queries": 0,
    "blocked": 0,
    "allowed": 0,
    "recent_logs": [] # Stores dictionaries: {'time', 'domain', 'status'}
}
MAX_LOGS = 20

# --- Web Application (Flask) ---
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats')
def get_stats():
    return jsonify(STATS)

# --- Blocklist Logic ---
def load_blocklist():
    """Downloads and parses the blocklist."""
    print(f"[*] Fetching blocklist from {BLOCKLIST_URL}...")
    try:
        r = requests.get(BLOCKLIST_URL)
        r.raise_for_status()
        count = 0
        for line in r.text.splitlines():
            # Standard hosts file format: 0.0.0.0 example.com
            if line.startswith("0.0.0.0"):
                parts = line.split()
                if len(parts) >= 2:
                    domain = parts[1]
                    BLOCKED_DOMAINS.add(domain)
                    count += 1
        print(f"[+] Loaded {count} domains into blocklist.")
    except Exception as e:
        print(f"[!] Error loading blocklist: {e}")

# --- DNS Resolver Logic ---
class BlockerResolver:
    def resolve(self, request, handler):
        qname = request.q.qname
        domain = str(qname).rstrip('.')
        
        STATS["total_queries"] += 1
        
        # 1. Check Blocklist
        if domain in BLOCKED_DOMAINS:
            STATS["blocked"] += 1
            log_entry = {"time": datetime.datetime.now().strftime("%H:%M:%S"), "domain": domain, "status": "BLOCKED"}
            self.update_logs(log_entry)
            print(f"[BLOCKED] {domain}")
            
            # Return 0.0.0.0 (The "Block")
            reply = request.reply()
            reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
            return reply

        # 2. Forward to Upstream (Allow)
        try:
            STATS["allowed"] += 1
            log_entry = {"time": datetime.datetime.now().strftime("%H:%M:%S"), "domain": domain, "status": "ALLOWED"}
            self.update_logs(log_entry)
            print(f"[ALLOWED] {domain}")

            # Send request to Google DNS (8.8.8.8)
            proxy_req = request.send(UPSTREAM_DNS_IP, UPSTREAM_DNS_PORT)
            reply = DNSRecord.parse(proxy_req)
            return reply
        except Exception as e:
            print(f"[!] Upstream Error: {e}")
            return request.reply()

    def update_logs(self, entry):
        STATS["recent_logs"].insert(0, entry)
        if len(STATS["recent_logs"]) > MAX_LOGS:
            STATS["recent_logs"].pop()

# --- Main Execution ---
if __name__ == '__main__':
    # 1. Load the blocklist
    load_blocklist()

    # 2. Start DNS Server in a separate thread
    resolver = BlockerResolver()
    dns_server = DNSServer(resolver, port=DNS_PORT, address="0.0.0.0", logger=DNSLogger(prefix=False))
    
    print(f"[*] Starting DNS Server on port {DNS_PORT}...")
    
    # Daemon=True means this thread dies when the main program dies
    dns_thread = threading.Thread(target=dns_server.start_thread) 
    dns_thread.daemon = True 
    dns_thread.start()

    # 3. Start Web Dashboard in the main thread
    print(f"[*] Starting Web Dashboard on http://localhost:{WEB_PORT}")
    try:
        app.run(host='0.0.0.0', port=WEB_PORT, debug=False, use_reloader=False)
    except PermissionError:
        print("[!] Permission Denied. Try running with 'sudo'.")
    except KeyboardInterrupt:
        print("\nStopping servers...")
        dns_server.stop()