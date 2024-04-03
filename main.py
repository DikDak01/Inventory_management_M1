import sqlite3
import tkinter as tk
from tkinter import simpledialog, Toplevel
from PIL import Image, ImageTk


class Management:

    def __init__(self):
        self.con = sqlite3.connect("management.db")
        self.cur = self.con.cursor()

    def create_table(self):
        self.cur.execute(
            """CREATE TABLE IF NOT EXISTS MANAGEMENT (
                Date DATE,
                Description TEXT,
                Type TEXT,
                quantity INT,
                Room TEXT,
                Cupboard TEXT,
                CONSTRAINT Date_unique UNIQUE (Date),
                CONSTRAINT Description_unique UNIQUE (Description),
                CONSTRAINT Type_unique UNIQUE (Type),
                CONSTRAINT quantity_unique UNIQUE (quantity),
                CONSTRAINT Room_unique UNIQUE (Room),
                CONSTRAINT Cupboard_unique UNIQUE (Cupboard)
            );"""
        )
        self.con.commit()

# TODO: self.cur.execute("SELECT DATE FROM MANAGEMENT WHERE Date=?", [Date, Description, Type, quantity, Room, Cupboard])
# TODO: sqlite3.ProgrammingError: Incorrect number of bindings supplied. The current statement uses 1, and there are 6 supplied.
    def insert_data(self, Date, Description, Type, quantity, Room, Cupboard):
        # Check whether the article already exists
        self.cur.execute("SELECT DATE FROM MANAGEMENT WHERE Date=?", [Date, Description, Type, quantity, Room, Cupboard])
        existing_row = self.cur.fetchone()

        if existing_row:
            print(f"The item '{Type}' already exists in stock.")
        else:
            self.cur.execute(
                """INSERT INTO MANAGEMENT (Date, Description, Type, quantity, Room, Cupboard)
                VALUES (?, ?, ?, ?, ?, ?)""", (Date, Description, Type, quantity, Room, Cupboard)
            )
            self.con.commit()
            print(f"The article '{Description}' was successfully added.")

    def insert_multiple_data(self, data):

        for item in data:
            self.name = item[0]
            self.insert_data(*item)

    def retrieve_data(self):
        self.cur.execute("SELECT * FROM MANAGEMENT")
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

class GUI(Management):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.master.title("Management")

        self.multi_listbox = MultiListbox(master, ["Date", "Description", "Type", "quantity", "Room", "Cupboard"])
        self.multi_listbox.pack(padx=30, pady=30, fill=tk.BOTH, expand=True)

        add_button = tk.Button(master, text="add", command=self.add_entry)
        add_button.pack(padx=10, pady=5, fill=tk.X)

        edit_button = tk.Button(master, text="edit", command=self.edit_entry)
        edit_button.pack(padx=10, pady=5, fill=tk.X)

        delete_button = tk.Button(master, text="delete", command=self.delete_entry)
        delete_button.pack(padx=10, pady=5, fill=tk.X)

        show_image_button = tk.Button(master, text="show picture", command=self.show_image)
        show_image_button.pack(padx=10, pady=5, fill=tk.X)

        close_button = tk.Button(master, text="close", command=master.quit)
        close_button.pack(padx=10, pady=5, fill=tk.X)

    def add_entry(self):
        add_name = {
            "Date": simpledialog.askstring("add an entry", "Date:"),
            "Description": simpledialog.askstring("add an entry", "Description:"),
            "Type": simpledialog.askstring("add an entry", "Type:"),
            "quantity": simpledialog.askstring("add an entry", "quantity:"),
            "Room": simpledialog.askstring("add an entry", "Room:"),
            "Cupboard": simpledialog.askstring("add an entry", "Cupboard:")
        }
        if add_name:
            self.insert_data(add_name["Date"], add_name["Description"], add_name["Type"], add_name["quantity"],
                             add_name["Room"], add_name["Cupboard"])
            self.update_listbox()

    def edit_entry(self):
        selected_index = self.multi_listbox.curselection()
        if selected_index:
            entry = self.multi_listbox.get(selected_index)
            old_name = entry[0]
            new_name = {
                "Date": simpledialog.askstring("to edit an entry", "add date:", initialvalue=old_name),
                "Description": simpledialog.askstring("to edit an entry", "Description:"),
                "Type": simpledialog.askstring("to edit an entry", "Type:"),
                "quantity": simpledialog.askstring("to edit an entry", "quantity:"),
                "Room": simpledialog.askstring("to edit an entry", "Room:"),
                "Cupboard": simpledialog.askstring("to edit an entry", "Cupboard:")
            }
            if new_name:
                self.cur.execute(
                    "UPDATE MANAGEMENT SET Date=?, Description=?, Type=?, quantity=?, Room=?, Cupboard=? WHERE Name=?",
                    (
                    new_name["Date"], new_name["Description"], new_name["Type"], new_name["quantity"], new_name["Room"],
                    new_name["Cupboard"], old_name))
                self.con.commit()
                self.update_listbox()

    def delete_entry(self):
        selected_index = self.multi_listbox.curselection()
        if selected_index:
            entry = self.multi_listbox.get(selected_index)
            self.cur.execute("DELETE FROM MANAGEMENT WHERE Name=?", (entry[0],))
            self.con.commit()
            self.update_listbox()

    def show_image(self):
        global my_img
        self.top = Toplevel()
        self.top.title("Overview Cupboard")
        my_img = ImageTk.PhotoImage(Image.open(r"Pictures/overview.jpg"))
        tk.Label(self.top, image=my_img).pack()

    def update_listbox(self):
        self.multi_listbox.delete(0, tk.END)
        self.cur.execute("SELECT * FROM MANAGEMENT")
        rows = self.cur.fetchall()
        for row in rows:
            self.multi_listbox.insert(row)


def main():
    root = tk.Tk()
    root.geometry("900x700")
    gui = GUI(root)
    gui.update_listbox()
    root.mainloop()


if __name__ == "__main__":
    main()
