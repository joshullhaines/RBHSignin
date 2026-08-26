"""
Main menu dialog.

Contains:
- RBHSISO: the first screen shown, with buttons to open
  volunteer/client dialogs.

DB tables touched (via callbacks):
- VolunteerName
- ClientName
- SISOLOG
- ClientSISOLOG
"""

from PyQt6.QtWidgets import (
    QHBoxLayout, QMainWindow, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget,
)

from rbh_siso.db import connect, ensure_schema
from rbh_siso.ui.common import Font, WarningDialog
from rbh_siso.ui.client_dialogs import ClientSignOut
from rbh_siso.ui.volunteer_dialogs import (
    VolunteerSignIn, VolunteerSignOut,
)


class RBHSISO(QMainWindow):
    """
    Main application window for the RBH Sign-In/Sign-Out
    system.

    This is the primary window that displays when the app
    starts. It provides buttons for volunteer sign-in,
    volunteer sign-out, and client sign-out operations.

    Note: This inherits from QMainWindow (not QDialog) to
    prevent the window from closing unexpectedly when child
    dialogs emit accept() signals.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(
            "Welcome to RBH! Please sign in and out"
        )
        self.NewVolWindow = None

        # Open database and ensure schema exists
        self.db = connect("Information.db")
        self.Curs = self.db.cursor()
        ensure_schema(self.Curs)
        
        self.Curs.execute(
            """
            DELETE FROM SISOLOG 
            WHERE (TimeOut IS NULL OR TimeOut = '') 
            AND Date != date('now', 'localtime')
            """
        )
        self.db.commit()

        # Create central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Volunteer Sign in button
        self.VolSignIn = QPushButton(
            text="Volunteer Sign in",
            parent=central_widget,
        )
        self.VolSignIn.setFont(Font)
        self.VolSignIn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.VolSignIn.setMaximumHeight(100)
        self.VolSignIn.clicked.connect(
            self.VolunteerSignIn,
        )

        # Volunteer Sign out button
        self.VolSignOut = QPushButton(
            text="Volunteer Sign Out",
            parent=central_widget,
        )
        self.VolSignOut.setFont(Font)
        self.VolSignOut.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.VolSignOut.setMaximumHeight(100)
        self.VolSignOut.clicked.connect(
            self.VolunteerSignOut,
        )

        # Volunteer buttons row
        self.VolunteerLayout = QHBoxLayout()
        self.VolunteerLayout.addWidget(self.VolSignIn)
        self.VolunteerLayout.addWidget(self.VolSignOut)

        # Client Sign out button
        self.CliSignOut = QPushButton(
            text="Client Sign Out",
            parent=central_widget,
        )
        self.CliSignOut.setFont(Font)
        self.CliSignOut.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.CliSignOut.setMaximumHeight(100)
        self.CliSignOut.clicked.connect(self.ClientSignOut)

        # Client buttons row
        self.ClientLayout = QHBoxLayout()
        self.ClientLayout.addWidget(self.CliSignOut)

        # Main layout - set on central widget, not window
        Layout = QVBoxLayout()
        Layout.addLayout(self.VolunteerLayout)
        Layout.addLayout(self.ClientLayout)
        central_widget.setLayout(Layout)

    def VolunteerSignIn(self):
        """Open a VolunteerSignIn dialog and connect its
        signal back to the parent slot."""
        self.NewSignInWindow = VolunteerSignIn(
            self.Curs, self.db,
        )
        self.NewSignInWindow.VolSignIn.connect(
            self.VolSignInComex,
        )
        self.NewSignInWindow.resize(self.size())
        self.NewSignInWindow.exec()

    def VolSignInComex(self, Name, Time):
        """Take name and time from the sign-in popup and
        enter it into the database."""
        if Name != "":
            TimeSplit = Time.split(" ")
            Date = TimeSplit[0]
            TimeOfDay = TimeSplit[1]
            SignedIn = self.CheckSignedIn(
                Name, Date, self.Curs, self.db,
            )
            if SignedIn is False:
                self.Curs.execute(
                    "INSERT INTO SISOLOG"
                    " (Name, Date, Timein)"
                    " VALUES (?, ?, ?)",
                    [Name, Date, TimeOfDay],
                )
                self.db.commit()
            else:
                self.Warningwindow = WarningDialog(
                    "You are already signed in!", 0,
                )
                self.Warningwindow.resize(self.size())
                self.Warningwindow.exec()

    def VolunteerSignOut(self):
        """Open a VolunteerSignOut dialog and connect its
        signal back to the parent slot."""
        self.NewSignOutWindow = VolunteerSignOut(
            self.Curs, self.db,
        )
        self.NewSignOutWindow.VolSignOut.connect(
            self.VolSignOutComex,
        )
        self.NewSignOutWindow.resize(self.size())
        self.NewSignOutWindow.exec()

    def VolSignOutComex(self, Name, Time):
        """Take name and date from the VolunteerSignOut
        popup and update the most recent matching sign-in
        in the database."""
        if Name != "":
            TimeSplit = Time.split(" ")
            Date = TimeSplit[0]
            TimeOfDay = TimeSplit[1]
            res = self.Curs.execute(
                "SELECT rowid FROM SISOLOG"
                " WHERE Name = ? AND Date = ?"
                " AND Timeout IS NULL"
                " ORDER BY rowid DESC LIMIT 1",
                [Name, Date],
            )
            row = res.fetchone()
            if row is None:
                self.Warningwindow = WarningDialog(
                    "No matching sign-in found"
                    " to sign out.", 0,
                )
                self.Warningwindow.resize(self.size())
                self.Warningwindow.exec()
                return

            self.Curs.execute(
                "UPDATE SISOLOG SET TimeOut = ?"
                " WHERE rowid = ?",
                [TimeOfDay, row[0]],
            )
            self.db.commit()

    def ClientSignOut(self):
        """Open a ClientSignOut popup and connect its signal
        back to the parent slot."""
        self.newClientSignOutWindow = ClientSignOut(
            self.Curs, self.db,
        )
        self.newClientSignOutWindow.showMaximized()
        self.newClientSignOutWindow.ClientSignOut.connect(
            self.ClientSignOutComex,
        )
        self.newClientSignOutWindow.resize(self.size())
        self.newClientSignOutWindow.exec()

    def ClientSignOutComex(
        self, Name, Date, HoursCount, Activity,
    ):
        """Add client sign-out information into the
        database."""
        if Name != "":
            self.Curs.execute(
                "INSERT INTO ClientSISOLOG"
                " (Name, Date, HoursCount, Activity)"
                " VALUES (?, ?, ?, ?)",
                [Name, Date, HoursCount, Activity],
            )
            self.db.commit()

    def CheckSignedIn(self, Name, Date, SisoCurs, SisoDB):
        """Check if a volunteer is already currently
        signed in."""
        res = SisoCurs.execute(
            "SELECT COUNT(*) FROM SISOLOG"
            " WHERE Name = ? AND Timeout IS NULL",
            [Name],
        )
        NumberSignIns = res.fetchall()
        if NumberSignIns[0][0] > 0:
            return True
        else:
            return False
