"""
Activity dialogs.

Contains:
- SignOutInfo: volunteer sign-out "activity breakdown" screen
- ActivitySelect: activity chooser row with hours/bike-count inputs

DB tables touched:
- Activity-specific tables (current approach; planned to be normalized later)
"""

from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QVBoxLayout,QHBoxLayout, QWidget,QDialog, QLineEdit,QLabel, QSizePolicy

from rbh_siso.ui.common import Font, WarningDialog


class SignOutInfo(QDialog):#This is where activities are selected and information is saved to respective activity databases
	DoneFinished = pyqtSignal(str)
	
	def __init__(self, Name, hours,SOICurs,SOIdb, date, parent=None):
		self.Hour =hours
		self.SOICurs = SOICurs
		self.SOIDB = SOIdb
		self.date = date
		self.Name = Name
		super().__init__( parent)
		
		self.setWindowTitle("Please select the activities worked on")
		
		ActivityList =["MoCo_bikes", "Terrific_kids_bikes", "Bikes_for_sale", "Client_Help", "Worked_on_my_bike"]
		
		self.layout =QVBoxLayout()
		
		# Done
		self.DoneBtn = QPushButton(
		text="Done",
		parent=self)
		self.DoneBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.DoneBtn.setFont(Font)
		self.DoneBtn.clicked.connect(self.Done)
		
		# BackButton
		self.BackBtn = QPushButton(
		text="Back",
		parent=self)
		self.BackBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.BackBtn.setFont(Font)
		self.BackBtn.clicked.connect(self.Back)
		
		# addactvButton
		self.AddActBtn = QPushButton(
		text="Add Activity",
		parent=self)
		self.AddActBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.AddActBtn.setFont(Font)
		self.AddActBtn.clicked.connect(self.AddAct)
		
		self.TopButLayout=QHBoxLayout()
		self.TopButLayout.addWidget(self.DoneBtn)
		self.TopButLayout.addWidget(self.BackBtn)
		self.TopButLayout.addWidget(self.AddActBtn)
		self.layout.addLayout(self.TopButLayout,stretch = 1)
		
		self.NameAndHours = QLabel("Hi " + self.Name + " you volunteered " +str(hours) + " Hours")
		self.NameAndHours.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.NameAndHours.setFont(Font)
		self.NameAndHours.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout.addWidget(self.NameAndHours,stretch = 2)
		
		self.activityNum =1
		self.activity1 = ActivitySelect(ActivityList)
		self.activity2 = ActivitySelect(ActivityList)
		self.activity3 = ActivitySelect(ActivityList) 
		self.activity4 = ActivitySelect(ActivityList)
		self.activity5 = ActivitySelect(ActivityList)
		self.NoMoreActivities = QLabel("The max number of activities is reached")
		self.NoMoreActivities.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.NoMoreActivities.setFont(Font)
		self.NoMoreActivities.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.layout.addWidget(self.activity1, stretch =4)
		
		
		self.setLayout(self.layout)
		
	
	def AddAct(self): #Adds an activity option to the display
		self.activityNum += 1
		if self.activityNum == 2:
			self.layout.addWidget(self.activity2,stretch =4)
		elif self.activityNum == 3:
			self.layout.addWidget(self.activity3,stretch =4)
		elif self.activityNum == 4:
			self.layout.addWidget(self.activity4,stretch = 4)
		elif self.activityNum == 5:
			self.layout.addWidget(self.activity5, stretch = 4)
		elif self.activityNum == 6:
			self.layout.addWidget(self.NoMoreActivities, stretch =4)
	
	def Done(self): #Checks if hours add up then emits done or warns user that hours do not match hours volunteered
		self.hoursEntered = 0
		self.HoursEnteredList = [self.activity1.hoursinput.text(), self.activity2.hoursinput.text(),self.activity3.hoursinput.text(),self.activity4.hoursinput.text(),self.activity5.hoursinput.text()]
		for text in self.HoursEnteredList:
			try:
				self.hoursEntered += float(text)
			except:
				#don't throw an error
				self.hoursEntered = self.hoursEntered

		if abs(self.hoursEntered - self.Hour) < 1e-9:
			##Read each activities values into respective db (only after validation passes)
			self.ActivityDatabaseWrite(self.Name, self.date, self.activity1.ActivitySelect.currentText(), self.activity1.hoursinput.text(), self.activity1.bikesinput.text()) 
			if self.activityNum >=2:
				self.ActivityDatabaseWrite(self.Name, self.date, self.activity2.ActivitySelect.currentText(), self.activity2.hoursinput.text(), self.activity2.bikesinput.text()) 
				if self.activityNum >=3:
					self.ActivityDatabaseWrite(self.Name, self.date, self.activity3.ActivitySelect.currentText(), self.activity3.hoursinput.text(), self.activity3.bikesinput.text()) 
					if self.activityNum >=4:
						self.ActivityDatabaseWrite(self.Name, self.date, self.activity4.ActivitySelect.currentText(), self.activity4.hoursinput.text(), self.activity4.bikesinput.text()) 
						if self.activityNum >=5:
							self.ActivityDatabaseWrite(self.Name, self.date, self.activity5.ActivitySelect.currentText(), self.activity5.hoursinput.text(), self.activity5.bikesinput.text()) 

			self.DoneFinished.emit("Done")
			self.accept()
		else:
			self.window =WarningDialog("The number of hours entered does not match the number of hours volunteered",0)
			self.window.resize(self.size())
			self.window.exec() 
			
	
	
	def Back(self):#exit dialog without committing changes
		self.DoneFinished.emit("")
		self.accept()
		
	def ActivityDatabaseWrite(self, Name, Date, ActivityName, ActivityHours, ActivityBikecount):##Write info into database for each activity
		self.SOICurs.execute(f"CREATE TABLE IF NOT EXISTS {ActivityName} (Name, Date, Hours, BikeCount)") 
		self.SOICurs.execute(f"INSERT INTO {ActivityName} VALUES (?,?,?,?)",[Name, Date, ActivityHours, ActivityBikecount ]) 
	
	
		
