import socket
import threading
import sys
import random
from datetime import datetime

clients = {}
nicknames = {}

HOST = "0.0.0.0"
PORT = 56789

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

try:
    server.bind((HOST, PORT))
except OSError as e:
    sys.exit(1)

server.listen()
print("\n" + "="*60)

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
except:
    local_ip = socket.gethostbyname(socket.gethostname())

print(f"Server started -> {local_ip}:{PORT}")
print(f"Local access:   127.0.0.1:{PORT}")
print("Waiting for connections...\n")

def generate_anonymous_nick():
    adjectives = ["Red", "Blue", "Green", "Yellow", "Purple", "Orange", "Gray", "Dark", "Light", "Cyber"]
    nouns = ["Fox", "Wolf", "Eagle", "Shark", "Phoenix", "Ghost", "Shadow", "Storm", "Thunder", "Spirit"]
    number = random.randint(10, 99)
    return f"{random.choice(adjectives)}{random.choice(nouns)}{number}"

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
    temp_nick = generate_anonymous_nick()
    nicknames[addr] = temp_nick
    clients[addr] = client
    
    print(f"New user connected: {temp_nick}")
    
    welcome = f"-> You are {temp_nick}\n"
    client.send(welcome.encode("utf-8"))
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    join_message = f"\n[{timestamp}] {temp_nick} joined\n"
    broadcast(join_message.encode("utf-8"), sender_addr=addr)
    
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
                formatted = f"[{timestamp}] {nicknames[addr]} -> {message}\n"
                
                print(formatted, end="", flush=True)
                
                broadcast(formatted.encode("utf-8"), addr)
                
        except Exception as e:
            break
    
    if addr in nicknames:
        print(f"User disconnected: {nicknames[addr]}")
        
        timestamp = datetime.now().strftime("%H:%M:%S")
        leave_message = f"\n[{timestamp}] {nicknames[addr]} left\n"
        
        for other_addr, other_client in list(clients.items()):
            if other_addr != addr:
                try:
                    other_client.send(leave_message.encode("utf-8"))
                except:
                    pass
    
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
    
    server.close()

if __name__ == "__main__":
    main()
