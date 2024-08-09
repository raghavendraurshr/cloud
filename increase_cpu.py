import requests
import threading
import time

# Configuration
haproxy_url = 'http://4.7.147.112'  # Replace with your HAProxy URL
num_threads = 100  # Number of concurrent threads
requests_per_thread = 1000  # Number of requests per thread
request_interval = 0.1  # Interval between requests in seconds

def send_requests():
    for _ in range(requests_per_thread):
        try:
            for _ in range(10000):  # This loop adds CPU work
                pass

            response = requests.get(haproxy_url)
            print(f"Request sent, status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Request failed: {e}")
        time.sleep(request_interval)

def main():
    print("Starting load test...")
    threads = []
    # Create and start threads
    for _ in range(num_threads):
        thread = threading.Thread(target=send_requests)
        thread.start()
        threads.append(thread)
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    print("Load test completed.")

if __name__ == "__main__":
    main()
