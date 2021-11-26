import string
import datetime
import subprocess
import uuid
from multiprocessing import Process
from timeit import default_timer as timer
import psycopg2.extras
import psycopg2
import random
USER = 'user'
DB = 'postgres'
PASS = 'pass'
INSERT_ROWS = 10000
CONCURRENCY = 10

psycopg2.extras.register_uuid()
conn = psycopg2.connect(dbname=DB, user=USER,
                        password=PASS, host='localhost')


cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS users;')
conn.commit()

cursor.execute('CREATE table users ('
               'name varchar(80),'
               'second_name varchar(80),'
               'birth_date date,'
               'id uuid  NOT NULL)')
cursor.execute('CREATE INDEX birthday_index ON users (birth_date);')
conn.commit()


def insert_user():
    conn = psycopg2.connect(dbname=DB, user=USER,
                            password=PASS, host='localhost')
    cursor = conn.cursor()
    for i in range(int(INSERT_ROWS/CONCURRENCY)):
        UUID = uuid.uuid4()
        name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=80))
        user_second_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=80))
        birth_day = datetime.datetime.today() - datetime.timedelta(days=i % 5000)
        cursor.execute(
            "INSERT INTO USERS (id, name, second_name, birth_date) VALUES (%s, %s, %s, %s);",
            (UUID, name, user_second_name, birth_day)
        )
        conn.commit()
    cursor.close()
    conn.close()


processes = []
start = timer()
for i in range(CONCURRENCY):
    p = Process(target=insert_user)
    p.start()
    processes.append(p)

for process in processes:
    process.join()
end = timer()
print(end - start)
