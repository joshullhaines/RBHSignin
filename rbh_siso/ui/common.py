"""
Shared UI widgets and helpers used across dialogs.

Keeping these in one module reduces circular-import issues when dialogs reference each other.
"""

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget, QDialog


# create a global font class (kept as-is from original file)
Font = QFont()
Font.setPointSize(20)


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


