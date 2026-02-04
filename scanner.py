#!/usr/bin/env python3
# ==========================================
# Advanced Port Scanner
# Made by: Furqan Ansari
# ==========================================

import socket
import threading
import argparse
from queue import Queue
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

# ---------- COLORS ----------
GREEN = Fore.GREEN
RED = Fore.RED
CYAN = Fore.CYAN
YELLOW = Fore.YELLOW
MAGENTA = Fore.MAGENTA
RESET = Style.RESET_ALL

# ---------- BANNER ----------
def banner():
    print(CYAN + r"""
 ██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ █████╗ ███╗   ██╗
 ██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝██╔══██╗████╗  ██║
 ██████╔╝██║   ██║██████╔╝   ██║   █████╗  ██║     ███████║██╔██╗ ██║
 ██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝  ██║     ██╔══██║██║╚██╗██║
 ██║     ╚██████╔╝██║  ██║   ██║   ███████╗╚██████╗██║  ██║██║ ╚████║
 ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝
""" + RESET)

    print(MAGENTA + "        Advanced Port Scanner")
    print(MAGENTA + "        Made by: Furqan Ansari")
    print(CYAN + "-" * 70 + RESET)


# ---------- GLOBALS ----------
queue = Queue()
open_ports = []
lock = threading.Lock()

# ---------- FUNCTIONS ----------
def scan_port(target, port, timeout):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        result = s.connect_ex((target, port))

        if result == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "Unknown"

            try:
                s.send(b"HEAD / HTTP/1.1\r\n\r\n")
                banner_data = s.recv(1024).decode(errors="ignore").strip()
                if not banner_data:
                    banner_data = "No banner"
            except:
                banner_data = "No banner"

            with lock:
                print(
                    GREEN +
                    f"[OPEN] Port {port:<5} | Service: {service:<12} | Banner: {banner_data[:40]}"
                )
                open_ports.append((port, service, banner_data))

        s.close()
    except:
        pass


def worker(target, timeout):
    while not queue.empty():
        port = queue.get()
        scan_port(target, port, timeout)
        queue.task_done()


# ---------- MAIN ----------
def main():
    banner()

    parser = argparse.ArgumentParser(description="Advanced Port Scanner - Made by Furqan Ansari")
    parser.add_argument("target", help="Target IP or Hostname")
    parser.add_argument("-p", "--ports", help="Port range (e.g. 1-1000)", default="1-1024")
    parser.add_argument("-t", "--threads", help="Number of threads", type=int, default=100)
    parser.add_argument("--timeout", help="Socket timeout", type=float, default=1)
    parser.add_argument("-o", "--output", help="Save results to file")

    args = parser.parse_args()

    start_port, end_port = map(int, args.ports.split("-"))

    print(YELLOW + f"[+] Target      : {args.target}")
    print(YELLOW + f"[+] Port Range : {start_port}-{end_port}")
    print(YELLOW + f"[+] Threads    : {args.threads}")
    print(YELLOW + f"[+] Started At : {datetime.now()}")
    print(CYAN + "-" * 70 + RESET)

    for port in range(start_port, end_port + 1):
        queue.put(port)

    for _ in range(args.threads):
        t = threading.Thread(target=worker, args=(args.target, args.timeout))
        t.daemon = True
        t.start()

    queue.join()

    print(CYAN + "-" * 70 + RESET)
    print(GREEN + f"[✔] Scan Completed | Open Ports Found: {len(open_ports)}")

    if args.output:
        with open(args.output, "w") as f:
            f.write(f"Advanced Port Scan Report\n")
            f.write(f"Target: {args.target}\n")
            f.write(f"Time  : {datetime.now()}\n\n")
            for port, service, banner_data in open_ports:
                f.write(f"Port {port} | Service: {service} | Banner: {banner_data}\n")

        print(GREEN + f"[✔] Report saved to: {args.output}")


if __name__ == "__main__":
    main()

