"""
Activity dialogs.

Contains:
- SignOutInfo: volunteer sign-out "activity breakdown"
  screen
- ActivitySelect: activity chooser row with hours /
  bike-count inputs

DB tables touched:
- Activity-specific tables (current approach; planned to
  be normalized later)
"""

from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget,
)

from rbh_siso.ui.common import Font, WarningDialog


class SignOutInfo(QDialog):
    """Where activities are selected and information is
    saved to respective activity databases."""

    DoneFinished = pyqtSignal(str)

    def __init__(
        self, Name, hours, SOICurs, SOIdb, date,
        parent=None,
    ):
        self.Hour = hours
        self.SOICurs = SOICurs
        self.SOIDB = SOIdb
        self.date = date
        self.Name = Name
        super().__init__(parent)

        self.setWindowTitle(
            "Please select the activities worked on",
        )

		#1 designates accepting bike count while 0 means N/A
        MasterActivities = [
            ("TERRIFIC_Kids_Bike_Repair", 1),
            ("TERRIFIC_Kids_Admin", 0),
            ("MoCo_Bike_Repair", 1),
            ("MoCo_Admin", 0),
            ("Sale_Bike_Repair", 1),
            ("Shop_admin", 0),
            ("New_Volunteer_Orientation", 0),
            ("Client_Assistance", 0),
            ("Sale_Bike_Admin", 0),
            ("Workshop_Instruction", 0),
            ("Workshop_Admin", 0),
            ("Worked_on_my_bike", 0),
        ]

        # Automatically generate both required structures from the master list
        ActivityList = [item[0] for item in MasterActivities]
        bike_activities = {item[0] for item in MasterActivities if item[1] == 1}


        self.layout = QVBoxLayout()

        # Hours summary label at the top - shows total time volunteered
        # This is prominently styled to prevent users from missing it and entering incorrect hours
        self.NameAndHours = QLabel(
            "Hi " + self.Name
            + " you volunteered "
            + str(hours) + " Hours",
        )
        self.NameAndHours.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        
        # Create a larger, bold font for the hours label
        hours_font = QFont(Font)
        hours_font.setPointSize(28)  # Larger than the standard 20pt
        hours_font.setBold(True)
        self.NameAndHours.setFont(hours_font)
        
        # Add prominent styling with colored background and border
        self.NameAndHours.setStyleSheet("""
            QLabel {
                background-color: #E3F2FD;
                color: #1976D2;
                padding: 20px;
                border: 3px solid #2196F3;
                border-radius: 8px;
                font-weight: bold;
            }
        """)
        
        self.NameAndHours.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        self.layout.addWidget(
            self.NameAndHours, stretch=2,
        )

        # Create all 5 activity row widgets (shown/hidden as needed)
        self.activityNum = 1
        self.activity1 = ActivitySelect(ActivityList, bike_activities)
        self.activity2 = ActivitySelect(ActivityList, bike_activities)
        self.activity3 = ActivitySelect(ActivityList, bike_activities)
        self.activity4 = ActivitySelect(ActivityList, bike_activities)
        self.activity5 = ActivitySelect(ActivityList, bike_activities)
        self.NoMoreActivities = QLabel(
            "The max number of activities is reached",
        )
        self.NoMoreActivities.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.NoMoreActivities.setFont(Font)
        self.NoMoreActivities.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        
        # Add first activity row (always visible)
        self.layout.addWidget(
            self.activity1, stretch=4,
        )

        # Add Activity button - appears below activity rows
        # Users click this to reveal additional activity rows
        self.AddActBtn = QPushButton(
            text="Add Activity",
            parent=self,
        )
        self.AddActBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.AddActBtn.setFont(Font)
        self.AddActBtn.setMaximumHeight(80)
        self.AddActBtn.clicked.connect(self.AddAct)
        self.layout.addWidget(self.AddActBtn, stretch=1)

        # Done and Back buttons at the bottom
        # Follows top-to-bottom data entry flow (matches Client Sign Out pattern)
        self.DoneBtn = QPushButton(
            text="Done",
            parent=self,
        )
        self.DoneBtn.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.DoneBtn.setFont(Font)
        self.DoneBtn.setMaximumHeight(80)
        self.DoneBtn.clicked.connect(self.Done)

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

        self.BottomButLayout = QHBoxLayout()
        self.BottomButLayout.addWidget(self.DoneBtn)
        self.BottomButLayout.addWidget(self.BackBtn)
        self.layout.addLayout(
            self.BottomButLayout, stretch=1,
        )

        self.setLayout(self.layout)

    def AddAct(self):
        """
        Add an activity option to the display.
        
        Inserts a new activity row before the "Add Activity" button,
        maintaining the top-to-bottom data entry flow.
        """
        self.activityNum += 1
        
        # Calculate insertion position: always insert before the button section
        # Layout structure: [label, activities..., AddActBtn, BottomButLayout]
        # Insert at count()-2 to place new activity before AddActBtn
        insert_position = self.layout.count() - 2
        
        if self.activityNum == 2:
            self.layout.insertWidget(
                insert_position, self.activity2, stretch=4,
            )
        elif self.activityNum == 3:
            self.layout.insertWidget(
                insert_position, self.activity3, stretch=4,
            )
        elif self.activityNum == 4:
            self.layout.insertWidget(
                insert_position, self.activity4, stretch=4,
            )
        elif self.activityNum == 5:
            self.layout.insertWidget(
                insert_position, self.activity5, stretch=4,
            )
        elif self.activityNum == 6:
            self.layout.insertWidget(
                insert_position, self.NoMoreActivities, stretch=4,
            )

    def Done(self):
        """Check if hours add up, then emit done or warn
        that hours don't match."""
        self.hoursEntered = 0
        self.HoursEnteredList = [
            self.activity1.hoursinput.text(),
            self.activity2.hoursinput.text(),
            self.activity3.hoursinput.text(),
            self.activity4.hoursinput.text(),
            self.activity5.hoursinput.text(),
        ]
        for text in self.HoursEnteredList:
            try:
                self.hoursEntered += float(text)
            except (ValueError, TypeError):
                pass

        if abs(self.hoursEntered - self.Hour) < 1e-9:
            # Write each activity into its respective DB
            # (only after validation passes)
            activities = [
                self.activity1,
                self.activity2,
                self.activity3,
                self.activity4,
                self.activity5,
            ]
            if self.activityNum < 5:
                ActivitiesEntered = self.activityNum
            else:
                ActivitiesEntered = 5
				
            for i in range(ActivitiesEntered):
                act = activities[i]
                self.ActivityDatabaseWrite(
                    self.Name,
                    self.date,
                    act.ActivitySelect.currentText(),
                    act.hoursinput.text(),
                    act.bikesinput.text(),
                )

            self.DoneFinished.emit("Done")
            self.accept()
        else:
            self.window = WarningDialog(
                "The number of hours entered does"
                " not match the number of hours"
                " volunteered",
                0,
            )
            self.window.resize(self.size())
            self.window.exec()

    def Back(self):
        """Exit dialog without committing changes."""
        self.DoneFinished.emit("")
        self.accept()

    def ActivityDatabaseWrite(
        self, Name, Date, ActivityName,
        ActivityHours, ActivityBikecount,
    ):
        """Write info into database for each activity."""
        self.SOICurs.execute(
            f"CREATE TABLE IF NOT EXISTS"
            f" {ActivityName}"
            f" (Name, Date, Hours, BikeCount)",
        )
        self.SOICurs.execute(
            f"INSERT INTO {ActivityName}"
            f" VALUES (?, ?, ?, ?)",
            [Name, Date, ActivityHours, ActivityBikecount],
        )


