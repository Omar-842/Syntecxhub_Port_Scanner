import socket
import sys
import threading
from datetime import datetime

target = input("Enter the ip address of the target: ")

try:
    t_ip = socket.gethostbyname(target)
except socket.gaierror:
    print("Hostname could not be resolved. Exiting")
    sys.exit()

choice = input("Scan a (s)ingle port or a (r)ange? [s/r]: ").strip().lower()

if choice == "s":
    port = int(input("Enter the port to scan: "))
    start_port = port
    end_port = port
else:
    start_port = int(input("Enter the start port: "))
    end_port = int(input("Enter the end port: "))

log_filename = "scan_results.log"
log_file = open(log_filename, "w")
print_lock = threading.Lock()  

print("..........Scanning Open Ports..........")
log_file.write("Scan of {} started at {}\n".format(t_ip, datetime.now()))

t1 = datetime.now()

def scan_port(port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((t_ip, port))
        sock.close()

        if result == 0:
            status = "Open"
        else:
            status = "Closed"

    except socket.timeout:
        status = "Timeout"
    except socket.error as e:
        status = "Error: " + str(e)

    line = " Port " + str(port) + " is " + status

    with print_lock:
        if status == "Open":
            print(line)
            log_file.write(line + "\n")


try:
    threads = []
    for port in range(start_port, end_port + 1):
        t = threading.Thread(target=scan_port, args=(port,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

except KeyboardInterrupt:
    print("You pressed Ctrl+C")
    log_file.write("Scan interrupted by user (Ctrl+C)\n")
    log_file.close()
    sys.exit()

t2 = datetime.now()
total = t2 - t1

summary = "Scanning Completed in: " + str(total)
print(summary)
log_file.write(summary + "\n")
log_file.close()

print("Full results (including closed/timeout ports) saved in " + log_filename)
