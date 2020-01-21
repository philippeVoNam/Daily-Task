 # * author : Philippe Vo 
 # * date : Jan-20-2020 23:31:03
 
# * Imports
# 3rd Party Imports
from datetime import date, datetime, timedelta
# User Imports
from sql_mod import add_task, get_tasks, create_connection
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

# * Code
def main():
    database = r"resources/data.db"
    conn = create_connection(database)

    taskController = TaskController()
    
    taskController.trello_download_to_db()

    tasks = get_tasks(conn)
    print(tasks)

    for task in tasks:
        taskGenerated = taskController.dbData_to_task(task)
        taskController.analyze_task(taskGenerated)

if __name__ == '__main__':
    main()