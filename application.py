import string

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required
from datetime import datetime

# Configure application
app = Flask(__name__)

# User type
USER_TYPES = ["Student", "Teacher"]

# Semesters
SEMESTERS = ["First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth"]

# Courses
COURSES = [
    "CSE133", "CSE134", "CSE137", "CSE138", "CSE143", "CSE150",
    "CSE233", "CSE234", "CSE237", "CSE238", "CSE239", "CSE240",
    "CSE245", "CSE250", "CSE252", "CSE325", "CSE326", "CSE329",
    "CSE331", "CSE332", "CSE333", "CSE334", "CSE335","CSE336",
    "CSE345", "CSE346", "CSE350", "CSE361", "CSE362", "CSE365",
    "CSE366", "CSE367", "CSE368", "CSE373", "CSE374", "CSE376",
    "CSE426", "CSE433", "CSE434", "CSE439", "CSE440", "CSE446",
    "CSE450", "CSE452", "CSE475", "CSE480", "CSE482", "CSE484",
    "EEE109D", "EEE110D", "EEE111D", "EEE112D", "EEE201D", "EEE202D",
    "MAT102D", "MAT103D", "MAT204D", "ENG101D", "ENG102D", "IPE106D",
    "IPE108D", "PHY103D", "PHY202D","PHY207D", "BUS203D", "STA202D", "ECO105D"
]

# Status
STATUS = ["Running..", "Done", "Absent"]

# Course which teacher will select
COURSE = ""

# Course selected by student to see history
COURSE_S = ""

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///scheduler.db")


@app.route("/")
@login_required
def index():
    """Shows all scheduled viva."""

    courses = db.execute("SELECT * FROM courses ORDER BY course")
    return render_template("index.html", courses=courses)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Remember user type
        session["user_type"] = rows[0]["type"]

        # print("\n\n", session["user_type"], type(session["user_type"]), "\n\n")

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/course_teacher")
@login_required
def course_teacher():
    """
    Shows all the courses for which teacher has scheduled viva.
    """
    id = session["user_id"]
    courses = db.execute("SELECT * FROM courses WHERE user_id = ? ORDER BY course", id)

    return render_template("teacher.html", courses=courses)


@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    """Create scheduled viva"""

    # User id
    id = session["user_id"]

    if request.method == "POST":

        semester = request.form.get("semester")
        if not semester:
            return apology("Missing semester")

        course = request.form.get("course")
        if not course:
            return apology("Missing course")

        date = request.form.get("date")
        if not date:
            return apology("Missing date")

        time = request.form.get("time")
        if not time:
            return apology("Missing time")

        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        row1 = db.execute("SELECT * FROM courses WHERE course = ?", course)

        if len(row1) > 0:
            return apology("Viva is already scheduled for this course.")

        db.execute("INSERT INTO courses (user_id, name, semester, course, date, time) VALUES(?, ?, ?, ?, ?, ?)", id, name, semester, course, date, time)

        return redirect("/course_teacher")

    return render_template("create.html", semesters=SEMESTERS, courses=COURSES)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    """Delete scheduled viva"""

    id = session["user_id"]

    if request.method == "POST":

        course = request.form.get("course")
        if not course:
            return apology("Missing course")

        db.execute("DELETE FROM courses WHERE user_id = ? AND course = ?", id, course)
        
        db.execute("DELETE FROM registrants WHERE course = ?", course)
        return redirect("/course_teacher")

    scheduled_courses = []
    row = db.execute("SELECT course FROM courses WHERE user_id = ? ORDER BY course", id)

    for element in row:
        scheduled_courses.append(element["course"])

    return render_template("delete.html", scheduled_courses=scheduled_courses)


@app.route("/schedule", methods=["GET", "POST"])
@login_required
def schedule():
    """Shows schedule for viva"""

    id = session["user_id"]
    if request.method == "POST":

        course = request.form.get("course")
        if not course:
            return apology("Missing course")

        global COURSE
        COURSE = course
        return redirect("/schedule_calender")

    courses = db.execute("SELECT * FROM courses WHERE user_id = ? ORDER BY course", id)

    return render_template("course.html", courses=courses)


@app.route("/schedule_calender", methods=["GET", "POST"])
@login_required
def schedule_calender():
    """Keep track of viva"""

    if request.method == "POST":

        status = request.form.get("status")

        if not status:
            status = "pending.."
        name = request.form.get("name")
        course = request.form.get("course")

        # now (datetime): Current date and time
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")
        date_time = str(date_time)

        # Update status in history
        db.execute("UPDATE history SET status = ?, datetime = ? WHERE username = ? AND course = ?", status, date_time, name, course)

        return redirect("/schedule_calender")

    registrants = db.execute("SELECT * FROM history WHERE course = ? ORDER BY username", COURSE)

    return render_template("schedule.html", registrants=registrants, status=STATUS)