class ActivitySelect(QWidget): #Takes in a list of activities and creates a space for entering information about the activities like hours worked etc.
	def __init__(self, Activitylist, parent=None):
	
		super().__init__()
		self.ActivitySelect = QComboBox()
		for Activity in Activitylist:
			self.ActivitySelect.addItem(Activity)
			self.ActivitySelect.currentTextChanged.connect(self.ActivityChange)
		self.ActivitySelect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.ActivitySelect.setFont(Font)
		
		self.hoursprompt = QLabel('Hours worked', parent)
		self.hoursprompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.hoursprompt.setFont(Font)
		self.hoursprompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.hoursinput = QLineEdit(parent)
		self.hoursinput.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.hoursinput.setFont(Font)
		
		self.hourslayout = QVBoxLayout()
		self.hourslayout.addWidget(self.hoursprompt,stretch = 1)
		self.hourslayout.addWidget(self.hoursinput, stretch = 3)
		
		self.bikesprompt = QLabel('Bikes completed', parent)
		self.bikesprompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.bikesprompt.setFont(Font)
		self.bikesprompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.bikesinput = QLineEdit(parent)
		self.bikesinput.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.bikesinput.setFont(Font)
		
		self.bikeslayout = QVBoxLayout()
		self.bikeslayout.addWidget(self.bikesprompt,stretch =1)
		self.bikeslayout.addWidget(self.bikesinput, stretch = 3)
		
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.ActivitySelect, stretch = 2)
		self.layout.addLayout(self.hourslayout,stretch = 2)
		self.layout.addLayout(self.bikeslayout,stretch =2)
		
		self.setLayout(self.layout)
		
	def ActivityChange(self):#Can be rewritten but makes it so you can only set num of bikes for certain activities.
		if self.ActivitySelect.currentText() == "MoCo_bikes" or  self.ActivitySelect.currentText() == "Terrific_kids_bikes" or self.ActivitySelect.currentText() == "Bikes_for_sale":
			self.bikesinput.setReadOnly(False)
		else:
			self.bikesinput.setReadOnly(True)
			self.bikesinput.clear()
			self.bikesinput.setText('N/A')


