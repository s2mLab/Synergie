import ttkbootstrap as ttkb
from core.database.DatabaseManager import DatabaseManager

class ConnectionPage:
    def __init__(self, root : ttkb.Window, dbManager : DatabaseManager) -> None:
        self.root = root
        self.dbManager = dbManager
        self.userConnected = ""
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.frame = ttkb.Frame(self.root)
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_rowconfigure(1, weight=1)
        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.label = ttkb.Label(self.frame, text="Please enter your email")
        self.label.grid(row=0, column=0, sticky="s")
        self.accountVar = ttkb.StringVar(self.frame, value="")
        self.entry = ttkb.Entry(self.frame, textvariable=self.accountVar)
        self.entry.grid(row=1, column=0)
        self.button = ttkb.Button(self.frame, text="Register", command=self.register)
        self.button.grid(row=2, column=0, sticky="n")
        self.errorVar = ttkb.StringVar(self.frame, value="")
        self.errorLabel = ttkb.Label(self.frame, textvariable=self.errorVar)
        self.errorLabel.grid(row=3, column=0)
        self.frame.grid(sticky="nswe")
    
    def register(self):
        userFound = self.dbManager.findUserByEmail(self.accountVar.get())
        if userFound != []:
            x = userFound[0]
            if x.get("role") == "COACH":
                print("Connected")
                self.userConnected = x.id
            else:
                self.errorVar.set("Error : you need a coach account")
        else:
            self.errorVar.set("Error : this user doesn't exist")
