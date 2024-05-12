import tkinter as tk
from tkinter import filedialog
from utils import api
import os
import requests

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

def download_template():
    url = 'https://raw.githubusercontent.com/Tsatsch/hrworks-sync/main/example/Arbeitszeitenvorlage.xlsx'
    response = requests.get(url)
    destination = filedialog.asksaveasfilename(defaultextension=".xlsx")
    if destination:
        with open(destination, 'wb') as f:
            f.write(response.content)

def run_update():
    if not input_field1.get() or not input_field2.get():
        error_label.config(text="Es gibt ein leeres Eingabefeld. Bitte füllen Sie alle Felder aus.")
        return
    if csv_file is None:
        error_label.config(text="Keine Datei ausgewählt. Bitte laden Sie eine CSV-Datei hoch.")
        return

    update_button.config(text="Import läuft...", state="disabled")
    root.update()
    try:
        token = api.generate_token(access_key=input_field1.get().strip(), secret_access_key=input_field2.get().strip())
        status = api.update_working_hours(token, csv_file)
    except ValueError as e:
        error_label.config(text=str(e))
        return
    finally:
        update_button.config(text="Import Starten", state="normal")  # Change the button text back
    success_label.config(text="Update erfolgreich durchgeführt!", fg="green")


def main():
    global file_label, input_field1, input_field2, error_label, success_label, update_button, root

    # Create the main window
    root = tk.Tk()
    root.title("HRWorks Zeitbuchung Importer")
    root.geometry("1280x800")
    # center content
    frame = tk.Frame(root)
    frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

    # header
    header = tk.Label(frame, text="HRWorks Zeitbuchung Importer", font=("Arial", 24, 'bold'))
    subheader = tk.Label(frame, text="Bitte laden Sie die CSV-Datei hoch, um die Arbeitszeiten zu aktualisieren", font=("Arial", 18))
    header.pack(pady=20)
    subheader.pack(pady=10)


    # label and first text input field
    input_label1 = tk.Label(frame, text="Access Key:", font=("Arial", 18))
    input_label1.pack(pady=5)
    input_field1 = tk.Entry(frame, width=30)
    input_field1.pack(pady=5)

    # label and second text input field
    input_label2 = tk.Label(frame, text="Secret Access Key:", font=("Arial", 18))
    input_label2.pack(pady=5)
    input_field2 = tk.Entry(frame, width=30)
    input_field2.pack(pady=5)

    # a file selection button
    file_button = tk.Button(frame, text="Datei hochladen", command=select_file, font=("Arial", 20))
    file_button.pack(pady=10)
    # a download template button
    download_button = tk.Button(frame, text="Template herunterladen", command=download_template, font=("Arial", 18))
    download_button.pack(pady=10)

    file_label = tk.Label(frame, text="", font=("Arial", 18))
    file_label.pack(pady=0)

    # a run update button
    update_button = tk.Button(text="Import Starten", command=run_update, font=("Arial", 24, 'bold'), fg="blue")
    update_button.pack(side=tk.BOTTOM, pady=20)

    # a label to display error messages & success messages
    error_label = tk.Label(frame, text="", font=("Arial", 16), fg="red")
    error_label.pack(pady=0)

    success_label = tk.Label(frame, text="", font=("Arial", 16), fg="green")
    success_label.pack(pady=0)

    # Start the GUI event loop
    frame.mainloop()

if __name__ == "__main__":
    main()