import tkinter as tk
import threading
import socket as sock_module
from node import socket_node, CLOSE_MESSAGE

node = None


def get_own_ip():
    return sock_module.gethostbyname(sock_module.gethostname())


def on_start():
    global node
    ip = get_own_ip()
    port = int(port_entry.get())
    interval = float(interval_entry.get())
    dead_intervals = int(dead_entry.get())

    node = socket_node(ip, port, interval, dead_intervals)
    thread = threading.Thread(target=node.main_loop, daemon=True)
    thread.start()

    start_button.config(state=tk.DISABLED)
    port_entry.config(state=tk.DISABLED)
    status_label.config(text=f"Running on {ip}:{port}")


def on_apply():
    if node is None:
        return
    node.set_dead_interval_amounts(int(dead_entry.get()))
    node.set_message_time_interval(float(interval_entry.get()))


def on_close():
    if node is not None:
        node.clean_up()
    root.destroy()


def refresh():
    if node is not None:
        alive_addresses = list(node.alive_dict.keys())
        count_label.config(text=str(len(alive_addresses)))
        nodes_listbox.delete(0, tk.END)
        for addr in alive_addresses:
            nodes_listbox.insert(tk.END, f"{addr[0]}:{addr[1]}")
    root.after(1000, refresh)


root = tk.Tk()
root.title("Broadcast Node Counter")
root.protocol("WM_DELETE_WINDOW", on_close)

tk.Label(root, text="Port:").pack()
port_entry = tk.Entry(root)
port_entry.insert(0, "9000")
port_entry.pack()

tk.Label(root, text="Broadcast interval (sec):").pack()
interval_entry = tk.Entry(root)
interval_entry.insert(0, "3")
interval_entry.pack()

tk.Label(root, text="Dead intervals count:").pack()
dead_entry = tk.Entry(root)
dead_entry.insert(0, "3")
dead_entry.pack()

start_button = tk.Button(root, text="Start", command=on_start)
start_button.pack()

apply_button = tk.Button(root, text="Apply settings", command=on_apply)
apply_button.pack()

status_label = tk.Label(root, text="Not started")
status_label.pack()

tk.Label(root, text="Running copies:").pack()
count_label = tk.Label(root, text="0")
count_label.pack()

tk.Label(root, text="Active nodes (ip:port):").pack()
nodes_listbox = tk.Listbox(root, width=40)
nodes_listbox.pack()

refresh()
root.mainloop()
