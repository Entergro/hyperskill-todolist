from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, between
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker


class DataBase:
    __db = 'sqlite:///todo.db?check_same_thread=False'
    __Base = declarative_base()
    __session = None

    # Singleton pattern
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(DataBase, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        engine = create_engine(self.__db)
        self.__Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.__session = Session()

    class __Table(__Base):
        __tablename__ = 'task'
        id = Column(Integer, primary_key=True)
        task = Column(String, default='default_value')
        deadline = Column(Date, default=datetime.today())

        def __repr__(self):
            return self.task

    # -----------------------------------------------------------------------------
    # Get list of tasks from database
    #
    # Use date = (date_from, date_to) to get tasks from range of date: [from, to]
    # Use date = (0, date_to) to get tasks before the date: (0, date_to]
    # Use date = (date_from, 0) to get tasks from the date: [date_from, 0)
    # Use date = None to get all tasks
    # -----------------------------------------------------------------------------
    def db_get_task(self, date=None):
        rows = self.__session.query(self.__Table)
        if date is not None:
            if date[0] == 0:
                rows = rows.filter(self.__Table.deadline <= date[1])
            elif date[1] == 0:
                rows = rows.filter(self.__Table.deadline >= date[0])
            else:
                rows = rows.filter(between(
                    self.__Table.deadline, date[0], date[1]))
        rows = rows.order_by(self.__Table.deadline).all()
        return rows

    # -----------------------------------------------------------------------------
    # Push task to database
    # -----------------------------------------------------------------------------
    def db_push_task(self, tmp_text, tmp_date):
        new_row = self.__Table(task=tmp_text,
                               deadline=datetime.strptime(tmp_date,
                                                          '%Y-%m-%d').date())
        self.__session.add(new_row)
        self.__session.commit()

    # -----------------------------------------------------------------------------
    # Delete task from database
    # -----------------------------------------------------------------------------
    def db_delete_task(self, id_tmp):
        row = self.__session.query(self.__Table).filter(self.__Table.id == id_tmp).all()
        self.__session.delete(row[0])
        self.__session.commit()


# Create new task
def push_task():
    print("Enter task")
    text = input()
    print("Enter deadline")
    deadline = input()

    DB.db_push_task(text, deadline)
    print("The task has been added!\n")


# Print today task
def print_tasks_today():
    task_list = DB.db_get_task((datetime.today().date(), datetime.today().date()))
    print(f"Today {datetime.strftime(datetime.today(), '%e %b')}:")
    if task_list:
        i = 1
        for task in task_list:
            print(f"{i}. {task.task}")
    else:
        print("Nothing to do!")
    print()


# Print task in range: [date_from, date_to]
def print_tasks_range(date_from, date_to):
    task_list = DB.db_get_task((date_from, date_to))

    # Dict
    # {date: [task list for the date]}
    task_dict = {date_from + timedelta(days=i): []
                 for i in range((date_to - date_from).days)}
    for task in task_list:
        task_dict[task.deadline].append(task.task)

    for date, date_tasks in task_dict.items():
        print(f'{datetime.strftime(date, "%A %e %B")}:')
        if not date_tasks:
            print("Nothing to do!")
        i = 1
        for el in date_tasks:
            print(f'{i}. {el}')
        print()


# Print all tasks
def print_tasks_all():
    task_list = DB.db_get_task()
    print('All tasks:')
    if task_list:
        for i in range(len(task_list)):
            print(f'{i + 1}. '
                  f'{task_list[i]}. '
                  f'{datetime.strftime(task_list[i].deadline, "%e %b")}')
    else:
        print("Nothing to do!")
    print()


# Print task in range: (0, today - 1]
def print_tasks_missed():
    task_list = DB.db_get_task((0, datetime.today().date() - timedelta(days=1)))

    print('Missed tasks:')
    if task_list:
        i = 1
        for el in task_list:
            print(f'{i}. '
                  f'{el}. '
                  f'{datetime.strftime(el.deadline, "%e %b")}')
    else:
        print('Nothing is missed!')
    print()


def delete_task():
    task_list = DB.db_get_task()

    print('Choose the number of the task you want to delete:')
    if task_list:
        for i in range(len(task_list)):
            print(f'{i + 1}. '
                  f'{task_list[i]}. '
                  f'{datetime.strftime(task_list[i].deadline, "%e %b")}')
        del_list_id = int(input())  # List's id of the task to delete
        DB.db_delete_task(task_list[del_list_id - 1].id)
        print('The task has been deleted!')
    else:
        print('Nothing to delete!')
    print()


actions = ["1) Today's tasks",
           "2) Week's tasks",
           "3) All tasks",
           "4) Missed tasks",
           "5) Add task",
           "6) Delete task",
           "0) Exit"]

DB = DataBase()

while True:
    for act in actions:
        print(act)
    req = int(input())
    # Get today tasks
    if req == 1:
        print_tasks_today()
    # Get week's tasks
    elif req == 2:
        print_tasks_range(datetime.today().date(),
                          datetime.today().date() + timedelta(weeks=1))
    # Get all tasks
    elif req == 3:
        print_tasks_all()
    # Get missed tasks
    elif req == 4:
        print_tasks_missed()
    # Add a new task
    elif req == 5:
        push_task()
    # Delete an existing task
    elif req == 6:
        delete_task()
    # Exit
    else:
        print("Bye!")
        break
