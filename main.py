"""

"""
import tkinter as tk
from tkinter.filedialog import askdirectory
import wmi
import os

c = wmi.WMI()
DRIVE_TYPES = {
    0: "Unknown",
    1: "No Root Directory",
    2: "Removable Disk",
    3: "Local Disk",
    4: "Network Drive",
    5: "Compact Disc",
    6: "RAM Disk"
}


class BagItGUI(tk.Frame):
    bagit_form_fields = [
        'Source Organization',
        'Organization Address',
        'Contact Name',
        'Contact-Phone',
        'Contact-Email',
        'External Description',
        'Bagging Date',
        'External Identifier',
        'Payload Oxum',
        'Bag Group Identifier',
        'Bag Count',
        'Internal Sender Identifier',
        'Internal Sender Description',
        'Directory'
    ]

    dir_name = ''

    def __init__(self, master=None):
        super().__init__(master)
        self.pack()
        self._create_widgets()

    def _create_widgets(self):
        entries = self._make_bagit_form(self.bagit_form_fields)
        self.bind('<Return>', (lambda event, e=entries: self._fetch_bagit_entries(e)))

        button_one = tk.Button(self, text='Show', command=(lambda e=entries: self._fetch_bagit_entries(e)))
        button_one.pack(side=tk.LEFT, padx=5, pady=5)

        button_three = tk.Button(self, text='Quit', command=self.quit)
        button_three.pack(side=tk.RIGHT, padx=5, pady=5)

    def _fetch_bagit_entries(self, entries):
        for entry in entries:
            field = entry[0]
            if field == 'Directory':
                text = self.dir_name
            else:
                text = entry[1].get()
            print("{}: {}".format(field, text))

    def _make_bagit_form(self, fields):
        entries = []
        for field in fields:
            row = tk.Frame(self)
            if field == 'Directory':
                entry = tk.Button(self, text="Browse...", command=self.ask_open_directory)
            else:
                label = tk.Label(row, width=15, text=field, anchor='w')
                entry = tk.Entry(row)
                label.pack(side=tk.LEFT)
            row.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
            label.pack(side=tk.LEFT)
            entry.pack(side=tk.RIGHT, expand=tk.YES, fill=tk.X)
            entries.append((field, entry))
        return entries

    def ask_open_directory(self):
        self.dir_name = askdirectory(title='Choose the directory to bag...')


def main():
    root = tk.Tk()
    app = BagItGUI(master=root)
    app.mainloop()


if __name__ == '__main__':
    main()
