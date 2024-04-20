import tkinter as tk
from tkinter import filedialog
from utils import api
import os


csv_file = None

def clear_error():
    error_label.config(text="")

def select_file():
    clear_error()
    global csv_file
    csv_file = filedialog.askopenfilename()
    file_name = os.path.basename(csv_file)
    file_size = os.path.getsize(csv_file)
    file_label.config(text=f"File: {file_name}, Size: {file_size} bytes")


def run_update():
    if not input_field1.get() or not input_field2.get():
        error_label.config(text="There is an empty input field")
        return
    if csv_file is None:
        error_label.config(text="No file selected")
        return
    try:
        token = api.generate_token(access_key=input_field1.get().strip(), secret_access_key=input_field2.get().strip())
        status = api.update_working_hours(token, csv_file)
    except ValueError as e:
        error_label.config(text=str(e))
        return

def main():
    global file_label, input_field1, input_field2, error_label

    # Create the main window
    root = tk.Tk()
    root.title("HRWorks Worktime Importer")

    # Add a header
    header = tk.Label(root, text="Please upload the CSV file to update the working times", font=("Arial", 14))
    header.pack(pady=20)


    # Add label and first text input field
    input_label1 = tk.Label(root, text="Access Key:", font=("Arial", 10))
    input_label1.pack(pady=5)
    input_field1 = tk.Entry(root, width=30)
    input_field1.pack(pady=5)

    # Add label and second text input field
    input_label2 = tk.Label(root, text="Secret Access Key:", font=("Arial", 10))
    input_label2.pack(pady=5)
    input_field2 = tk.Entry(root, width=30)
    input_field2.pack(pady=5)

    # Add a file selection button
    file_button = tk.Button(root, text="Select File", command=select_file, font=("Arial", 12))
    file_button.pack(pady=10)
    file_label = tk.Label(root, text="", font=("Arial", 10))
    file_label.pack(pady=0)

    # Add a run update button
    update_button = tk.Button(root, text="Run Update", command=run_update, font=("Arial", 14, 'bold'))
    update_button.pack(pady=10)

    # Add a label to display error messages
    error_label = tk.Label(root, text="", font=("Arial", 10), fg="red")
    error_label.pack(pady=0)

    # Start the GUI event loop
    root.mainloop()

if __name__ == "__main__":
    main()