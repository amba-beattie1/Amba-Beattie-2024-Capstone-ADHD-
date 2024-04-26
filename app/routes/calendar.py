from app import app
from flask import render_template, session, redirect, request, flash
import calendar
import datetime as d
# This imports the data objects that you created in the data file in the classes folder
from app.classes.data import Task, User
# This imports the forms that you created in the forms file in the classes folder
from app.classes.forms import TaskForm
from bson.objectid import ObjectId

cal = calendar.Calendar(6)

# mormal and reverse month dictionaries
months = {'January': 1, 'February': 2, 'March': 3, 'April': 4, 'May': 5, 'June': 6, 'July': 7, 'August': 8, 'September': 9, 'October': 10, 'November': 11, 'December': 12}
reverseMonths = {v: k for k, v in months.items()}


# Get today's month and year if there are no arguments
# Get day for calendar display
currentday = str(d.datetime.now().day)
currentmonth = str(d.datetime.now().month)
currentyear = str(d.datetime.now().year)


# functions to load a list for a month and is called from the getMonth function
def flatten(array):
    new = []
    for i in array:
      for j in i:
        new.append(j)
    return new

# Gets month data from the calendar library which is imported above
def getMonth(month, year):
    weeks = cal.monthdayscalendar(int(year), months[month])
    return flatten(weeks)


# multiple @app.route decorators can be used to catch multiple combinations of url's input by the user
@app.route('/calendar', methods=['GET', 'POST'],  defaults={'month': reverseMonths[int(currentmonth)], 'year': currentyear})
@app.route('/calendar/<month>/<year>', methods=['GET', 'POST'])
def calen(month, year):
    # Manages looping the months and going to the next Year
    nextMonthYear = year
    prevMonthYear = year
    nextMonth = (months[month]+1)
    prevMonth = (months[month]-1)
    if month == "December":
        nextMonthYear = str(int(year)+1)
        nextMonth = 1
    elif month == "January":
        prevMonthYear = str(int(year)-1)
        prevMonth = 12

    nextMonthName = reverseMonths[nextMonth]
    prevMonthName = reverseMonths[prevMonth]
    nextYear = str(int(year)+1)
    prevYear = str(int(year)-1)


    #get tasks and format the dates for use on the calendar
    tasks = Task.objects()
    for task in tasks:
        task.date = task.date.strftime('%Y-%m-%d').split("-")
        task.date[1] = reverseMonths[int(task.date[1])]
        task.date[2] = str(int(task.date[2]))


    return render_template('calendar.html', monthName = month, nextMonthName = nextMonthName, prevMonthName = prevMonthName,
    month=getMonth(month, year), year=year, nextYear = nextYear, prevYear = prevYear, nextMonthYear = nextMonthYear, prevMonthYear = prevMonthYear,
    weekdays=['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
    tasks=tasks,
    currentday=currentday, currentmonth=currentmonth, monthNameReverse = months[month], currentyear=currentyear)

# this is the code that is run when the user requests a specific day
@app.route('/day/<day>/<month>/<year>', methods=['GET', 'POST'])
def day(day, month, year):

    if 'credentials' not in session:
        flash('You must be logged in to access that page')
        return redirect('authorize')

    #get tasks and format the dates for use on the calendar
    tasks = Task.objects()
    for task in tasks:
        task.date = task.date.strftime('%Y-%m-%d-%I:%M %p').split("-")
        task.date[1] = reverseMonths[int(task.date[1])]
        task.date[2] = str(int(task.date[2]))

    return render_template('day.html', day=day, month=month, year=year, tasks=tasks)

# TODO need an editTask route

# this function is run when the user requests to delete an task.
@app.route('/deletetask/<id>', methods=['GET', 'POST'])
def deletetask(id):

    if 'credentials' not in session:
        flash('You must be logged in to access that page')
        return redirect('authorize')

    for task in Task.objects:
        if str(task.id) == id:
            task.delete()
            return redirect('/calendar')
    return render_template("index.html")

# This code is run when the user wants to create a new task
@app.route('/newtask', methods=['GET', 'POST'])
@app.route('/newtask/<objtype>/<objid>', methods=['GET', 'POST'])
def newtask(objtype="none",objid="none"):
    if 'credentials' not in session:
        flash('You must be logged in to access that page')
        return redirect('authorize')
    form = TaskForm()
    if form.validate_on_submit():
      tasktime = str(form.time.data)
      tasktime = tasktime.split(":")
      taskdate = form.date.data
      taskdate = taskdate.strftime('%Y-%m-%d').split("-")
      taskdatetime = d.datetime.combine(d.date(int(taskdate[0]),int(taskdate[1]),int(taskdate[2])), d.time(int(tasktime[0]),int(tasktime[1]),int(tasktime[2])))

      newTask = Task()
      newTask.owner = ObjectId(session['currUserId'])
      newTask.description = form.description.data
      newTask.priority=form.priority.data
      newTask.notes=form.notes.data
      newTask.date = taskdatetime
      newTask.save()

      newTask.reload()

      if objtype == "job" and objid:
        newTask.update(job=ObjectId(objid))

      return redirect('/calendar')

    return render_template('newtask.html', form=form)