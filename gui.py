from tkinter.filedialog import askdirectory
import tkinter as tk
import tkgen.gengui
from bagit import make_bag
from tkinter import messagebox
from tempfile import NamedTemporaryFile

JSON_SPEC = """{
  "LabelFrame": [
    {
      "text": "BagIt",
      "borderwidth": 2,
      "relief": "groove",
      "column": 0,
      "columnspan": 3,
      "row": 0,
      "colweight": 1,
      "Label": [
        {
          "text": "Source Organization:",
          "column": 0,
          "row": 0
        },
        {
          "text": "Organization Address:",
          "column": 0,
          "row": 1
        },
        {
          "text": "Contact Name:",
          "column": 0,
          "row": 2
        },
        {
          "text": "Contact-Phone:",
          "column": 0,
          "row": 3
        },
        {
          "text": "Contact-Email:",
          "column": 0,
          "row": 4
        },
        {
          "text": "External Description:",
          "column": 0,
          "row": 5
        },
        {
          "text": "External Identifier:",
          "column": 0,
          "row": 6
        },
        {
          "text": "Bag Size",
          "column": 0,
          "row": 7
        },
        {
          "text": "Bag Group Identifier:",
          "column": 0,
          "row": 8
        },
        {
          "text": "Bag Count:",
          "column": 0,
          "row": 9
        },
        {
          "text": "Internal Sender Identifier:",
          "column": 0,
          "row": 10
        },
        {
          "text": "Internal Sender Description:",
          "column": 0,
          "row": 11
        },
        {
          "text": "BagIt Profile Identifier",
          "oolumn": 0,
          "row": 12
        },
        {
          "text": "No directory selected",
          "name": "source_dir_path",
          "column": 1,
          "row": 13
        },
        {
          "text": "No directory selected",
          "name": "destination_dir_path",
          "column": 1,
          "row": 14
        },
        {
          "text": " ",
          "column": 0,
          "row": 15
        }
      ],
      "Entry": [
        {
          "name": "source_organization",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 0,
          "colweight": 1
        },
        {
          "name": "organization_address",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 1,
          "colweight": 1
        },
        {
          "name": "contact_name",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 2,
          "colweight": 1
        },
        {
          "name": "contact_phone",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 3,
          "colweight": 1
        },
        {
          "name": "contact_email",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 4,
          "colweight": 1
        },
        {
          "name": "external_description",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 5,
          "colweight": 1
        },
        {
          "name": "external_identifier",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 6,
          "colweight": 1
        },
        {
          "name": "bag_size",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 7,
          "colweight": 1
        },
        {
          "name": "bag_group_identifier",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 8,
          "colweight": 1
        },
        {
          "name": "bag_count",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 9,
          "colweight": 1
        },
        {
          "name": "internal_sender_identifier",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 10,
          "colweight": 1
        },
        {
          "name": "internal_sender_description",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 11,
          "colweight": 1
        },
        {
          "name": "bagit_profile_identifier",
          "bg": "white",
          "width": 20,
          "column": 1,
          "row": 12,
          "colweight": 1
        }
      ],
      "Button": [
        {
          "name": "source_directory",
          "text": "Source Directory",
          "column": 0,
          "row": 13
        },
        {
          "name": "destination_directory",
          "text": "Destination Directory",
          "column": 0,
          "row": 14
        },
        {
          "name": "bagit",
          "text": "BagIt",
          "column": 0,
          "row": 16
        },
        {
          "name": "exit",
          "text": "Exit",
          "column": 1,
          "row": 16
        }
      ]
    }
  ]
}
"""

class BagItGUI(tk.Frame):
    root = None
    source_organization = None
    organization_address = None
    contact_name = None
    contact_phone = None
    contact_email = None
    external_description = None
    external_identifier = None
    bag_group_identifier = None
    bag_count = None
    internal_sender_identifier = None
    internal_sender_description = None
    source_dir = None
    destination_dir = None

    def __init__(self):
        tmp_file = NamedTemporaryFile(delete=False)
        with open(tmp_file.name, 'w') as f:
            f.write(JSON_SPEC)
        self.root = tkgen.gengui.TkJson(tmp_file.name, title='BagIt')

        self.source_organization = self.root.entry('source_organization')
        self.organization_address = self.root.entry('organization_address')
        self.contact_name = self.root.entry('contact_name')
        self.contact_phone = self.root.entry('contact_phone')
        self.contact_email = self.root.entry('contact_email')
        self.external_description = self.root.entry('external_description')
        self.external_identifier = self.root.entry('external_identifier')
        self.bag_size = self.root.entry('bag_size')
        self.bag_group_identifier = self.root.entry('bag_group_identifier')
        self.bag_count = self.root.entry('bag_count')
        self.internal_sender_identifier = self.root.entry('internal_sender_identifier')
        self.internal_sender_description = self.root.entry('internal_sender_description')
        self.bagit_profile_identifier = self.root.entry('bagit_profile_identifier')

        self.root.button('source_directory', cmd=self.source_directory)
        self.root.button('destination_directory', cmd=self.destination_directory)
        self.root.button('bagit', cmd=self.bagit)
        self.root.button('exit', self.root.destroy)

        self.root.mainloop()

    def source_directory(self, event=None):
        self.source_dir = askdirectory(title='Choose the directory to bag...')
        self.root.label('source_dir_path').set(self.source_dir)

    def destination_directory(self, event=None):
        self.destination_dir = askdirectory(title='Choose a destination directory...')
        self.root.label('destination_dir_path').set(self.source_dir)

    def bagit(self, event=None):
        bag_info = {
            'Source-Organization': self.source_organization.get(),
            'Organization-Address': self.organization_address.get(),
            'Contact-Name': self.contact_name.get(),
            'Contact-Phone': self.contact_phone.get(),
            'Contact-Email': self.contact_email.get(),
            'External-Description': self.external_description.get(),
            'External-Identifier': self.external_identifier.get(),
            'Bag-Size': self.bag_size.get(),
            'Bag-Group-Identifier': self.bag_group_identifier.get(),
            'Bag-Count': self.bag_count.get(),
            'Internal-Sender-Identifier': self.internal_sender_description.get(),
            'Internal-Sender-Description': self.internal_sender_description.get(),
            'BagIt-Profile-Identifier': self.bagit_profile_identifier.get()
        }
        print(self.source_dir)
        print(self.destination_dir)
        success = make_bag(self.source_dir, self.destination_dir, bag_info=bag_info)
        if success:
            messagebox.showinfo("Done creating bag!")
            self.root.destroy()