"""
Volunteer dialogs.

Contains:
- VolunteerSignIn: select existing volunteer (autocomplete) or add a new volunteer, then sign in
- VolunteerSignOut: select volunteer currently signed in today, compute hours, then collect activity breakdown
- NewVolunteerInformation: register a volunteer (VolunteerName)
- VolunteerSelect: editable QComboBox helper used by multiple dialogs

DB tables touched:
- VolunteerName
- SISOLOG
"""

import math
from datetime import datetime

from PyQt6.QtCore import pyqtSignal,Qt
from PyQt6.QtWidgets import QComboBox, QPushButton, QVBoxLayout,QHBoxLayout, QWidget,QDialog, QLineEdit,QLabel, QCheckBox, QCompleter, QSizePolicy

from rbh_siso.ui.common import Font, InformationInput, WarningDialog
from rbh_siso.ui.activity_dialogs import SignOutInfo


class VolunteerSignIn(QDialog):#This is the splash screen for Volunteer signin
	VolSignIn = pyqtSignal(str,str)

	def __init__(self,VolsCurs,VolsDB,parent=None):
		super().__init__(parent)
		
		
		self.ManualEntry = False
		#This section opens the volunteers sqlite db and  pulls all the names from it
		self.VolsCurs = VolsCurs
		self.VolsDB = VolsDB


		
		self.setWindowTitle("Volunteer Sign In")
		# ~ self.resize(800, 200)
		
		# New colunteer button
		self.NewVolBtn = QPushButton(
		text="New Volunteer",
		parent=self)
		self.NewVolBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.NewVolBtn.setFont(Font)
		self.NewVolBtn.clicked.connect(self.New_Volunteer)
		
		# SignInButton
		self.SignInBtn = QPushButton(
		text="Sign In",
		parent=self)
		self.SignInBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.SignInBtn.setFont(Font)
		self.SignInBtn.clicked.connect(self.AcceptEntries)
		
		# BackButton
		self.BackBtn = QPushButton(
		text="Back",
		parent=self)
		self.BackBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.BackBtn.setFont(Font)
		self.BackBtn.clicked.connect(self.Back)
		
		#ForgotToSignButton
		self.ForgotToSignBtn = QPushButton(
		text="Forgot To Sign In",
		parent=self)
		self.ForgotToSignBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.ForgotToSignBtn.setFont(Font)
		self.ForgotToSignBtn.clicked.connect(self.ForgotToSign)
		
		#Initialize the newvolinfo as none
		self.window = None
		
		#Create a combo box which lists out volunteers from the database add in an autofill to help speed up process
		res = VolsCurs.execute("SELECT Name FROM VolunteerName")
		NamesTup=res.fetchall()
		self.Names =[]
		for Name in NamesTup:
			self.Names.append(Name[0])
		self.CurrentVolunteers = VolunteerSelect(self.Names)
		self.CurrentVolunteersFill = QCompleter(self.Names)
		self.CurrentVolunteersFill.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive) #allows for autocomplete to ignore case
		self.CurrentVolunteers.setCompleter(self.CurrentVolunteersFill) #sets the autofill completer	
		self.CurrentVolunteers.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.CurrentVolunteers.setFont(Font)
		self.VolunteerSelect = QLabel("Returning volunteers type and use the dropdown", parent=self)
		self.VolunteerSelect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.VolunteerSelect.setFont(Font)
		self.VolunteerSelect.setAlignment(Qt.AlignmentFlag.AlignCenter)
		
		# Button with a text and parent widget
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.VolunteerSelect, stretch =3)
		self.layout.addWidget(self.CurrentVolunteers, stretch = 4)
		
		BotButLayout=QHBoxLayout()
		BotButLayout.addWidget(self.NewVolBtn)
		BotButLayout.addWidget(self.SignInBtn)
		BotButLayout.addWidget(self.ForgotToSignBtn)
		BotButLayout.addWidget(self.BackBtn)
		self.layout.addLayout(BotButLayout,stretch = 1)
		
		self.setLayout(self.layout) 


	
	def New_Volunteer(self): #Pops up the NewVolunteerInformation poppup to add new information too can connect it to a the NEwNameSaved parent function
		self.window = NewVolunteerInformation(self.VolsCurs,self.VolsDB)
		self.window.NewName.connect(self.NewNameSaved) # Connect the dialog's signal to the parent's slot
		self.window.resize(self.size())
		self.window.exec() # Show the dialog as modal
	
	def NewNameSaved(self,Name): #Takes info from the NewVolunteerInformation popup and pushes to sign in function(acceptentries)
		if Name != "":
			if self.CurrentVolunteers.findText(Name) == -1:
				self.CurrentVolunteers.addItem(Name)
				self.Names.append(Name)
	
			self.CurrentVolunteers.setCurrentText(Name)
			self.AcceptEntries()
	
	
	def AcceptEntries(self):#send just the name and time back to add to add to database
		if self.ManualEntry is False:
			self.RightNow = datetime.now().strftime('%Y-%m-%d %H:%M') #place current time
		else:
			self.RightNowList =(datetime.now().strftime('%Y-%m-%d'),self.ManualTimeBox.input.text()) #take timeentered
			self.RightNow = " ".join(self.RightNowList)
		
		self.VolunteerName = self.CurrentVolunteers.currentText()
		if self.VolunteerName in self.Names: #only sign in if the name entered is already in volunteer database
			self.VolSignIn.emit(self.VolunteerName,self.RightNow)
			self.YouSignedInwindow =WarningDialog("Thank you for signing in!",1.5)
			self.YouSignedInwindow.resize(self.size())
			self.YouSignedInwindow.exec()
			self.accept()
		else:
			self.Warningwindow =WarningDialog("If you are a new volunteer please click 'New volunteer' otherwise please select from the dropdown",0)
			self.Warningwindow.resize(self.size())
			self.Warningwindow.exec()
	
	def Back(self):	#exit dialog without commiting chanes
		self.VolSignIn.emit("","")
		self.accept()
		
	def ForgotToSign(self):#Set manual entry to true and add buttons for it
		self.ManualEntry = True
		
		#Time
		self.ManualTimeBox =InformationInput("Time (military XX:XX)", self)
		self.layout.addWidget(self.ManualTimeBox)
		
		


