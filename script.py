from jenkinsapi.jenkins import Jenkins
from argparse import ArgumentParser
from datetime import datetime
import sqlite3


def getJenkinsInstance(username, password):
    """ Returns a Jenkins Instance """
    baseurl = "http://localhost:8080"
    server = Jenkins(baseurl, username=username, password=password)
    return server 

def createJobTable(cursor):
    """ Creates the database table only if it doesn't already exist """
    cursor.execute('CREATE TABLE IF NOT EXISTS jobs (job_name TEXT, status TEXT, time_checked TIMETAMP)')

def createDatabaseConnection():
    """ Returns a database connection """
    connection = sqlite3.connect("jobs.db")
    createJobTable(connection)
    return connection

def insertJob(connection, item, status, current_time):
    """ Inserts a specific job to the database. """
    cursor = connection.cursor()
    try:
        cursor.execute('''INSERT INTO jobs(job_name, status, time_checked) VALUES(?, ?, ?)''', (item, status, current_time,))
        connection.commit()
    except sqlite3.Error, _exc:
        raise Exception("Error Inserting Adding Job to database: %s" %_exc)


def insertJobs(server, connection):
    """ Batch install of all the jobs in our jenkins instance. """
    cursor = connection.cursor()
    for index, item in enumerate(server.keys()):
        job = server.get_job(item)
        build = job.get_last_build()
        insertJob(connection, item, build.get_status(), datetime.utcnow())
    connection.close() 
 
if __name__ == "__main__":
    ap = ArgumentParser()
    ap.add_argument("username",  help="Username of your Jenkins instance")
    ap.add_argument("password", help="Password of your Jenkins instance")
    args = ap.parse_args()
    server = getJenkinsInstance(args.username, args.password)
    conn = createDatabaseConnection()
    insertJobs(server, conn)