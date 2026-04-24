import tkinter as tk
from ftp_client import del_file, connect_to_server, list_files, get_file_content, put_content, get_data_socket
from dotenv import load_dotenv
import os

load_dotenv()
PASSWORD = os.getenv("TEST_USER_PASSWORD") or ""


control_socket = None
server_name = None
port = None
username = None
password = None
filename = None

def on_connect():
    global server_name, port, username, password, control_socket
    server_name = server_name_entry.get()
    port = int(port_entry.get())
    username = username_entry.get()
    password = password_entry.get()
    control_socket = connect_to_server(server_name, port, username, password)
    file_listbox.delete(0, tk.END)
    data_socket = get_data_socket(control_socket, server_name)
    for file in list_files(control_socket, data_socket):
        file_listbox.insert(tk.END, file)


def on_save(text):
    content = text.get("1.0", tk.END)
    data_socket = get_data_socket(control_socket, server_name)
    put_content(control_socket, data_socket, filename, content.encode())
    refresh_listbox()


def open_editor(content=""):
    editor_window = tk.Toplevel(root)
    editor_window.title("Edit file")
    text = tk.Text(editor_window)
    text.insert(tk.END, content)
    text.pack()
    save_button = tk.Button(editor_window, text="Save", command=lambda: on_save(text))
    save_button.pack()


def on_create():
    global filename
    filename = filename_entry.get()
    open_editor()


def refresh_listbox():
    file_listbox.delete(0, tk.END)
    data_socket = get_data_socket(control_socket, server_name)
    for file in list_files(control_socket, data_socket):
        file_listbox.insert(tk.END, file)


def on_read():
    global filename
    filename = filename_entry.get()
    data_socket = get_data_socket(control_socket, server_name)
    content = get_file_content(control_socket, data_socket, filename).decode()
    file_content.delete("1.0", tk.END)
    file_content.insert(tk.END, content)


def on_update():
    global filename
    filename = filename_entry.get()
    data_socket = get_data_socket(control_socket, server_name)
    content = get_file_content(control_socket, data_socket, filename).decode()
    open_editor(content)


def on_delete():
    global filename
    filename = filename_entry.get()
    del_file(control_socket, filename)
    file_content.delete("1.0", tk.END)
    refresh_listbox()


root = tk.Tk()
root.title("FTP Client")

tk.Label(root, text="Server Name:").pack()
server_name_entry = tk.Entry(root)
server_name_entry.insert(0, "localhost")
server_name_entry.pack()

tk.Label(root, text="Port:").pack()
port_entry = tk.Entry(root)
port_entry.insert(0, "21")
port_entry.pack()

tk.Label(root, text="Username:").pack()
username_entry = tk.Entry(root)
username_entry.insert(0, "TestUser")
username_entry.pack()

tk.Label(root, text="Password:").pack()
password_entry = tk.Entry(root, show="*")
password_entry.insert(0, PASSWORD)
password_entry.pack()

connect_button = tk.Button(root, text="Connect", command=on_connect)
connect_button.pack()

tk.Label(root, text="File content:").pack()
file_content = tk.Text(root)
file_content.pack()

tk.Label(root, text="List of files:").pack()
file_listbox = tk.Listbox(root)
file_listbox.pack()

tk.Label(root, text="Select file:").pack()
filename_entry = tk.Entry(root)
filename_entry.insert(0, "example.txt")
filename_entry.pack()

create_button = tk.Button(root, text="Create file", command=on_create)
create_button.pack()

read_button = tk.Button(root, text="Retrieve file", command=on_read)
read_button.pack()

update_button = tk.Button(root, text="Update file", command=on_update)
update_button.pack()

delete_button = tk.Button(root, text="Delete file", command=on_delete)
delete_button.pack()

root.mainloop()

if control_socket:
    control_socket.sendall("QUIT\r\n".encode())
    control_socket.close()
