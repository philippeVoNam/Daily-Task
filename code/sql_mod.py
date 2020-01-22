import sqlite3
from sqlite3 import Error
# User imports
# from star_mod import *
# from video_mod import *

# SECTION : QUERY

def add_task(conn, task):
    """
    Create a new star into the stars table
    :param conn:
    :param star: -> object of Star
    :return: star id
    """
    data = task.get_data()
    sql = ''' INSERT INTO tasks(title, group_class, due_date, progress, completed)
              VALUES(?,?,?,?,?) '''
              
    cur = conn.cursor()
    cur.execute('SELECT * FROM tasks WHERE (title=? AND group_class=?)', (task.title, task.groupClass))
    entry = cur.fetchone()

    if entry is None:
        cur = conn.cursor()
        cur.execute(sql, data)
        conn.commit()
        # print("added")
        # print(task)
    else:
        # print("Entry already downloaded")
        # print(task)
        pass
    
    return cur.lastrowid

def delete_task(conn, groupClass, title):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = 'DELETE FROM tasks WHERE group_class=? AND title=?'
    cur = conn.cursor()
    cur.execute(sql, (groupClass,title))
    conn.commit()

def update_task(conn, task):
    """
    update priority, begin_date, and end date of a task
    :param conn:
    :param task:
    :return: project id
    """
    sql = ''' UPDATE tasks
              SET title = ?,
              group_class = ?,
              due_date = ?,
              progress = ?,
              completed= ? 
              WHERE group_class=? AND title=?'''
    cur = conn.cursor()
    cur.execute(sql, (task.title, task.groupClass, task.dueDateStr, task.progress, task.completed, task.groupClass, task.title))
    conn.commit()

def get_tasks_dbData(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks")
 
    tasks = cur.fetchall()

    return tasks

# SECTION : CREATE
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
 
    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

#Example Code
def main():
    database = r"resources/data.db"
 
    sql_create_tasks_table = """CREATE TABLE IF NOT EXISTS tasks (
                                    id integer PRIMARY KEY,
                                    title text NOT NULL,
                                    group_class text NOT NULL,
                                    due_date text NOT NULL,
                                    progress integer NOT NULL,
                                    completed integer NOT NULL
                                );"""

    # steps / total_steps = percentage completion
 
    # create a database connection
    conn = create_connection(database)
 
    # create tables
    if conn is not None:
        # create tasks table
        create_table(conn, sql_create_tasks_table)
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    main()