"""
Client dialogs.

Contains:
- ClientSignOut: collects client sign-out info and optionally joins the mailing list.

DB tables touched:
- ClientName
- ClientSISOLOG
"""

from datetime import datetime

from PyQt6.QtCore import pyqtSignal,Qt,QStringListModel
from PyQt6.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QDialog, QCheckBox, QCompleter, QSizePolicy

from rbh_siso.ui.common import Font, InformationInput
from rbh_siso.ui.volunteer_dialogs import VolunteerSelect


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
		if self.mailingListEntry:
			return
		self.layout.addWidget(self.Email)
		self.layout.addWidget(self.PhoneNumber)
		
		self.mailingListEntry = True
		self.NewCliBtn.setEnabled(False)
		self.NewCliBtn.setText("Mailing list enabled")

	
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
		 


