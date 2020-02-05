 #!/usr/bin/env python
 # * author : Philippe Vo 
 # * date : Jan-20-2020 23:31:03
 
# * Imports
# 3rd Party Imports
from datetime import date, datetime, timedelta
from pyfiglet import print_figlet
from PyInquirer import style_from_dict, Token, prompt
from PyInquirer import Validator, ValidationError
from examples import custom_style_3
import os
import cowsay
import calendar
from colored import fg, bg, attr

from blessed import Terminal

# User Imports
from sql_mod import add_task, get_tasks_dbData, create_connection
from task_mod import Task, TaskController

# * Template
# class ClassName():
#     """
#     description : What is it 
#     features    : What it can do
#     """
#     def __init__(self):
#         """ init. """

#     def func_name(self, inputs):
#         """
#         feature : what does it do 
#         :input [type] name: what is it 
#         :input [type] name:
#         :input [type] name:
#         :return [type] name: what is it
#         """

# TODO :
"""
- consider porting this to "curses" - will allow to still have the terminal feel, but with updating of the screen handled more elegantly. 
- maybe have a different version that i can use it in a smaller terminal ... 
- if trello updated some stuff, if task already exists in database -> it wont update it in database 
- maybe rethink the analyze_task ... 
- delete some tasks if completed - so ID dont get too big ... 
"""

class NumberValidator(Validator):
    def validate(self, document):
        try:
            int(document.text)
        except ValueError:
            raise ValidationError(
                message='Please enter a number',
                cursor_position=len(document.text))  # Move cursor to end

# * Code
def main_cli():
    taskController = TaskController()

    # Download from trello and update database
    mandatoryTasks, optionaltasks, pastduetasks = get_data_trello_to_db(True)

    validTaskList = get_tasks_valid([mandatoryTasks, optionaltasks, pastduetasks])

    # print data
    print_data(mandatoryTasks, optionaltasks, pastduetasks, taskController)

    # Ask which task to update
    commandAnswer = ask_command()

    # Main Loop
    while commandAnswer != "Quit":
        taskID = ask_update_task()
        
        # update task
        task = taskController.get_task_by_id(taskID, validTaskList)
        if task == None:
            print("Invalid ID.")
        else :
            progress = ask_progress()
            taskController.update_task_progress(task, progress)

            # clear screen
            clear_screen()

            # Update database and re-print
            ## Download from trello and update database
            # SECTION : get_data()
            mandatoryTasks, optionaltasks, pastduetasks = get_data_trello_to_db(True)
            validTaskList = get_tasks_valid([mandatoryTasks, optionaltasks, pastduetasks])

            # SECTION : display_screen()
            ## print data
            print_data(mandatoryTasks, optionaltasks, pastduetasks, taskController)

        # SECTION : wait_menu_selection() -> either "Update Task" / "Quit" / "Keyboard Input Selection Menu"
        # ask command
        commandAnswer = ask_command()

def main_blessed():
    """ using the blessed UI """

def ask_command():
    """[ask user if they want to Update Task or Quit program]
    
    Returns:
        [Dictionary] -- [description]
    """
    questions = [{
    'type': 'list',
    'name': 'choice',
    'message': 'What is your command?',
    'choices': ['Update Task', 'Quit']
    }]
    answers = prompt(questions, style=custom_style_3)
    
    return answers["choice"]

def ask_update_task():
    """[ask which task to update]
    
    Returns:
        [Dictionary] -- [description]
    """
    questions = [{
    'type': 'input',
    'name': 'id',
    'message': 'Which task to you want to update ?',
    'validate': NumberValidator,
    'filter': lambda val: int(val)
    }]
    answers = prompt(questions, style=custom_style_3)
    
    return answers["id"]

def ask_progress():
    questions = [{
    'type': 'input',
    'name': 'progress',
    'message': 'At progress % do you think you are ?',
    'validate': NumberValidator,
    'filter': lambda val: int(val)
    }]
    answers = prompt(questions, style=custom_style_3)
    
    return answers["progress"]

def get_tasks_valid(taskLists):
    """[scans all the containers and add all the valid tasks (ie not completed yet)]
    
    Arguments:
        taskLists {[type]} -- [description]
    
    Returns:
        [List Integer] -- [idBank]
    """
    validTaskList = []
    for taskList in taskLists:
        for task in taskList:
            validTaskList.append(task)

    return validTaskList

def print_data(mandatoryTasks, optionaltasks, pastduetasks, taskController):
    # Printing Tasks
    colorMandatory = "255;2;151:" 
    colorOptional = "2;255;232:" 
    colorPastdue = "255;255;255:" 

    mandatoryTasksStr = []
    for task in mandatoryTasks:
        mandatoryTasksStr.append(task.get_list_print_data())

    optionalTasksStr = []
    for task in optionaltasks:
        optionalTasksStr.append(task.get_list_print_data())

    pastdueTasksStr = []
    for task in pastduetasks:
        pastdueTasksStr.append(task.get_list_print_data())

    print_figlet("Mandatory", font="slant", colors=colorMandatory)
    taskController.print_task_table(mandatoryTasksStr)

    print_figlet("Optional", font="slant", colors=colorOptional)
    taskController.print_task_table(optionalTasksStr)

    print_figlet("Past-Due", font="slant", colors=colorPastdue)
    taskController.print_task_table(pastdueTasksStr)

    print("")

    today = date.today()
    dateStr = today.strftime("%d-%B-%Y")
    cowsay.tux("Current Date : " + dateStr)

