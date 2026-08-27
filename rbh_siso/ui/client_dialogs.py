"""
Client dialogs.

Contains:
- ClientSignOut: collects client sign-out info and
  optionally joins the mailing list.

DB tables touched:
- ClientName
- ClientSISOLOG
"""

from datetime import datetime

from PyQt6.QtCore import pyqtSignal, Qt, QStringListModel
from PyQt6.QtWidgets import (
    QCheckBox, QCompleter, QDialog, QHBoxLayout,
    QPushButton, QSizePolicy, QVBoxLayout,
)

from rbh_siso.ui.common import Font, InformationInput, CheckboxInput
from rbh_siso.ui.volunteer_dialogs import VolunteerSelect


class ClientSignOut(QDialog):
    """Splash screen for the client sign-out."""

    ClientSignOut = pyqtSignal(str, str, str, str)

    def __init__(self, ClientCurs, ClientDB, parent=None):
        super().__init__(parent)

        self.mailingListEntry = False

        self.ClientCurs = ClientCurs
        self.ClientDB = ClientDB

        # Pull all previously entered client names
        res = self.ClientCurs.execute(
            "SELECT Name FROM ClientName",
        )
        NamesTup = res.fetchall()
        self.NamesList = []
        for Name in NamesTup:
            self.NamesList.append(Name[0])

        # Create Name Entry with autocomplete
        self.NamesListFill = QStringListModel()
        self.NamesListFill.setStringList(self.NamesList)
        self.AutofillNames = QCompleter(
            self.NamesListFill,
        )
        # Allow autocomplete to ignore case
        self.AutofillNames.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive,
        )
        self.Names = InformationInput(
            "Name (write over or stay anonymous)", self,
        )
        self.Names.input.setCompleter(self.AutofillNames)
        self.Names.input.setText("RBH Client")

        self.setWindowTitle("Client Sign Out")

        # Join our mailing list button
        self.NewCliBtn = QPushButton(
            text="Join our mailing list?",
            parent=self,
        )
        self.NewCliBtn.setFont(Font)
        self.NewCliBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.NewCliBtn.setMaximumHeight(80)
        self.NewCliBtn.clicked.connect(self.mailingList)

        # SignOutButton
        self.SignOutBtn = QPushButton(
            text="Sign Out",
            parent=self,
        )
        self.SignOutBtn.setFont(Font)
        self.SignOutBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.SignOutBtn.setMaximumHeight(80)
        self.SignOutBtn.clicked.connect(self.SignOut)

        # BackButton
        self.BackBtn = QPushButton(
            text="Back",
            parent=self,
        )
        self.BackBtn.setFont(Font)
        self.BackBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.BackBtn.setMaximumHeight(80)
        self.BackBtn.clicked.connect(self.Back)

        # Time spent entry
        self.Hours = InformationInput(
            "Time Spent (in hours)", self,
        )

        # Rockville Resident
        self.RckVillRes= CheckboxInput("Rockville Resident?", self)

        # Activity selection
        self.ClientActivityList = [
            "Client_Activity",
            "Independent_Bike_Repair/Maintenance",
            "Assisted_Bike_Repair/Maintenance",
            "Attending_Workshop",
            "Donating_Parts",
            "Donating_Accessories",
            "Donating_Bike(s)",
        ]
        self.ClientActivities = VolunteerSelect(
            self.ClientActivityList,
        )

        # Email entry
        self.Email = InformationInput(
            "Email(Optional)", self,
        )

        # PhoneNumber entry
        self.PhoneNumber = InformationInput(
            "Phone Number(Optional)", self,
        )

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.Names, stretch=2)
        self.layout.addWidget(self.RckVillRes, stretch=3)
        self.layout.addWidget(
            self.ClientActivities, stretch=3,
        )
        self.layout.addWidget(self.Hours, stretch=2)
        self.layout.addWidget(self.NewCliBtn, stretch=1)

        self.Buttonslayout = QHBoxLayout()
        self.Buttonslayout.addWidget(self.SignOutBtn)
        self.Buttonslayout.addWidget(self.BackBtn)

        self.layout.addLayout(
            self.Buttonslayout, stretch=1,
        )
        self.setLayout(self.layout)

    def mailingList(self):
        """Add email and phone entry widgets and change
        behaviour."""
        if self.mailingListEntry:
            return
        self.layout.addWidget(self.Email)
        self.layout.addWidget(self.PhoneNumber)

        self.mailingListEntry = True
        self.NewCliBtn.setEnabled(False)
        self.NewCliBtn.setText("Mailing list enabled")

    def Back(self):
        """Exit dialog without committing any database
        changes."""
        self.ClientSignOut.emit("", "", "", "")
        self.accept()

    def SignOut(self):
        """Check if name is in client name database
        already; add if not. Update mailing list info
        if enabled. Then emit sign-out data."""
        # If name not already in DB, add it
        if self.Names.input.text() not in self.NamesList:
            self.ClientCurs.execute(
                "INSERT INTO ClientName"
                " (Name, RockVilleRes) VALUES (?, ?)",
                [
                    self.Names.input.text(),
                    self.RckVillRes.isChecked(),
                ],
            )
            self.ClientDB.commit()

        # If mailing list enabled, update contact info
        if self.mailingListEntry:
            self.ClientCurs.execute(
                "UPDATE ClientName"
                " SET Email = ?, PhoneNumber = ?,"
                " RockvilleRes = ? WHERE Name = ?",
                [
                    self.Email.input.text(),
                    self.PhoneNumber.input.text(),
                    self.RckVillRes.isChecked(),
                    self.Names.input.text(),
                ],
            )
            self.ClientDB.commit()

        # Log this sign-out by emitting to parent
        self.date = datetime.now().strftime('%Y-%m-%d')

        self.ClientSignOut.emit(
            self.Names.input.text(),
            self.date,
            self.Hours.input.text(),
            self.ClientActivities.currentText(),
        )
        self.accept()
