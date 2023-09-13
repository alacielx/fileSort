import tkinter as tk
from tkinter import ttk
import requests

def downloadProgressBar(url, destination_path, title = "Downloading..."):
    def read_bytes():
        nonlocal bytes_read
        bytes_read += 500
        progress_var.set((bytes_read / max_bytes) * 100)
        if bytes_read < max_bytes:
            root.after(100, read_bytes)
        else:
            download_file(url, destination_path)

    def download_file(url, destination_path):
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))

        with open(destination_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                root.update_idletasks()

        root.destroy()

    root = tk.Tk()
    root.title(title)

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 300) // 2
    y = (screen_height - 70) // 2
    root.geometry(f"300x70+{x}+{y}")

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(padx=20, pady=20, fill='both', expand=True)

    bytes_read = 0
    max_bytes = 0

    max_bytes = 50000
    progress_var.set(0)
    read_bytes()

    root.mainloop()
