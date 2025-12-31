# Written by Josh Hull-Haines on 2025 to create a SISO Application for RBH
import sys
from datetime import datetime

from PyQt6.QtCore import QSize,pyqtSignal,Qt,QStringListModel, QTimer
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtWidgets import QApplication,QComboBox, QPushButton, QVBoxLayout,QHBoxLayout, QWidget,QDialog, QLineEdit,QLabel, QMainWindow, QCheckBox, QCompleter, QSizePolicy
import sqlite3
import math
from threading import Timer

#create a global font class
Font = QFont()
Font.setPointSize(20)
		
class RBHSISO(QDialog):#This is the Signin Signout Page
	def __init__(self,parent=None):
		super().__init__(parent)
		self.setWindowTitle("Welcome to RBH! Please sign in and out")
		self.NewVolWindow = None
#		self.resize(800, 200)
		
		#Open all the applicable database and tables the program will use. Initates if not already done so
		self.db = sqlite3.connect("Information.db")
		self.Curs = self.db.cursor()
		self.Curs.execute("CREATE TABLE IF NOT EXISTS VolunteerName(Name PRIMARY KEY, Email, Address, PhoneNumber, RockVilleRes)")
		self.Curs.execute("CREATE TABLE IF NOT EXISTS ClientName(Name PRIMARY KEY, Email, PhoneNumber, RockVilleRes)")       
		self.Curs.execute("CREATE TABLE IF NOT EXISTS ClientSISOLOG(Name, Date, HoursCount, Activity)")     
		self.Curs.execute("CREATE TABLE IF NOT EXISTS SISOLOG(Name, Date, Timein, Timeout)") 
		
		#Volunteer Sign in button and link to pop up window when pressed
		self.VolSignIn = QPushButton(
		text="Volunteer Sign in",
		parent=self)

		self.VolSignIn.setFont(Font)
		self.VolSignIn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.VolSignIn.clicked.connect(self.VolunteerSignIn)
		
		#Volunteer Sign out button and link to pop up window when pressed
		self.VolSignOut = QPushButton(
		text="Volunteer Sign Out",
		parent=self)
		self.VolSignOut.setFont(Font)
		self.VolSignOut.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.VolSignOut.clicked.connect(self.VolunteerSignOut)
		
		self.VolunteerLayout=QHBoxLayout()
		self.VolunteerLayout.addWidget(self.VolSignIn)
		self.VolunteerLayout.addWidget(self.VolSignOut)
		
		#Client Sign out button and link to pop up window when pressed
		self.CliSignOut = QPushButton(
		text="Client Sign Out",
		parent=self)
		self.CliSignOut.setFont(Font)
		self.CliSignOut.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.CliSignOut.clicked.connect(self.ClientSignOut)
		
		self.ClientLayout=QHBoxLayout()
		self.ClientLayout.addWidget(self.CliSignOut)
		
		Layout=QVBoxLayout()
		Layout.addLayout(self.VolunteerLayout)
		Layout.addLayout(self.ClientLayout)
		self.setLayout(Layout)
		self.adjustSize()
	
	
	def VolunteerSignIn(self):
		#Opens a VolunteerSignin pop up object as well as connecting it back to the parent with a function to do the signing in
		self.NewSignInWindow = VolunteerSignIn(self.Curs,self.db)
		self.NewSignInWindow.VolSignIn.connect(self.VolSignInComex) # Connect the dialog's signal to the parent's slot
		self.NewSignInWindow.resize(self.size())
		self.NewSignInWindow.exec() # Show the dialog as modal
		
	
	def VolSignInComex(self,Name,Time): #This function takes the name and time from the sign in popup object and enters it into the database
		if Name != "":
			TimeSplit = Time.split(" ")
			Date = TimeSplit[0]
			TimeOfDay = TimeSplit[1]
			SignedIn = self.CheckSignedIn(Name,Date,self.Curs,self.db) #check if signed in already before adding new entry
			if SignedIn is False:
				self.Curs.execute("INSERT INTO SISOLOG (Name, Date, Timein) VALUES (?, ?, ?)",[Name,Date,TimeOfDay])
				self.db.commit()
			else:
				self.Warningwindow =WarningDialog("You are already signed in!",0)
				self.Warningwindow.resize(self.size())
				self.Warningwindow.exec() 
	
	def VolunteerSignOut(self): #Opens a  VolunteerSignOut pop up object and connects it back to the parent to log information into the database
		self.NewSignOutWindow = VolunteerSignOut(self.Curs,self.db)
		self.NewSignOutWindow.VolSignOut.connect(self.VolSignOutComex) # Connect the dialog's signal to the parent's slot
		self.NewSignOutWindow.resize(self.size())
		self.NewSignOutWindow.exec() # Show the dialog as modal
	
	def VolSignOutComex(self,Name,Time): #Takes the name and date from the VolunteerSignOut popup and enters the information into the most recent matching signin in the database
		if Name != "":
			TimeSplit = Time.split(" ")
			Date = TimeSplit[0]
			TimeOfDay = TimeSplit[1]
			res = self.Curs.execute("SELECT rowid FROM SISOLOG WHERE Name = ? AND Date = ?",[Name, Date])
			IDS = res.fetchall()
			self.Curs.execute("UPDATE SISOLOG SET TimeOut = ? WHERE rowid = ?",[TimeOfDay, IDS[-1][0]])
			self.db.commit()
			
	def ClientSignOut(self):#Opens a ClientSignOut popup and connects it back to the parent to log information into the database
		self.newClientSignOutWindow = ClientSignOut(self.Curs,self.db)
		self.newClientSignOutWindow.showMaximized()
		self.newClientSignOutWindow.ClientSignOut.connect(self.ClientSignOutComex) # Connect the dialog's signal to the parent's slot
		self.newClientSignOutWindow.resize(self.size())
		self.newClientSignOutWindow.exec() # Show the dialog as modal
	
	def ClientSignOutComex(self, Name, Date, HoursCount, Activity):#Adds the Client SignoutInformation into the database
		if Name != "":
			self.Curs.execute("INSERT INTO ClientSISOLOG ( Name, Date, HoursCount, Activity) VALUES (?,?,?,?)",[Name, Date, HoursCount, Activity])
			self.db.commit()	
			
	def CheckSignedIn(self,Name,Date,SisoCurs,SisoDB): #Checks to see if a volunteer is already currently signed in
		self.SisoCurs = SisoCurs
		self.SisoDB = SisoDB
		res = SisoCurs.execute("SELECT COUNT(*) FROM SISOLOG WHERE Name = ? AND Timeout IS NULL",[Name])
		NumberSignIns=res.fetchall()
		if NumberSignIns[0][0]>0:
			return True
		else:
			return False

