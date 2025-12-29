import sqlite3
    
db = sqlite3.connect("Information.db")
Curs = db.cursor()
Curs.execute("DROP TABLE VolunteerName")
Curs.execute("CREATE TABLE VolunteerName(Name PRIMARY KEY, Email, Address, PhoneNumber, RockVilleRes)")
Curs.execute("""INSERT INTO VolunteerName VALUES ('Josh Hull','Hull.joshua@gmail.com', '216 Virginia Ave, Rockville, MD 20850', '215-983-7600',1)""")
Curs.execute("""INSERT INTO VolunteerName VALUES ('Steve','None','None','None', 1)""")


res = Curs.execute("SELECT Name FROM VolunteerName")
a=res.fetchall()
print(a)
 
Curs.execute("DROP TABLE ClientName")
Curs.execute("CREATE TABLE ClientName(Name PRIMARY KEY, Email, Address, PhoneNumber)")

Curs.execute("DROP TABLE SISOLOG")
Curs.execute("CREATE TABLE SISOLOG(Name, Date, Timein, Timeout)")
Name ="joe johnson"
Time = "2025-11-16 00:00"
TimeSplit = Time.split(" ")
Date = TimeSplit[0]
TimeOfDay = TimeSplit[1]

Curs.execute("INSERT INTO SISOLOG (Name, Date, Timein) VALUES (?, ?, ?)",[Name,Date,TimeOfDay])
db.commit()
