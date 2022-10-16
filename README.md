# Description

The project recognition_attendance_sheet has been realized in the framework of the Data Architecture course of the DS2E master degree at the University of Strasbourg. The objective of our project is to automate the signing of an attendance sheet.

-    The program will scrap from the courses schedule (ernest) informations on the different classes of the day. (Course name, Professor name and the time of the course)

-    A facial recognition function will recognize the students present using a webcam.

-    The information will be associated and compiled in a document in pdf format.




# Requirements :

The following prerequisites are necessary for the proper execution of the program:

1.    Packages

Make sure to have the following libraries installed in your Python environment:

- opencv
- tkinter
- selenium
- ChromeDriverManager
- rich.progress
- rich.consome
- time
- pandas
- numpy
- os
- PIL
- dlib
- argparse
- ntpath



2.    Have access to an Ernest account (University of Strasbourg platform) in order to use the data from the timetable.


3.    Have chromedriver and google chrome installed on your computer. We also recommend that you make sure that your version of Chrome matches the version of the driver.


4.    the program will use your camera to verify the presence of an individual, so make sure you have authorized access to the webcam and that your "known_faces" folder contains the various individuals you wish to recognize.

- Run (on Windows) => python easy_facial_recognition.py --i known_faces

For MacOS you don't need to precise "python".


# Authors : 

- ROUSSAUX Claude @LarryJr64
- LANEVE Louis @LANEVE
- NEUNREUTHER Alexander @NEUNREUTHER

# References / Sources:

- The project of @anisayari -> https://github.com/anisayari/easy_facial_recognition