class ClientSignOut(QDialog):#This is the splash screen for the client signout
	ClientSignOut = pyqtSignal(str,str,str,str)
	def __init__(self,ClientCurs,ClientDB,parent=None):
		super().__init__(parent)
		
		
		self.mailingListEntry = False
		
		self.ClientCurs = ClientCurs
		self.ClientDB = ClientDB
		
		#pulls all previously entered client names from database
		res = self.ClientCurs.execute("SELECT Name FROM ClientName")
		NamesTup=res.fetchall()
		self.NamesList =[]
		for Name in NamesTup:
			self.NamesList.append(Name[0])
		#Create Name Entry with autocomplete from existing names in clientnamelog
		self.NamesListFill = QStringListModel()
		self.NamesListFill.setStringList(self.NamesList)
		self.AutofillNames=QCompleter(self.NamesListFill)
		self.AutofillNames.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)#allows for autocomplete to ignore case
		self.Names = InformationInput("Name (write over or stay anonymous)", self)
		self.Names.input.setCompleter(self.AutofillNames)
		self.Names.input.setText("RBH Client")
		
		
		self.setWindowTitle("Client Sign Out")

		# Join our mailing list button
		self.NewCliBtn = QPushButton(
		text="Join our mailing list?",
		parent=self)
		self.NewCliBtn.setFont(Font)
		self.NewCliBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.NewCliBtn.clicked.connect(self.mailingList)
		
		# SignOutButton
		self.SignOutBtn = QPushButton(
		text="Sign Out",
		parent=self)
		self.SignOutBtn.setFont(Font)
		self.SignOutBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.SignOutBtn.clicked.connect(self.SignOut)
		
		# BackButton
		self.BackBtn = QPushButton(
		text="Back",
		parent=self)
		self.BackBtn.setFont(Font)
		self.BackBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.BackBtn.clicked.connect(self.Back)
		
		#time spent entry
		self.Hours=InformationInput("Time Spent (in hours)", self)
		
		#Rockville Resident
		self.RckVillRes = QCheckBox("Rockville Resident?", self)
		self.RckVillRes.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.RckVillRes.setFont(Font)
		# ~ self.RckVillRes = ToggleButton("Rockville Resident", self)
		
		#Avtivity selection
		self.ClientActivityList = ["Client Activity", "Independent Bike Repair/Maintenance", "Assisted Bike Repair/Maintenance", "Donating Parts", "Donating Accessories", "Donating Bike(s)"]
		self.ClientActivities = VolunteerSelect(self.ClientActivityList)
		
		#Email entry
		self.Email = InformationInput("Email(Optional)",self)
		
		#PhoneNumber entry
		self.PhoneNumber = InformationInput("Phone Number(Optional)",self)
		
		# Button with a text and parent widget
		self.layout = QVBoxLayout()
		self.layout.addWidget(self.Names,stretch=2)
		self.layout.addWidget(self.RckVillRes,stretch=3)
		self.layout.addWidget(self.ClientActivities,stretch=3)
		self.layout.addWidget(self.Hours,stretch=2)
		self.layout.addWidget(self.NewCliBtn,stretch=1)
		
		
		self.Buttonslayout = QHBoxLayout()
		self.Buttonslayout.addWidget(self.SignOutBtn)
		self.Buttonslayout.addWidget(self.BackBtn)
		
		self.layout.addLayout(self.Buttonslayout,stretch=1)
		self.setLayout(self.layout)

		
	def mailingList(self): #Adds buttons into the popup for email and phone# entry and changes behaviour later
		self.layout.addWidget(self.Email)
		self.layout.addWidget(self.PhoneNumber)
		
		self.mailingListEntry = True

	
	def Back(self):#exit dialog without comitting any database changes
		self.ClientSignOut.emit("","", "","")
		self.accept()
		
	def SignOut(self):#First Check if name is part of client name database already or join mailing list is true.
		
		if self.Names.input.text() not in self.NamesList: #if the name is not already in the database add it as well as if rockville resident
			self.ClientCurs.execute("INSERT INTO ClientName (Name, RockVilleRes) VALUES (?,?)",[self.Names.input.text(),self.RckVillRes.isChecked()])
			self.ClientDB.commit()	

		if self.mailingListEntry == True: #if mailing list is true update email. phonenumber and if rockville resident
			self.ClientCurs.execute("UPDATE ClientName SET Email = ?, PhoneNumber = ?, RockvilleRes = ? WHERE Name = ?", [self.Email.input.text(), self.PhoneNumber.input.text(), self.RckVillRes.isChecked(),self.Names.input.text()])
			self.ClientDB.commit()	
			
		#finally log this signout in the SISOLOG by emitting it to pareny
		self.date = datetime.now().strftime('%Y-%m-%d')
		
		self.ClientSignOut.emit(self.Names.input.text(),self.date, self.Hours.input.text(), self.ClientActivities.currentText())
		self.accept()
		 


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
		self.Timein =datetime.strptime(self.TimeinTup[0][0],'%H:%M')
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
		
		##Read each activities values into respective db
		self.ActivityDatabaseWrite(self.Name, self.date, self.activity1.ActivitySelect.currentText(), self.activity1.hoursinput.text(), self.activity1.bikesinput.text()) 
		if self.activityNum >=2:
			self.ActivityDatabaseWrite(self.Name, self.date, self.activity2.ActivitySelect.currentText(), self.activity2.hoursinput.text(), self.activity2.bikesinput.text()) 
			if self.activityNum >=3:
				self.ActivityDatabaseWrite(self.Name, self.date, self.activity3.ActivitySelect.currentText(), self.activity3.hoursinput.text(), self.activity3.bikesinput.text()) 
				if self.activityNum >=4:
					self.ActivityDatabaseWrite(self.Name, self.date, self.activity4.ActivitySelect.currentText(), self.activity4.hoursinput.text(), self.activity4.bikesinput.text()) 
					if self.activityNum >=5:
						self.ActivityDatabaseWrite(self.Name, self.date, self.activity5.ActivitySelect.currentText(), self.activity5.hoursinput.text(), self.activity5.bikesinput.text()) 
		
		if self.hoursEntered == self.Hour:       
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
	
	
		
