import json
import time
import urllib.request
import urllib.error
import threading
from concurrent.futures import ThreadPoolExecutor

# Target settings
BASE_URL = "http://localhost:8000/api/v1"
QUERY_URL = f"{BASE_URL}/external/query"
TOKEN_URL = f"{BASE_URL}/external/token"

print("🚀 Starting EvoKnow Performance Load Test...")

# 1. Fetch JWT Token for authentication
token = None
try:
    token_req = urllib.request.Request(
        TOKEN_URL,
        data=json.dumps({"client_name": "LoadTestRunner", "scopes": ["read"]}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(token_req, timeout=5) as response:
        res_data = json.loads(response.read().decode("utf-8"))
        token = res_data["access_token"]
        print("🔑 JWT Token obtained successfully.")
except Exception as e:
    print(f"⚠️ Warning: Failed to obtain JWT token ({e}). Continuing with unauthenticated tests.")

# Load test parameters
CONCURRENT_USERS = 5
REQUESTS_PER_USER = 3
TOTAL_REQUESTS = CONCURRENT_USERS * REQUESTS_PER_USER
QUESTION = "What is the role of Apache Kafka in the system?"

latencies = []
success_count = 0
failure_count = 0
lock = threading.Lock()

def send_query_request():
    global success_count, failure_count
    headers = {
        "Content-Type": "application/json"
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    payload = json.dumps({
        "question": QUESTION,
        "top_k": 2
    }).encode("utf-8")
    
    start_time = time.time()
    try:
        req = urllib.request.Request(
            QUERY_URL,
            data=payload,
            headers=headers,
            method="POST"
        )
        # 10s timeout to allow local LLM inference
        with urllib.request.urlopen(req, timeout=15) as response:
            res_body = json.loads(response.read().decode("utf-8"))
            elapsed = (time.time() - start_time) * 1000
            
            with lock:
                latencies.append(elapsed)
                success_count += 1
                
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.reason}")
        with lock:
            failure_count += 1
    except Exception as e:
        print(f"❌ Request failed: {e}")
        with lock:
            failure_count += 1

# Start timers
start_test_time = time.time()

print(f"⚡ Simulating {CONCURRENT_USERS} concurrent users sending {REQUESTS_PER_USER} queries each...")

with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
    futures = [executor.submit(send_query_request) for _ in range(TOTAL_REQUESTS)]
    # Wait for all requests to finish
    for f in futures:
        f.result()

total_test_duration = time.time() - start_test_time

# Calculations
if latencies:
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
else:
    avg_latency = min_latency = max_latency = 0

throughput = TOTAL_REQUESTS / total_test_duration

print("\n==================================================")
print("📊 PERFORMANCE LOAD TEST RESULTS")
print("==================================================")
print(f"Target URL:         {QUERY_URL}")
print(f"Concurrent Users:   {CONCURRENT_USERS}")
print(f"Total Requests:     {TOTAL_REQUESTS}")
print(f"Success Requests:   {success_count} ({success_count/TOTAL_REQUESTS*100:.1f}%)")
print(f"Failed Requests:    {failure_count} ({failure_count/TOTAL_REQUESTS*100:.1f}%)")
print(f"Total Test Time:    {total_test_duration:.2f} seconds")
print(f"Throughput:         {throughput:.2f} req/sec")
print(f"Min Latency:        {min_latency:.2f} ms")
print(f"Max Latency:        {max_latency:.2f} ms")
print(f"Avg Latency:        {avg_latency:.2f} ms")
print("==================================================")
