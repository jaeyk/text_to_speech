import socket
import threading
import time
import webbrowser
import tkinter as tk

import uvicorn

from main import app

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.25)
        return sock.connect_ex((host, port)) == 0


class PracticeTalkDesktop:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("PracticeTalk")
        self.root.geometry("380x170")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.status_var = tk.StringVar(value="Starting local server...")
        self.server = None
        self.server_thread = None
        self.opened_browser = False
        self.poll_count = 0

        self._build_ui()
        self._start_server()

    def _build_ui(self) -> None:
        frame = tk.Frame(self.root, padx=16, pady=16)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="PracticeTalk Desktop", font=("Helvetica", 14, "bold")).pack(anchor="w")
        tk.Label(frame, textvariable=self.status_var, wraplength=340, justify="left").pack(anchor="w", pady=(8, 12))

        button_row = tk.Frame(frame)
        button_row.pack(anchor="w")

        tk.Button(button_row, text="Open App", command=self.open_app, width=12).pack(side="left")
        tk.Button(button_row, text="Quit", command=self.on_close, width=12).pack(side="left", padx=(10, 0))

    def _start_server(self) -> None:
        if is_port_open(HOST, PORT):
            self.status_var.set(f"Server already running at {URL}")
            self.open_app()
            return

        config = uvicorn.Config(app, host=HOST, port=PORT, log_level="warning")
        self.server = uvicorn.Server(config)
        self.server_thread = threading.Thread(target=self.server.run, daemon=True)
        self.server_thread.start()
        self.root.after(150, self._poll_server)

    def _poll_server(self) -> None:
        if is_port_open(HOST, PORT):
            self.status_var.set(f"Running at {URL}")
            self.open_app()
            return

        self.poll_count += 1
        if self.poll_count >= 80:
            self.status_var.set("Server failed to start. Close and try again.")
            return
        self.root.after(150, self._poll_server)

    def open_app(self) -> None:
        if not self.opened_browser:
            webbrowser.open(URL)
            self.opened_browser = True

    def on_close(self) -> None:
        if self.server is not None:
            self.server.should_exit = True
            if self.server_thread is not None and self.server_thread.is_alive():
                self.server_thread.join(timeout=2.0)
        self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    PracticeTalkDesktop().run()


if __name__ == "__main__":
    main()