class WarningDialog(QDialog):#A more generic warning dialogue class with changeable messages and a delayed close. Pass 0 or less for no autoclose
	def __init__(self, WarnMessage,timeOut, parent=None):

		super().__init__(parent)

		self.setWindowTitle("")
		self.hoursMisMatch=QLabel(WarnMessage)
		self.hoursMisMatch.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.hoursMisMatch.setFont(Font)
		self.hoursMisMatch.setAlignment(Qt.AlignmentFlag.AlignCenter)
		#Acknoledge button
		self.AckBtn = QPushButton(
		text="Acknowledge",
		parent=self)
		self.AckBtn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.AckBtn.setFont(Font)
		self.AckBtn.clicked.connect(self.Ack)
	
		self.HourMisMatchLayout = QVBoxLayout()
		self.HourMisMatchLayout.addWidget(self.hoursMisMatch,stretch =4)
		self.HourMisMatchLayout.addWidget(self.AckBtn, stretch =1)
	
		self.setLayout(self.HourMisMatchLayout)
		if timeOut > 0:
			QTimer.singleShot(timeOut*1000, self.accept)
		
	def Ack(self):#exit dialog
		self.accept()
	
		
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


class InformationInput(QWidget): #A generic text prompt with editable text box right next to it
	def __init__(self, text, parent=None):
		self.text = text
		super().__init__()
		#InputBox
		self.prompt = QLabel(self.text, parent)
		self.prompt.setFont(Font)
		self.prompt.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.prompt.setAlignment(Qt.AlignmentFlag.AlignCenter)
		self.input = QLineEdit(parent)
		self.input.setFont(Font)
		self.input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		self.layout = QHBoxLayout()
		self.layout.addWidget(self.prompt, stretch = 2)
		self.layout.addWidget(self.input,stretch = 5)
		self.setLayout(self.layout)

