import socket
import threading
import sys
from datetime import datetime

clients = {}
nicknames = {}
messages_history = []

HOST = "0.0.0.0"
PORT = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
except OSError as e:
    print("Failed to start server:", e)
    print("Port might be already in use. Try another port.")
    sys.exit(1)

server.listen()
print("\n" + "═"*60)
local_ip = socket.gethostbyname(socket.gethostname())
print(f"  Server started →  {local_ip}:{PORT}  ")
print(f"  You can also use:  127.0.0.1:{PORT}  (localhost only)")
print("═"*60 + "\n")
print("Waiting for connections...\n")

def broadcast(message, sender_addr=None):
    for addr, client in list(clients.items()):
        if sender_addr is not None and addr == sender_addr:
            continue
        try:
            client.send(message)
        except:
            client.close()
            del clients[addr]
            if addr in nicknames:
                del nicknames[addr]

def handle_client(client, addr):
    print(f"Connected: {addr}")
    
    temp_nick = f"User{len(clients)}"
    nicknames[addr] = temp_nick
    clients[addr] = client
    
    welcome = f"→ You connected as {temp_nick}\n"
    client.send(welcome.encode("utf-8"))
    
    for msg in messages_history[-30:]:
        client.send(msg.encode("utf-8"))
    
    buffer = ""
    
    while True:
        try:
            data = client.recv(8192).decode("utf-8")
            if not data:
                break
                
            buffer += data
            
            while '\n' in buffer:
                message, buffer = buffer.split('\n', 1)
                message = message.strip()
                
                if not message:
                    continue
                
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted = f"[{timestamp}] {nicknames[addr]} → {message}\n"
                
                print(formatted, end="", flush=True)
                messages_history.append(formatted)

                if len(messages_history) > 100:
                    messages_history.pop(0)
                
                broadcast(formatted.encode("utf-8"), addr)
                
        except UnicodeDecodeError as e:
            print(f"Unicode error with {addr}: {e}")
            try:
                data = client.recv(8192).decode("utf-8", errors="ignore")
                buffer += data
            except:
                break
        except Exception as e:
            print(f"Error with {addr}: {e}")
            break
    
    print(f"Disconnected: {addr}")
    client.close()
    if addr in clients:
        del clients[addr]
    if addr in nicknames:
        del nicknames[addr]

def main():
    while True:
        try:
            client, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(client, addr), daemon=True)
            thread.start()
        except KeyboardInterrupt:
            print("\nServer shutting down...")
            break
        except Exception as e:
            print("Accept error:", e)
    
    server.close()

if __name__ == "__main__":
    main()