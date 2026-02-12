import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog
from datetime import datetime

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("anonsessage")
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

        self.create_widgets()
        self.ask_connect()

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

    def ask_connect(self):
        while True:
            host_port = simpledialog.askstring(
                "Connect",
                "Enter server address (IP:PORT)\nExample: 192.168.1.100:56789",
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
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((host, port))
            self.running = True
            self.append_message("→ Connected!\n\n")

            threading.Thread(target=self.receive_messages, daemon=True).start()

            self.master.title(f"anonsessage — {host}:{port}")
            self.msg_entry.focus()

        except Exception as e:
            messagebox.showerror("Connection Error", str(e))
            self.ask_connect()

    def receive_messages(self):
        while self.running:
            try:
                data = self.sock.recv(4096).decode("utf-8")
                if not data:
                    break
                self.append_message(data)
            except:
                break

        if self.running:
            self.append_message("\n!!! Connection lost !!!\n")
            self.running = False

    def send_message(self):
        if not self.running:
            return

        msg = self.msg_entry.get().strip()
        self.msg_entry.delete(0, tk.END)

        if not msg:
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        local_message = f"[{timestamp}] You → {msg}\n"

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