@app.route("/taken_courses")
@login_required
def taken_courses():
    """
    Displays all the courses a student has taken.
    """
    id = session["user_id"]
    courses = db.execute("SELECT * FROM registrants WHERE user_id = ? ORDER BY course", id)

    return render_template("taken_courses.html", courses=courses)


@app.route("/course_register", methods=["GET", "POST"])
@login_required
def course_register():
    """ Register students for course."""

    id = session["user_id"]

    if request.method == "POST":

        course = request.form.get("course")
        if not course:
            return apology("Missing course")

        row = db.execute("SELECT * FROM courses WHERE course = ?", course)

        teacher = row[0]["name"]

        row1 = db.execute("SELECT * FROM registrants WHERE user_id = ? AND course = ? AND teacher = ?", id, course, teacher)

        if len(row1) > 0:
            return apology("You have already registered for this course!")

        db.execute("INSERT INTO registrants (user_id, teacher, course) VALUES(?, ?, ?)", id, teacher, course)

        # Student name
        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        db.execute("INSERT INTO history (username, course) VALUES(?, ?)", name, course)
        return redirect("/taken_courses")

    courses = db.execute("SELECT * FROM courses ORDER BY course")

    return render_template("course_register.html", courses=courses)


@app.route("/course_deregister", methods=["GET", "POST"])
@login_required
def course_deregister():
    """Deregister from course"""

    id = session["user_id"]

    if request.method == "POST":

        course = request.form.get("course")
        if not course:
            return apology("Missing course")

        # Student name
        row = db.execute("SELECT username FROM users WHERE id = ?", id)
        name = row[0]["username"]

        # Delete student from history
        db.execute("DELETE FROM history WHERE username = ? AND course = ?", name, course)

        db.execute("DELETE FROM registrants WHERE user_id = ? AND course = ?", id, course)
        return redirect("/taken_courses")

    courses = db.execute("SELECT * FROM registrants WHERE user_id = ? ORDER BY course", id)

    return render_template("deregister.html", courses=courses)


@app.route("/history", methods=["GET", "POST"])
@login_required
def history():
    """Shows history of viva to student"""

    id = session["user_id"]
    
    if request.method == "POST":
        
        course = request.form.get("course")
        
        if not course:
            return apology("Missing course")
        
        global COURSE_S
        COURSE_S = course
        
        return redirect("/history_calender")

    courses = db.execute("SELECT course FROM registrants WHERE user_id = ? ORDER BY course", id)

    return render_template("history.html", courses=courses)
    
    
@app.route("/history_calender")
@login_required
def history_calender():
    """
    Shows the history of viva to student
    """
    registrants = db.execute("SELECT * FROM history WHERE course = ? ORDER BY username", COURSE_S)
    return render_template("summary.html", registrants=registrants)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (As by submitting a form via POST)
    if request.method == "POST":

        # Ensure user type was submitted
        user_type = request.form.get("type")
        if not user_type:
            return apology("Must select user type")

        # Ensure user name was submitted
        username = request.form.get("username")
        if not username:
            return apology("MUST PROVIDE USERNAME!")

        # Ensure username doesn't exist already
        row = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(row) > 0:
            return apology("USERNAME ALREADY EXIST!")

        # Get users password and confirmation from form
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure password and confirmation was provided
        if not password or not confirmation:
            return apology("MUST PROVIDE PASSWORD!")

        # Ensure password and confirmation are same
        if password != confirmation:
            return apology("PASSWORD DOESN'T MATCH!")

        # Checking valid password
        digits = "0123456789"
        punctuations = string.punctuation
        letters = string.ascii_lowercase + string.ascii_uppercase

        digit_present = False
        punctuation_present = False
        letter_present = False

        # Checking if password contain letter, digit, symbol or not
        for char in password:
            if char in digits:
                digit_present = True
            elif char in punctuations:
                punctuation_present = True
            elif char in letters:
                letter_present = True

        # If length of password is less than 5 or it doesn't contain letter, digit
        # and punctuation then reject registration
        if len(password) < 5 or not digit_present or not punctuation_present or not letter_present:
            return apology("Length of password must be atleast 5 and it should contain letter, digit and symbol")

        # Generates hash value of password
        password_hash = generate_password_hash(password)

        # Inserts user in the users table
        db.execute("INSERT INTO users (type, username, hash) VALUES(?, ?, ?)", user_type, username, password_hash)

        # Redirect user to login form
        return redirect("/login")

    # User reached route via GET (As by clicking a link or via redirect)
    return render_template("register.html", user_types=USER_TYPES)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
