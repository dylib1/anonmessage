import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import datetime
import random
import string

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("anonmessage")
        self.master.geometry("520x580")
        self.master.resizable(False, False)

        try:
            self.master.attributes('-alpha', 0.99)
            self.master.attributes('-transparentcolor', 'grey')
            self.master.wm_attributes('-topmost', False)
        except:
            pass

        self.sock = None
        self.running = False
        self.is_dark_mode = True
        self.session_id = self.generate_session_id()
        self.use_proxy = False
        self.proxy_host = ""
        self.proxy_port = 0

        self.create_widgets()
        self.ask_proxy_settings()
        self.ask_connect()

    def generate_session_id(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    def create_widgets(self):
        self.theme_btn = tk.Button(
            self.master,
            text="Light Mode",
            command=self.toggle_theme,
            width=12
        )
        self.theme_btn.pack(anchor="w", padx=10, pady=(10, 0))

        self.chat_area = scrolledtext.ScrolledText(
            self.master,
            wrap=tk.WORD,
            state='disabled',
            font=("Consolas", 11),
            height=22
        )
        self.chat_area.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        input_frame = tk.Frame(self.master)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        self.msg_entry = tk.Entry(input_frame, font=("Consolas", 11))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.msg_entry.bind("<Return>", lambda e: self.send_message())

        send_btn = tk.Button(input_frame, text="Send", width=10,
                             command=self.send_message)
        send_btn.pack(side=tk.RIGHT)

        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.apply_theme()

    def apply_theme(self):
        if self.is_dark_mode:
            bg = "#0d1117"
            fg = "#c9d1d9"
            accent = "#58a6ff"
            entry_bg = "#161b22"
            btn_bg = "#21262d"
            btn_fg = "#c9d1d9"
            select_bg = "#1f6feb"
            self.theme_btn.config(text="Light Mode")
        else:
            bg = "#ffffff"
            fg = "#0d1117"
            accent = "#0969da"
            entry_bg = "#f6f8fa"
            btn_bg = "#f0f0f0"
            btn_fg = "#24292f"
            select_bg = "#bde0ff"
            self.theme_btn.config(text="Dark Mode")

        self.master.configure(bg=bg)

        self.chat_area.configure(
            bg=bg,
            fg=fg,
            insertbackground=fg,
            selectbackground=select_bg,
            selectforeground=fg
        )

        self.msg_entry.configure(
            bg=entry_bg,
            fg=fg,
            insertbackground=fg,
            selectbackground=select_bg
        )

        self.theme_btn.configure(bg=btn_bg, fg=btn_fg, activebackground=accent)

        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg)
            elif isinstance(widget, tk.Button) and widget != self.theme_btn:
                widget.configure(bg=btn_bg, fg=btn_fg, activebackground=accent)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

    def append_message(self, text):
        self.chat_area.configure(state='normal')
        self.chat_area.insert(tk.END, text)
        self.chat_area.see(tk.END)
        self.chat_area.configure(state='disabled')

    def clear_chat(self):
        self.chat_area.configure(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.configure(state='disabled')

    def self_destruct(self):
        if messagebox.askyesno("Self Destruct", "Delete all messages and disconnect?"):
            self.clear_chat()
            self.append_message("Chat history destroyed\n")
            if self.running:
                self.on_closing()

    def ask_proxy_settings(self):
        use_proxy = messagebox.askyesno(
            "Proxy Settings",
            "Use SOCKS5 proxy?\n\n"
            "Yes = Configure proxy\n"
            "No = Direct connection"
        )
        
        if use_proxy:
            while True:
                proxy_str = simpledialog.askstring(
                    "SOCKS5 Proxy",
                    "Enter SOCKS5 proxy (host:port)\n"
                    "Example: 127.0.0.1:9050 (Tor)\n"
                    "Example: 192.168.1.100:1080",
                    parent=self.master
                )
                
                if not proxy_str:
                    self.use_proxy = False
                    break
                
                try:
                    host, port_str = proxy_str.split(":")
                    port = int(port_str)
                    self.use_proxy = True
                    self.proxy_host = host
                    self.proxy_port = port
                    self.append_message(f"-> SOCKS5 proxy configured: {host}:{port}\n")
                    break
                except:
                    messagebox.showerror("Error", "Invalid proxy format. Expected host:port")
        else:
            self.use_proxy = False
            self.append_message("-> Direct connection (no proxy)\n")

    def create_socket(self):
        if self.use_proxy:
            try:
                import socks
                sock = socks.socksocket()
                sock.set_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
                return sock
            except ImportError:
                messagebox.showerror("Error", "PySocks module is required for proxy connection.\nInstall: pip install PySocks")
                return None
        else:
            return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def ask_connect(self):
        while True:
            host_port = simpledialog.askstring(
                "Connect",
                "Enter server address (IP:PORT)\n"
                "Example: 192.168.1.100:56789",
                parent=self.master
            )
            if not host_port:
                self.master.destroy()
                return

            try:
                host, port_str = host_port.split(":")
                port = int(port_str)
                break
            except:
                messagebox.showerror("Error", "Invalid format. Expected IP:PORT")

        try:
            self.sock = self.create_socket()
            if self.sock is None:
                self.ask_connect()
                return
                
            self.sock.connect((host, port))
            self.running = True
            
            if self.use_proxy:
                self.append_message(f"-> Connected via SOCKS5 proxy ({self.proxy_host}:{self.proxy_port})\n\n")
            else:
                self.append_message("-> Connected (direct)\n\n")

            threading.Thread(target=self.receive_messages, daemon=True).start()

            self.master.title(f"anonmessage — {host}:{port}")
            self.msg_entry.focus()

        except ImportError:
            messagebox.showerror("Error", "PySocks module is not installed.\nPlease install: pip install PySocks")
            self.ask_connect()
        except Exception as e:
            error_msg = str(e)
            if self.use_proxy:
                messagebox.showerror("Proxy Connection Error", 
                                   f"Failed to connect via proxy {self.proxy_host}:{self.proxy_port}\n\n{error_msg}")
            else:
                messagebox.showerror("Connection Error", error_msg)
            self.ask_connect()

    def receive_messages(self):
        buffer = ""
        while self.running:
            try:
                data = self.sock.recv(16384).decode("utf-8", errors="ignore")
                if not data:
                    break

                buffer += data

                while '\n' in buffer:
                    message, buffer = buffer.split('\n', 1)
                    if message.strip():
                        self.append_message(message + "\n")

            except:
                break

        if self.running:
            self.append_message("\n!!! Connection lost\n")
            self.running = False

    def send_message(self):
        if not self.running:
            return

        msg = self.msg_entry.get().strip()
        self.msg_entry.delete(0, tk.END)

        if not msg:
            return
            
        elif msg == "/clear":
            self.clear_chat()
            return
        elif msg == "/selfdestruct":
            self.self_destruct()
            return
        elif msg == "/proxy":
            status = f"Proxy: {'Enabled' if self.use_proxy else 'Disabled'}"
            if self.use_proxy:
                status += f" ({self.proxy_host}:{self.proxy_port})"
            self.append_message(status + "\n")
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        local_message = f"[{timestamp}] You -> {msg}\n"

        self.append_message(local_message)

        try:
            self.sock.send((msg + "\n").encode("utf-8"))
        except:
            self.append_message("Send error — connection lost\n")
            self.running = False

    def on_closing(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except:
                pass
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClient(root)
    root.mainloop()
