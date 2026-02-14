"""
Main menu dialog.

Contains:
- RBHSISO: the first screen shown, with buttons to open volunteer/client dialogs.

DB tables touched (via callbacks):
- VolunteerName
- ClientName
- SISOLOG
- ClientSISOLOG
"""

from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QSizePolicy

from rbh_siso.db import connect, ensure_schema
from rbh_siso.ui.common import Font, WarningDialog
from rbh_siso.ui.client_dialogs import ClientSignOut
from rbh_siso.ui.volunteer_dialogs import VolunteerSignIn, VolunteerSignOut


class RBHSISO(QDialog):#This is the Signin Signout Page
	def __init__(self,parent=None):
		super().__init__(parent)
		self.setWindowTitle("Welcome to RBH! Please sign in and out")
		self.NewVolWindow = None
#		self.resize(800, 200)
		
		#Open all the applicable database and tables the program will use. Initates if not already done so
		self.db = connect("Information.db")
		self.Curs = self.db.cursor()
		ensure_schema(self.Curs)
		
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
			res = self.Curs.execute(
				"SELECT rowid FROM SISOLOG WHERE Name = ? AND Date = ? AND Timeout IS NULL ORDER BY rowid DESC LIMIT 1",
				[Name, Date],
			)
			row = res.fetchone()
			if row is None:
				self.Warningwindow = WarningDialog("No matching sign-in found to sign out.", 0)
				self.Warningwindow.resize(self.size())
				self.Warningwindow.exec()
				return

			self.Curs.execute("UPDATE SISOLOG SET TimeOut = ? WHERE rowid = ?",[TimeOfDay, row[0]])
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