class ActivitySelect(QWidget):
    """Takes in a list of activities and creates a space
    for entering information about each activity like
    hours worked, etc."""

    def __init__(self, Activitylist, bike_activities, parent=None):
        super().__init__(parent)
		
        self.bike_activities = bike_activities
        self.ActivitySelect = QComboBox()
        for Activity in Activitylist:
            self.ActivitySelect.addItem(Activity)
        self.ActivitySelect.currentTextChanged.connect(
            self.ActivityChange,
        )
        self.ActivitySelect.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.ActivitySelect.setFont(Font)
        self.ActivitySelect.setMaximumHeight(80)

        self.hoursprompt = QLabel(
            'Hours worked', parent,
        )
        self.hoursprompt.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.hoursprompt.setFont(Font)
        self.hoursprompt.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        self.hoursinput = QLineEdit(parent)
        self.hoursinput.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.hoursinput.setFont(Font)
        self.hoursinput.setMaximumHeight(60)

        self.hourslayout = QVBoxLayout()
        self.hourslayout.addWidget(
            self.hoursprompt, stretch=1,
        )
        self.hourslayout.addWidget(
            self.hoursinput, stretch=3,
        )

        self.bikesprompt = QLabel(
            'Bikes completed', parent,
        )
        self.bikesprompt.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.bikesprompt.setFont(Font)
        self.bikesprompt.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )
        self.bikesinput = QLineEdit(parent)
        self.bikesinput.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self.bikesinput.setFont(Font)
        self.bikesinput.setMaximumHeight(60)

        self.bikeslayout = QVBoxLayout()
        self.bikeslayout.addWidget(
            self.bikesprompt, stretch=1,
        )
        self.bikeslayout.addWidget(
            self.bikesinput, stretch=3,
        )

        self.layout = QHBoxLayout()
        self.layout.addWidget(
            self.ActivitySelect, stretch=2,
        )
        self.layout.addLayout(
            self.hourslayout, stretch=2,
        )
        self.layout.addLayout(
            self.bikeslayout, stretch=2,
        )

        self.setLayout(self.layout)

    def ActivityChange(self):
        """Enable/disable bike count input based on
        selected activity."""

        current = self.ActivitySelect.currentText()
        if current in self.bike_activities:
            self.bikesinput.setReadOnly(False)
            self.bikesinput.setText('')
        else:
            self.bikesinput.setReadOnly(True)
            self.bikesinput.clear()
            self.bikesinput.setText('N/A')