def clear_screen():
    os.system("clear")

def get_data_trello_to_db(updateFromTrello = False):
    # Downloading Trello Data and updating database 
    database = r"resources/data.db"
    conn = create_connection(database)

    with conn:
        try:
            taskController = TaskController()

            if updateFromTrello:
                taskController.trello_download_to_db()

        except Exception as e:
            color = bg('indian_red_1a') + fg('white')
            reset = attr('reset')
            print(color + "Could not download data from Trello. Database hade not been updated." + reset)
            print(e)

        tasksDbData = get_tasks_dbData(conn)
        tasks = taskController.dbDatas_to_tasks(tasksDbData)

    # Filtering tasks between mandatory and optional 
    mandatoryTasks, optionaltasks, pastduetasks = taskController.filter_tasks(tasks)

    return mandatoryTasks, optionaltasks, pastduetasks 

# ANCHOR : Blessed

# FIXME : main thing that is really "slow" -> get_data() from Trello ...

menu = [["o Update Task"], ["o Quit"]]

def main_blessed():
    """ using the blessed UI """
    # SECTION : get_data()
    mandatoryTasks, optionaltasks, pastduetasks = get_data_trello_to_db(True)
    validTaskList = get_tasks_valid([mandatoryTasks, optionaltasks, pastduetasks])

    data = [mandatoryTasks, optionaltasks, pastduetasks]

    # SECTION : display_screen()
    display_screen(data,"")

    # SECTION : main loop
    term = Terminal()
    taskController = TaskController()

    with term.fullscreen():
        selection = 0
        display_screen(data, selection)
        selection_inprogress = True
        program_running = True

        with term.cbreak(), term.hidden_cursor():

            while program_running:
                while selection_inprogress:
                    key = term.inkey()
                    if key.is_sequence:
                        if key.name == 'KEY_TAB':
                            selection += 1
                        if key.name == 'KEY_DOWN':
                            selection += 1
                        if key.name == 'KEY_UP':
                            selection -= 1
                        if key.name == 'KEY_ENTER':
                            selection_inprogress = False
                    elif key:
                        print("got {0}.".format(key))

                    selection = selection % len(menu)

                    display_screen(data, selection)
                
                if menu[selection][0] == "o Update Task":
                    # SECTION : Update Task
                    selection_inprogress = True

                    # get the task ID
                    taskID = ask_update_task() # FIXME : Have to modify ?
        
                    # update task
                    task = taskController.get_task_by_id(taskID, validTaskList)
                    if task == None:
                        print("Invalid ID.")
                    else :
                        progress = ask_progress()
                        taskController.update_task_progress(task, progress)

                    # SECTION : get_data()
                    mandatoryTasks, optionaltasks, pastduetasks = get_data_trello_to_db(False)
                    validTaskList = get_tasks_valid([mandatoryTasks, optionaltasks, pastduetasks])

                    data = [mandatoryTasks, optionaltasks, pastduetasks]

                    display_screen(data, selection)
                
                else:
                    print("Exit Program.")
                    program_running = False
            

def display_screen(data, selection):
    """ display the screen """
    term = Terminal()
    taskController = TaskController()

    # Clear screen
    print(term.clear())

    # Convert data to str
    mandatoryTasks = data[0]
    optionaltasks = data[1]
    pastduetasks = data[2]

    mandatoryTasksStr = []
    for task in mandatoryTasks:
        mandatoryTasksStr.append(task.get_list_print_data())

    optionalTasksStr = []
    for task in optionaltasks:
        optionalTasksStr.append(task.get_list_print_data())

    pastdueTasksStr = []
    for task in pastduetasks:
        pastdueTasksStr.append(task.get_list_print_data())

    # Print Titles and Data
    colorMandatory = "255;2;151:" 
    colorOptional = "2;255;232:" 
    colorPastdue = "255;255;255:" 

    # print(term.bold_red("Mandatory"))
    print_figlet("Mandatory", font="slant", colors=colorMandatory)

    taskController.print_task_table(mandatoryTasksStr)

    # print(term.bold_green("Optional"))
    print_figlet("Optional", font="slant", colors=colorOptional)

    taskController.print_task_table(optionalTasksStr)

    # print(term.bold_grey("PastDue"))
    print_figlet("Past-Due", font="slant", colors=colorPastdue)

    taskController.print_task_table(pastdueTasksStr)

    print("")

    # Current Date
    today = date.today()
    dateStr = today.strftime("%d-%B-%Y")
    cowsay.tux("Current Date : " + dateStr)

    # Print Menu
    for (idx, m) in enumerate(menu):
        if idx == selection:
            print(term.red(m[0]))
        else:
            print(term.white(m[0]))

if __name__ == '__main__':
    # main_cli()
    main_blessed()