 # * author : Philippe Vo 
 # * date : Dec-22-2019 16:46:14
 
# * Imports
# 3rd Party Imports
from datetime import date, datetime, timedelta
# User Imports
from trello_mod import TrelloController
from sql_mod import add_task, create_connection

# * Code
class Task():
    def __init__(self, groupClass, title, dueDate, steps, totalSteps):
        # init
        self.groupClass = groupClass
        self.title = title
        self.dueDate = dueDate # this should be a datetime obj
        self.steps = steps
        self.totalSteps = totalSteps

        self.progress = round(steps/totalSteps) * 100

    def get_data(self):
        return (self.title, self.groupClass, self.dueDate, self.steps, self.totalSteps)

    def __str__(self):
        return "Task : " + self.groupClass + " : " + self.title

class TaskController():
    def __init__(self):
        # init.
        pass

    def analyze_task(self, task):
        """
        feature: analyze the task to determine if it is :
        - mandatory
        - optional
        """
        today = date.today()
        daysLeft = (task.dueDate.date() - today)
        daysLeft = int(daysLeft.days)

        if daysLeft <= 1:
            print(task)
            print("mandatory")
        else:
            print(task)
            print("optional")

    def dbData_to_task(self, dbData):
        """
        feature: converts data from database into a Task
        """
        title = dbData[1] 
        groupClass = dbData[2] 
        datetime_object = datetime.strptime(dbData[3] , "%d-%m-%Y") # convert datetime -> str
        dueDate = datetime_object
        steps = int(dbData[4]) 
        totalSteps = int(dbData[5])

        task = Task(groupClass, title, dueDate, steps, totalSteps)

        return task

    def trello_download_to_db(self):
        """
        feature : downloads all the cards that have a duedate of within 14 days into the database
        """
        trelloController = TrelloController()
        board = trelloController.get_board("SCHOOL WINTER")
        cards = trelloController.get_cards(board)

        for card in cards:
            today = date.today()
            daysLeft = (card["dueDate"].date() - today)
            daysLeft = int(daysLeft.days)

            dueDate = card["dueDate"].strftime("%d-%m-%Y") # convert str -> datetime
            task = Task(card["groupName"], card["cardName"], dueDate, 0, daysLeft )

            # insert into db
            database = r"resources/data.db"
            conn = create_connection(database)
            add_task(conn, task)
            