##Below code felt increasingly brute forced and was scrapped in favor of checkbox
# ~ class ToggleButton(QWidget): #A generic button that has toggleable state and memory 
	# ~ def __init__(self, text, parent=None):
		# ~ self.EnteredText =text
		# ~ super().__init__()
		# ~ self.isChecked = 1
		# ~ self.BtnClick()
		
		# ~ self.Btn = QPushButton(text = self.EnteredText, parent = self)		
		# ~ self.Btn.setFont(Font)
		# ~ self.Btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
		# ~ self.Btn.clicked.connect(self.BtnClick)
		# ~ self.layout = QHBoxLayout()
		# ~ self.layout.addWidget(self.Btn)
		# ~ self.setLayout(self.layout)
		
	# ~ def BtnClick(self): #The toggle function happens when clicked
		# ~ if self.isChecked == 0: #in off state so turn on
			# ~ self.isChecked = 1
			# ~ self.Btn.text = self.EnteredText
			# ~ print(self.EnteredText)
		# ~ else: #in on state so turn off
			# ~ self.isChecked = 0
			# ~ print(" ".join(["Not", self.EnteredText]))
			# ~ self.Btn.setText (" ".join(["Not", self.EnteredText]))
		
		
if __name__ == "__main__":
	app = QApplication(sys.argv)
	
	window =RBHSISO()
	window.showMaximized()
	app.exec()
	
