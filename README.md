# SUST Viva Scheduler
YouTube video link for the project: https://youtu.be/VlpgEhphmcE


# Description

SUST Viva Scheduler is a dynamic web application that allows users to schedule and participate in viva or appointments. This app categorizes users in two types - student and teacher. Based on the type, users can have different functionalities.

Teachers can schedule viva for different courses by providing the semester in which the course is taken, course name, viva date and viva start time. Teachers can also delete viva which they have created. 

Teachers can view all the viva schedules which are scheduled by all of the teachers and can also view separately the viva schedules which were created by the teacher.

Teachers can see all the students who have registered for the teacher's course. On the time of viva teachers can update the status of viva of the students as pending or running or done or absent in real time and that time will be stored beside status automatically.

Students can view all the scheduled viva. They can register in the available vivas. They can also deregister from viva in which they are enrolled. They can also view separately all the courses in which they have registered.

By selecting the course in which they are enrolled, they can see the entire history of the course. They can see the status and time assigned to students after viva in real time.


# Prerequisites

SL | Learning Task | Description |
--:|:--------------|:------------|
1  | Language    | Python |  | |
2  | Web Basic    | Basics of HTML, CSS |   | |
3  | Web Framework    | Flask |   | |
1  | Database    | SQLite |  | |


# Project Setup
Log in to CS50 IDE (https://ide.cs50.io/) using github. Create a directory called viva by typing mkdir viva in the command prompt. Go to the viva directory by typing cd viva. In the viva directory make two directories called templates and static. Store the html files in templates directory and css file in static directory. Store application.py, helpers.py, scheduler.db in viva directory.
Staying in viva directory type flask run in the command prompt. You will see a link. Clicking and opening the link you can interact with the entire web app.

