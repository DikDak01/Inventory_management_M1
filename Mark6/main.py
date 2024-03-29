import sqlite3
import tkinter as tk
from tkinter import simpledialog, Toplevel
from PIL import Image, ImageTk
import datetime

class Lagerverwaltung:

    def __init__(self):
        self.con = sqlite3.connect("management.db")
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS LAGERVERWALTUNG(
            Datum DATE
            Bezeichnung TEXT,
            Typ TEXT,
            Menge INT,
            Raum TEXT,
            Schrank TEXT,
            CONSTRAINT Datum_unique UNIQUE (Datum));
            CONSTRAINT Bezeichnung_unique UNIQUE (Bezeichnung));
            CONSTRAINT Typ_unique UNIQUE (Typ));
            CONSTRAINT Menge_unique UNIQUE (Menge));
            CONSTRAINT Raum_unique UNIQUE (Raum));
            CONSTRAINT Schrank_unique UNIQUE (Schrank));"""
        )
        self.con.commit()

    def insert_data(self, Datum, Bezeichnung, Typ, Menge, Raum, Schrank):
        # Überprüfen, ob der Artikel bereits existiert
        self.cur.execute("SELECT Name FROM LAGERVERWALTUNG WHERE Name=?", (Datum,Bezeichnung,Typ,Menge,Raum,Schrank ))
        existing_row = self.cur.fetchone()
        if existing_row:
            print(f"Der Artikel '{Typ}' existiert bereits im Lager.")
        else:
            self.cur.execute(
                """INSERT INTO LAGERVERWALTUNG (Name, Raum, Schrank)
                VALUES (?, ?, ?)""", (Datum, Bezeichnung, Typ, Menge, Raum, Schrank)
            )
            self.con.commit()
            print(f"Der Artikel '{Bezeichnung}' wurde erfolgreich hinzugefügt.")

    def insert_multiple_data(self, data):
        """
        Insert multiple records at once
        data: List of tuples (Datum, Bezeichnung, Typ, Menge, Raum, Schrank)
        """
        for item in data:
            self.name = item[0]
            self.insert_data(*item)

    def retrieve_data(self):
        self.cur.execute("SELECT * FROM LAGERVERWALTUNG")
        rows = self.cur.fetchall()
        for row in rows:
            print(row)

    def close_connection(self):
        self.con.close()


class MultiListbox(tk.Frame):
    def __init__(self, master, columns):
        tk.Frame.__init__(self, master)

        # Header
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X)

        for column in columns:
            label = tk.Label(header_frame, text=column)
            label.pack(side=tk.LEFT, padx=5, pady=5)

        # Listbox
        self.listBox = tk.Listbox(self, selectmode=tk.SINGLE)
        self.listBox.pack(fill=tk.BOTH, expand=True)

    def insert(self, values):
        self.listBox.insert(tk.END, values)

    def curselection(self):
        return self.listBox.curselection()

    def delete(self, first, last=None):
        self.listBox.delete(first, last)

    def get(self, first, last=None):
        return self.listBox.get(first, last)

    def size(self):
        return self.listBox.size()

    def see(self, index):
        self.listBox.see(index)

    def selection_clear(self, first, last=None):
        self.listBox.selection_clear(first, last)

    def selection_set(self, first, last=None):
        self.listBox.selection_set(first, last)


class GUI(Lagerverwaltung):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Lagerverwaltung")

        # Listbox mit mehreren Spalten
        self.multi_listbox = MultiListbox(master, ["Datum", "Bezeichnung", "Typ", "Menge", "Raum", "Schranknummer"])
        self.multi_listbox.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

        # Buttons
        add_button = tk.Button(master, text="Hinzufügen", command=self.add_entry)
        add_button.pack(padx=10, pady=5, fill=tk.X)

        edit_button = tk.Button(master, text="Bearbeiten", command=self.edit_entry)
        edit_button.pack(padx=10, pady=5, fill=tk.X)

        delete_button = tk.Button(master, text="Löschen", command=self.delete_entry)
        delete_button.pack(padx=10, pady=5, fill=tk.X)

        show_image_button = tk.Button(master, text="Bild anzeigen", command=self.show_image)
        show_image_button.pack(padx=10, pady=5, fill=tk.X)

        close_button = tk.Button(master, text="Fenster schließen", command=master.quit)
        close_button.pack(padx=10, pady=5, fill=tk.X)

    def add_entry(self):
        name = simpledialog.askstring("Neuen Eintrag hinzufügen", "Name:")
        if name:
            raum = simpledialog.askstring("Neuen Eintrag hinzufügen", "Raum:")
            if raum:
                schrank = simpledialog.askstring("Neuen Eintrag hinzufügen", "Schrank:")
                if schrank:
                    self.insert_data(name, raum, schrank)
                    self.update_listbox()

    def edit_entry(self):
        selected_index = self.multi_listbox.curselection()
        if selected_index:
            entry = self.multi_listbox.get(selected_index)
            old_name = entry[0]
            new_name = simpledialog.askstring("Eintrag bearbeiten", "Neue Bezeichnung:", initialvalue=old_name)
            if new_name:
                new_raum = simpledialog.askstring("Eintrag bearbeiten", "Neuer Raum:")
                if new_raum:
                    new_schrank = simpledialog.askstring("Eintrag bearbeiten", "Neue Schranknummer:")
                    if new_schrank:
                        self.cur.execute("UPDATE LAGERVERWALTUNG SET Name=?, Raum=?, Schrank=? WHERE Name=?", (new_name, new_raum, new_schrank, old_name))
                        self.con.commit()
                        self.update_listbox()

    def delete_entry(self):
        selected_index = self.multi_listbox.curselection()
        if selected_index:
            entry = self.multi_listbox.get(selected_index)
            self.cur.execute("DELETE FROM LAGERVERWALTUNG WHERE Name=?", (entry[0],))
            self.con.commit()
            self.update_listbox()

    def show_image(self):
        global my_img
        self.top = Toplevel()
        self.top.title("Übersicht Schränke")
        my_img = ImageTk.PhotoImage(Image.open(r"Pictures/overview.jpg"))
        tk.Label(self.top, image=my_img).pack()

    def update_listbox(self):
        self.multi_listbox.delete(0, tk.END)
        self.cur.execute("SELECT * FROM LAGERVERWALTUNG")
        rows = self.cur.fetchall()
        for row in rows:
            self.multi_listbox.insert(row)


def main():
    root = tk.Tk()
    root.geometry("900x700")
    gui = GUI(root)
    gui.update_listbox()  # Initialisiere die Liste beim Start der Anwendung
    root.mainloop()


if __name__ == "__main__":
    main()
