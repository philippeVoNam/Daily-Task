 # * author : Philippe Vo 
 # * date : Dec-22-2019 16:46:14
 
# * Imports
# 3rd Party Imports
from datetime import date, datetime, timedelta
import sys
# User Imports
from trello_mod import TrelloController
import sql_mod as sqlMod
from globals import MANDATORY, OPTIONAL, PASTDUE, COMPLETED

# * Code
class Task():
    def __init__(self, groupClass, title, dueDate, progress = 0, completed = 0, id = 0):
        # init
        # data saved to database
        self.groupClass = groupClass
        self.title = title
        self.dueDate = dueDate # this should be a datetime obj
        self.progress = progress
        self.completed = completed # boolean 0/1
        self.id = id

        # data saved on runtime only 
        self.dueDateStr = self.dueDate.strftime("%d-%m-%Y") # convert datetime -> str
        self.dueDateStrPrint = self.dueDate.strftime("%d-%B-%Y") # convert datetime -> str

        # Progress text
        self.progressText = self.progress_text_generate(self.progress, 100)

    def get_data(self):
        return (self.title, self.groupClass, self.dueDateStr, self.progress, self.completed)

    def get_list_print_data(self):
        return [self.id, self.groupClass, self.title, self.dueDateStrPrint, self.progressText]

    def progress_text_generate(self, count, total): # taken from https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
        bar_len = 20
        filled_len = int(round(bar_len * count / float(total)))

        percents = round(100.0 * count / float(total), 1)
        bar = '◼' * filled_len + '-' * (bar_len - filled_len)

        progressText = '[%s] %s%s' % (bar, percents, '%')
        return progressText

    def __str__(self):
        return self.groupClass + " : " + self.title  + " : " + str(self.progress)

class TaskController():
    def __init__(self):
        # init.
        pass

    def analyze_task(self, task):
        """
        feature: analyze the task to determine if it is :
        - mandatory
        - optional
        :input [Task] task: 
        :return [string] type: mandatory / optional
        """

        today = date.today()
        daysLeft = (task.dueDate.date() - today)
        daysLeft = int(daysLeft.days)

        if task.completed == 1:
            return COMPLETED

        if daysLeft <= 0:
            return PASTDUE
        elif daysLeft > 0 and daysLeft <= 2: # automatically mandatory if its due in 2 days
            return MANDATORY
        else:
            # if task progress  < expected progress -> MANDATORY
            expectedProgress = self.expected_progress(daysLeft)
            if task.progress < expectedProgress:
                return MANDATORY
            else:
                return OPTIONAL

    def expected_progress(self, daysLeft):
        """[calculates the expected progress percentage based on the number of daysLeft]
        
        Arguments:
            daysLeft {[int]} -- [description]
        
        Returns:
            [int] -- [description]
        """
        expectedProgress = -10 * daysLeft + 110
        return expectedProgress

    def filter_tasks(self, tasks):
        """ 
        feature : analyze tasks and return a list of mandatory and optional tasks
        :input [List Task] tasks
        :return [List Task,List Task] mandatoryTasks, optionalTasks
        """
        mandatoryTasks = []
        optionalTasks = []
        pastdueTasks = []

        for task in tasks:
            priority = self.analyze_task(task)
            if priority == PASTDUE:
                pastdueTasks.append(task)
            elif priority == MANDATORY:
                mandatoryTasks.append(task)
            elif priority == OPTIONAL:
                optionalTasks.append(task)
            else:
                pass # already completed

        return mandatoryTasks, optionalTasks, pastdueTasks

    def dbData_to_task(self, dbData):
        """
        feature: converts data from database into a Task
        """
        title = dbData[1] 
        groupClass = dbData[2] 
        datetime_object = datetime.strptime(dbData[3] , "%d-%m-%Y") # convert str -> datetime
        dueDate = datetime_object
        progress = int(dbData[4]) 
        completed = int(dbData[5])
        id = int(dbData[0])

        task = Task(groupClass, title, dueDate, progress, completed, id)

        return task

    def dbDatas_to_tasks(self, dbDatas):
        """[Converts list of dbDatas into tasks]
        
        Arguments:
            dbDatas {[List dbData]} -- [dbData is a tuple of data of the task]
        
        Returns:
            [List Task] -- [description]
        """
        tasks = []

        for dbData in dbDatas:
            task = self.dbData_to_task(dbData)
            tasks.append(task)

        return tasks

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

            # for a specific, this is only done once ... 
            task = Task(card["groupName"], card["cardName"], card["dueDate"], 0, 0)

            # insert into db
            database = r"resources/data.db"
            conn = sqlMod.create_connection(database)
            with conn:
                sqlMod.add_task(conn, task) # add task only if does not exist already 

    def print_task_table(self, tasksStr):
        """[prints the tasks in a table format]
        
        Arguments:
            tasksStr {[List of List String [id, groupname, title, duedate]]} -- [description]
        """
        # sort the tasks in terms of date
        tasksStr = sorted(tasksStr,key=lambda taskStr: datetime.strptime(taskStr[3] , "%d-%B-%Y"))

        for row in tasksStr:
            print("    {: <5} {: <12} {: <40} {: <20} {: <15}".format(*row))

    def update_task_progress(self, task, progress):
        """[update the progress of task]
        
        Arguments:
            task {[Task]} -- [description]
        """
        # if task is completed
        if progress < 0:
            print("Invalid input")
            return

        task.progress = progress
        
        if task.progress >= 100:
            self.set_task_complete(task)
            trelloController = TrelloController()
            trelloController.move_to_complete(task.groupClass, task.title)
            
        # if not
        else:
            task.progress = progress

            database = r"resources/data.db"
            conn = sqlMod.create_connection(database)
            with conn:
                sqlMod.update_task(conn, task)

    def set_task_complete(self, task):
        """[sets the task to completed]
        
        Arguments:
            task {[Task]} -- [description]
        """
        task.completed = 1 

        database = r"resources/data.db"
        conn = sqlMod.create_connection(database)
        with conn:
            sqlMod.update_task(conn, task)

    def get_task_by_id(self, id, tasks):
        """[return task by id if exists]
        
        Arguments:
            id {[integer]} -- [description]
            tasks {[List Tasks]} -- [description]
        
        Returns:
            [Task] -- [description]
        """
        for task in tasks:
            if task.id == id:
                return task

        return None
        
