import psutil
import time

# Get the CPU usage percentage for each core
cpu_percentages = psutil.cpu_percent(interval=1, percpu=True)
print("CPU usage per core:")
for i, percentage in enumerate(cpu_percentages):
    print(f"Core {i}: {percentage}%")

# Get the overall CPU usage percentage
overall_cpu_percentage = psutil.cpu_percent(interval=1)
print(f"Overall CPU usage: {overall_cpu_percentage}%")

# Alternatively, get a summary every few seconds
print("\nMonitoring overall CPU usage every 2 seconds:")
try:
    while True:
        overall_cpu_percentage = psutil.cpu_percent(interval=2)
        print(f"Overall CPU usage: {overall_cpu_percentage}%")
except KeyboardInterrupt:
    print("\nExiting monitoring.")