class VolunteerSignOut(QDialog):#This is the splash screen for Volunteer signOut
	VolSignOut = pyqtSignal(str,str)
	
	def __init__(self,VolsCurs,VolsDB, parent=None):
		super().__init__(parent)
		
		
		#This section opens the volunteers sqlite db and  pulls all the names from it that signed in today and didn't sign out
		self.VolsCurs = VolsCurs
		self.VolsDB = VolsDB
		self.Date = datetime.now().strftime('%Y-%m-%d')
		res = VolsCurs.execute("SELECT Name FROM SISOLOG WHERE Date = ? AND TimeOut IS NULL",[self.Date])
		NamesTup=res.fetchall()
		self.Names =[]
		for Name in NamesTup:
			self.Names.append(Name[0])
		
		self.window =None
		
		self.setWindowTitle("Volunteer Sign Out")
#		self.resize(800, 200)
		
		# Sign Out
		self.SignOutBtn = QPushButton(
		text="Sign Out",
		parent=self)
		self.SignOutBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.SignOutBtn.setFont(Font)
		self.SignOutBtn.clicked.connect(self.SignOut)
		
		
		# BackButton
		self.BackBtn = QPushButton(
		text="Back",
		parent=self)
		self.BackBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.BackBtn.setFont(Font)
		self.BackBtn.clicked.connect(self.Back)
		
		#Create a combo box which lists out volunteers from the database
		self.CurrentVolunteers = VolunteerSelect(self.Names)
		self.CurrentVolunteers.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.CurrentVolunteers.setFont(Font)
		self.VolunteerSelect = QLabel("If you signed in use the dropdown", parent=self)
		self.VolunteerSelect.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.VolunteerSelect.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.VolunteerSelect.setFont(Font)
		
		
		# Button with a text and parent widget
		layout = QVBoxLayout()
		layout.addWidget(self.VolunteerSelect,stretch = 3)
		layout.addWidget(self.CurrentVolunteers, stretch =4)
		
		BotButLayout=QHBoxLayout()
		BotButLayout.addWidget(self.SignOutBtn)
		BotButLayout.addWidget(self.BackBtn)
		layout.addLayout(BotButLayout, stretch =1)
		
		self.setLayout(layout) 
	
	def SignOut(self): #This section calculates time spent in 1/4 hours and calls SignOutInfo for gathering more info
		self.RightNow = datetime.now().strftime('%Y-%m-%d %H:%M')
		self.Volunteer = self.CurrentVolunteers.currentText()
		self.res = self.VolsCurs.execute("SELECT Timein FROM SISOLOG WHERE Name =? AND Date = ? AND TimeOut IS NULL",[self.Volunteer,self.Date])
		self.TimeinTup=self.res.fetchall()
		if not self.TimeinTup:
			self.window = WarningDialog("No active sign-in found for this volunteer today.", 0)
			self.window.resize(self.size())
			self.window.exec()
			return
		try:
			self.Timein =datetime.strptime(self.TimeinTup[0][0],'%H:%M')
		except Exception:
			self.window = WarningDialog("Stored sign-in time is invalid; cannot compute hours.", 0)
			self.window.resize(self.size())
			self.window.exec()
			return
		self.Timestrip=self.RightNow.split(" ")
		self.Timeout =datetime.strptime(self.Timestrip[1],'%H:%M')
		self.TimePassed = self.Timeout-self.Timein
		self.Hours = math.ceil(self.TimePassed.total_seconds()/(60*15))*.25

		
		self.window = SignOutInfo(self.Volunteer,self.Hours,self.VolsCurs,self.VolsDB, self.Date)
		self.window.DoneFinished.connect(self.DoneComex)
		self.window.resize(self.size())
		self.window.exec() # Show the dialog as modal
	
	def DoneComex(self, Done):#done signing out close the window and pass data to the parent
		if Done == "Done":
			self.VolunteerName = self.CurrentVolunteers.currentText()
		
			self.VolSignOut.emit(self.VolunteerName,self.RightNow)
		self.accept()
	
	def Back(self):#exit dialog without committing any changes
		self.VolSignOut.emit("","")
		self.accept()
		



