"""
Volunteer dialogs.

Contains:
- VolunteerSignIn: select existing volunteer (autocomplete)
  or add a new volunteer, then sign in
- VolunteerSignOut: select volunteer currently signed in
  today, compute hours, then collect activity breakdown
- NewVolunteerInformation: register a volunteer
  (VolunteerName)
- VolunteerSelect: editable QComboBox helper used by
  multiple dialogs

DB tables touched:
- VolunteerName
- SISOLOG
"""

import math
from datetime import datetime
import re

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtWidgets import (
    QCheckBox, QComboBox, QCompleter, QDialog,
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from rbh_siso.ui.common import (
    Font, InformationInput, WarningDialog,
)
from rbh_siso.ui.activity_dialogs import SignOutInfo


class VolunteerSignIn(QDialog):
    """Splash screen for Volunteer sign-in."""

    VolSignIn = pyqtSignal(str, str)

    def __init__(self, VolsCurs, VolsDB, parent=None):
        """Initialize the VolunteerSignIn dialog."""
        super().__init__(parent)

        self.ManualEntry = False
        self.VolsCurs = VolsCurs
        self.VolsDB = VolsDB
        self.setWindowTitle("Volunteer Sign In")

        # New volunteer button
        self.NewVolBtn = QPushButton(
            text="New Volunteer",
            parent=self,
        )
        self.NewVolBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.NewVolBtn.setFont(Font)
        self.NewVolBtn.setMaximumHeight(80)
        self.NewVolBtn.clicked.connect(self.New_Volunteer)

        # SignInButton
        self.SignInBtn = QPushButton(
            text="Sign In",
            parent=self,
        )
        self.SignInBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.SignInBtn.setFont(Font)
        self.SignInBtn.setMaximumHeight(80)
        self.SignInBtn.clicked.connect(self.AcceptEntries)

        # BackButton
        self.BackBtn = QPushButton(
            text="Back",
            parent=self,
        )
        self.BackBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.BackBtn.setFont(Font)
        self.BackBtn.setMaximumHeight(80)
        self.BackBtn.clicked.connect(self.Back)

        # ForgotToSignButton
        self.ForgotToSignBtn = QPushButton(
            text="Forgot To Sign In",
            parent=self,
        )
        self.ForgotToSignBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.ForgotToSignBtn.setFont(Font)
        self.ForgotToSignBtn.setMaximumHeight(80)
        self.ForgotToSignBtn.clicked.connect(
            self.ForgotToSign,
        )

        # Initialize the newvolinfo as none
        self.window = None

        # Create a combo box listing volunteers from the
        # database; add autocomplete to speed up process
        res = VolsCurs.execute(
            "SELECT Name FROM VolunteerName",
        )
        NamesTup = res.fetchall()
        self.Names = []
        for Name in NamesTup:
            self.Names.append(Name[0])
        self.CurrentVolunteers = VolunteerSelect(self.Names)
        self.CurrentVolunteersFill = QCompleter(self.Names)
        # Allow autocomplete to ignore case
        self.CurrentVolunteersFill.setCaseSensitivity(
            Qt.CaseSensitivity.CaseInsensitive,
        )
        self.CurrentVolunteers.setCompleter(
            self.CurrentVolunteersFill,
        )
        self.CurrentVolunteers.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.CurrentVolunteers.setFont(Font)
        self.VolunteerSelect = QLabel(
            "Returning volunteers type"
            " and use the dropdown",
            parent=self,
        )
        self.VolunteerSelect.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.VolunteerSelect.setFont(Font)
        self.VolunteerSelect.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        # Layout
        self.layout = QVBoxLayout()
        self.layout.addWidget(
            self.VolunteerSelect, stretch=3,
        )
        self.layout.addWidget(
            self.CurrentVolunteers, stretch=4,
        )

        BotButLayout = QHBoxLayout()
        BotButLayout.addWidget(self.NewVolBtn)
        BotButLayout.addWidget(self.SignInBtn)
        BotButLayout.addWidget(self.ForgotToSignBtn)
        BotButLayout.addWidget(self.BackBtn)
        self.layout.addLayout(BotButLayout, stretch=1)

        self.setLayout(self.layout)

    def New_Volunteer(self):
        """Pop up NewVolunteerInformation and connect its
        signal to NewNameSaved."""
        self.window = NewVolunteerInformation(
            self.VolsCurs, self.VolsDB,
        )
        self.window.NewName.connect(self.NewNameSaved)
        self.window.resize(self.size())
        self.window.exec()

    def NewNameSaved(self, Name):
        """Take info from the NewVolunteerInformation popup
        and push to sign-in (AcceptEntries)."""
        if Name != "":
            if self.CurrentVolunteers.findText(Name) == -1:
                self.CurrentVolunteers.addItem(Name)
                self.Names.append(Name)

            self.CurrentVolunteers.setCurrentText(Name)
            self.AcceptEntries()

    def AcceptEntries(self):
        """Send name and time back to add to database."""
        if self.ManualEntry is True:
            time_str = self.ManualTimeBox.input.text().strip()
            
            # Check if empty
            if time_str == "": 
                self.NoTimeEntered = WarningDialog(
                    "Please enter a time, in the forgot to sign in box, otherwise click back", 5,
                )
                self.NoTimeEntered.resize(self.size())
                self.NoTimeEntered.exec()
                return
                
            # Validate strict military time formats
            match_colon = re.match(r"^([01]\d|2[0-3]):([0-5]\d)$", time_str)
            match_no_colon = re.match(r"^([01]\d|2[0-3])([0-5]\d)$", time_str)
            
            # If not XX:XX and not XXXX, ask gor valid time
            if not match_colon and not match_no_colon:
                self.InvalidTime = WarningDialog(
                    "Please enter a valid military time (e.g., 08:30 or 1430).", 0,
                )
                self.InvalidTime.resize(self.size())
                self.InvalidTime.exec()
                return
                
            # If XXXX, change to XX:XX
            if match_no_colon:
                formatted_time = f"{match_no_colon.group(1)}:{match_no_colon.group(2)}"
                self.ManualTimeBox.input.setText(formatted_time)        
        
        if self.ManualEntry is False:
            self.RightNow = datetime.now().strftime(
                '%Y-%m-%d %H:%M',
            )
        else:
            self.RightNowList = (
                datetime.now().strftime('%Y-%m-%d'),
                self.ManualTimeBox.input.text(),
            )
            self.RightNow = " ".join(self.RightNowList)
        
			
        self.VolunteerName = (
            self.CurrentVolunteers.currentText()
        )
        # Only sign in if name is in volunteer database
        if self.VolunteerName in self.Names:
            self.VolSignIn.emit(
                self.VolunteerName, self.RightNow,
            )
            self.YouSignedInwindow = WarningDialog(
                "Thank you for signing in!", 1.5,
            )
            self.YouSignedInwindow.resize(self.size())
            self.YouSignedInwindow.exec()
            self.accept()
        else:
            self.Warningwindow = WarningDialog(
                "If you are a new volunteer please"
                " click 'New volunteer' otherwise"
                " please select from the dropdown",
                0,
            )
            self.Warningwindow.resize(self.size())
            self.Warningwindow.exec()

    def Back(self):
        """Exit dialog without committing changes."""
        self.VolSignIn.emit("", "")
        self.accept()

    def ForgotToSign(self):
        """Set manual entry to true and add input for
        time."""
        self.ManualEntry = True

        # Time
        self.ManualTimeBox = InformationInput(
            "Time (military XX:XX)", self,
        )
        self.layout.addWidget(self.ManualTimeBox)


class VolunteerSignOut(QDialog):
    """Splash screen for Volunteer sign-out."""

    VolSignOut = pyqtSignal(str, str)

    def __init__(self, VolsCurs, VolsDB, parent=None):
        super().__init__(parent)

        # Pull all names that signed in today and have
        # not yet signed out
        self.VolsCurs = VolsCurs
        self.VolsDB = VolsDB
        self.Date = datetime.now().strftime('%Y-%m-%d')
        res = VolsCurs.execute(
            "SELECT Name FROM SISOLOG"
            " WHERE TimeOut IS NULL",
        )
        NamesTup = res.fetchall()
        self.Names = []
        for Name in NamesTup:
            self.Names.append(Name[0])

        self.window = None

        self.setWindowTitle("Volunteer Sign Out")

        # Sign Out
        self.SignOutBtn = QPushButton(
            text="Sign Out",
            parent=self,
        )
        self.SignOutBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.SignOutBtn.setFont(Font)
        self.SignOutBtn.setMaximumHeight(80)
        self.SignOutBtn.clicked.connect(self.SignOut)

        # BackButton
        self.BackBtn = QPushButton(
            text="Back",
            parent=self,
        )
        self.BackBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.BackBtn.setFont(Font)
        self.BackBtn.setMaximumHeight(80)
        self.BackBtn.clicked.connect(self.Back)

        # Combo box listing volunteers from the database
        self.CurrentVolunteers = VolunteerSelect(self.Names)
        self.CurrentVolunteers.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.CurrentVolunteers.setFont(Font)
        self.VolunteerSelect = QLabel(
            "If you signed in use the dropdown",
            parent=self,
        )
        self.VolunteerSelect.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        self.VolunteerSelect.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.VolunteerSelect.setFont(Font)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(
            self.VolunteerSelect, stretch=3,
        )
        layout.addWidget(
            self.CurrentVolunteers, stretch=4,
        )

        BotButLayout = QHBoxLayout()
        BotButLayout.addWidget(self.SignOutBtn)
        BotButLayout.addWidget(self.BackBtn)
        layout.addLayout(BotButLayout, stretch=1)

        self.setLayout(layout)

    def SignOut(self):
        """Calculate time spent in 1/4 hours and call
        SignOutInfo for gathering more info."""
        self.RightNow = datetime.now().strftime(
            '%Y-%m-%d %H:%M',
        )
        self.Volunteer = (
            self.CurrentVolunteers.currentText()
        )
        self.res = self.VolsCurs.execute(
            "SELECT Timein FROM SISOLOG"
            " WHERE Name = ? AND TimeOut IS NULL",
            [self.Volunteer],
        )
        self.TimeinTup = self.res.fetchall()
        if not self.TimeinTup:
            self.window = WarningDialog(
                "No active sign-in found for"
                " this volunteer.", 0,
            )
            self.window.resize(self.size())
            self.window.exec()
            return
        try:
            self.Timein = datetime.strptime(
                self.TimeinTup[0][0], '%H:%M',
            )
        except Exception:
            self.window = WarningDialog(
                "Stored sign-in time is invalid;"
                " cannot compute hours."
                "Removing previous sign in attempt, please sign in with forgot to sign in", 0,
            )
            self.window.resize(self.size())
            self.window.exec()
            self.VolsCurs.execute(
                "DELETE FROM SISOLOG WHERE Name = ? AND TimeOut IS NULL",
                [self.Volunteer]
            )
            self.VolsDB.commit()
            self.blockSignals(True)
            self.close()
            return
            
            
        self.Timestrip = self.RightNow.split(" ")
        self.Timeout = datetime.strptime(
            self.Timestrip[1], '%H:%M',
        )
        self.TimePassed = self.Timeout - self.Timein
        self.Hours = (
            math.ceil(
                self.TimePassed.total_seconds()
                / (60 * 15)
            ) * 0.25
        )

        self.window = SignOutInfo(
            self.Volunteer, self.Hours,
            self.VolsCurs, self.VolsDB, self.Date,
        )
        self.window.DoneFinished.connect(self.DoneComex)
        self.window.resize(self.size())
        self.window.exec()

    def DoneComex(self, Done):
        """Done signing out - close the window and pass
        data to the parent."""
        if Done == "Done":
            self.VolunteerName = (
                self.CurrentVolunteers.currentText()
            )
            self.VolSignOut.emit(
                self.VolunteerName, self.RightNow,
            )
        self.accept()

    def Back(self):
        """Exit dialog without committing any changes."""
        self.VolSignOut.emit("", "")
        self.accept()


class VolunteerSelect(QComboBox):
    """
    A QComboBox populated with a list of volunteer names.
    
    Features:
    - Editable with autocomplete (typing filters the list)
    - Styled dropdown arrow for better visibility on large screens
    - Visible border to make the interactive area clear
    """

    def __init__(self, nlist, parent=None):
        super().__init__(parent)

        for Name in nlist:
            self.addItem(Name)

        # Makes typing possible
        self.setEditable(True)
        # Don't allow typed text to be inserted
        self.setInsertPolicy(
            self.InsertPolicy.NoInsert,
        )
        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        
        # Limit vertical expansion on maximized windows for better proportions
        self.setMaximumHeight(80)
        
        # Style the dropdown with a clean, minimal look
        # The arrow is enlarged for visibility without visual clutter
        self.setStyleSheet("""
            QComboBox {
                border: 2px solid #999;
                border-radius: 4px;
                padding: 8px;
                padding-right: 50px;
            }
            QComboBox::drop-down {
                width: 40px;
                border: none;
                background: transparent;
            }
            QComboBox::down-arrow {
                width: 16px;
                height: 16px;
                image: url(none);
                border-left: 8px solid transparent;
                border-right: 8px solid transparent;
                border-top: 10px solid #555;
            }
            QComboBox:hover {
                border: 2px solid #2196F3;
            }
        """)
        self.setFont(Font)


class NewVolunteerInformation(QDialog):
    """Where volunteers can register their information."""

    NewName = pyqtSignal(str)

    def __init__(self, VolsCurs, VolsDB, parent=None):
        super().__init__(parent)
        self.VolsCurs = VolsCurs
        self.VolsDB = VolsDB

        self.setWindowTitle(
            "Please Provide your information",
        )

        # NameBox
        self.Name = InformationInput("Name", self)
        # EmailBox
        self.Email = InformationInput(
            "Email (optional)", self,
        )
        # NumberBox
        self.Number = InformationInput(
            "Phone Number (optional)", self,
        )
        # AddressBox
        self.Address = InformationInput(
            "Address (optional)", self,
        )
        # Rockville Resident
        self.RckVillRes = QCheckBox(
            "Rockville Resident?", self,
        )
        self.RckVillRes.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.RckVillRes.setFont(Font)

        self.SaveBtn = QPushButton(
            text="Save and Sign In",
            parent=self,
        )
        self.SaveBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.SaveBtn.setFont(Font)
        self.SaveBtn.setMaximumHeight(80)
        self.SaveBtn.clicked.connect(self.AcceptEntries)

        self.BackBtn = QPushButton(
            text="Back",
            parent=self,
        )
        self.BackBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.BackBtn.setFont(Font)
        self.BackBtn.setMaximumHeight(80)
        self.BackBtn.clicked.connect(self.Back)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.Name, stretch=3)
        self.layout.addWidget(self.RckVillRes, stretch=4)
        self.layout.addWidget(self.Email, stretch=3)
        self.layout.addWidget(self.Number, stretch=3)
        self.layout.addWidget(self.Address, stretch=3)

        self.BtnLayout = QHBoxLayout()
        self.BtnLayout.addWidget(self.SaveBtn)
        self.BtnLayout.addWidget(self.BackBtn)
        self.layout.addLayout(self.BtnLayout, stretch=1)
        self.setLayout(self.layout)

    def AcceptEntries(self):
        """Check that critical info is provided, set empty
        optional fields to 'Not Entered', then write to
        database."""
        if self.Name.input.text() != "":
            if self.Email.input.text() == "":
                self.Email.input.setText("Not Entered")
            if self.Address.input.text() == "":
                self.Address.input.setText("Not Entered")
            if self.Number.input.text() == "":
                self.Number.input.setText("Not Entered")
            # Add name and other info to database
            self.VolsCurs.execute(
                "INSERT INTO VolunteerName"
                " VALUES (?, ?, ?, ?, ?)",
                [
                    self.Name.input.text(),
                    self.Email.input.text(),
                    self.Address.input.text(),
                    self.Number.input.text(),
                    self.RckVillRes.isChecked(),
                ],
            )
            self.VolsDB.commit()
            # Send just the name back to add to dialog box
            self.NewVolunteerName = (
                self.Name.input.text()
            )
            self.NewName.emit(self.NewVolunteerName)
            self.accept()

    def Back(self):
        """Exit without committing changes."""
        self.NewName.emit("")
        self.accept()