class VolunteerSelect(QComboBox):#This class creates a QCombobox populated with a list of names(volunteers)
	def __init__(self,nlist, parent=None):
	
		super().__init__()
		
		for Name in nlist:
			self.addItem(Name)
			
		self.setEditable(True)#makes typing possible
		self.setInsertPolicy(self.InsertPolicy.NoInsert) #Doesn't allow typing to be accepted, only for autocomplete
		self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.setFont(Font)
		
		
class NewVolunteerInformation(QDialog):#This is where volunteers can register their information
	NewName = pyqtSignal(str)
	
	def __init__(self,VolsCurs,VolsDB, parent=None):
		super().__init__(parent)
		self.VolsCurs = VolsCurs
		self.VolsDB = VolsDB
		
		self.setWindowTitle("Please Provide your information")
#		self.resize(800, 200)
		#NameBox
		self.Name =InformationInput("Name", self)
		#EmailBox
		self.Email =InformationInput("Email (optional)", self)
		#NumberBox
		self.Number =InformationInput("Phone Number (optional)", self)
		#AddressBox
		self.Address =InformationInput("Address (optional)", self)
		#Rockville Resident
		self.RckVillRes = QCheckBox("Rockville Resident?", self)
		self.RckVillRes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.RckVillRes.setFont(Font)

		
		self.SaveBtn = QPushButton(
		text="Save and Sign In",
		parent=self)
		self.SaveBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.SaveBtn.setFont(Font)
		self.SaveBtn.clicked.connect(self.AcceptEntries)
		
		self.BackBtn = QPushButton(
		text="Back",
		parent=self)
		self.BackBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.BackBtn.setFont(Font)
		self.BackBtn.clicked.connect(self.Back)
		
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.Name,stretch =3)
		self.layout.addWidget(self.RckVillRes,stretch =4)
		self.layout.addWidget(self.Email,stretch =3)
		self.layout.addWidget(self.Number,stretch =3)
		self.layout.addWidget(self.Address,stretch =3)

		
		self.BtnLayout = QHBoxLayout()
		self.BtnLayout.addWidget(self.SaveBtn)
		self.BtnLayout.addWidget(self.BackBtn)
		self.layout.addLayout(self.BtnLayout, stretch =1)
		self.setLayout(self.layout)
		
	def AcceptEntries(self): #Checks that critical information is provided and also sets empty optional fields to Not entered then writes to database
		if self.Name.input.text() != "":
			if self.Email.input.text() == "":
				self.Email.input.setText("Not Entered")
			if self.Address.input.text() == "":
				self.Address.input.setText("Not Entered")
			if self.Number.input.text() == "":
				self.Number.input.setText("Not Entered")
			#Add name and other info to database
			self.VolsCurs.execute("INSERT INTO VolunteerName VALUES (?,?,?,?,?)",[self.Name.input.text(),self.Email.input.text(),self.Address.input.text(),self.Number.input.text(),self.RckVillRes.isChecked()])
			self.VolsDB.commit()
			#send just the name back to add to dialogue box
			self.NewVolunteerName = self.Name.input.text()
			self.NewName.emit(self.NewVolunteerName)
			self.accept()
	
	def Back(self):#Exit without comitting changes
		self.NewName.emit("")
		self.accept()


