import MySQLdb as sql

def getPasswordFromDb():
    host = ''
    user = ''
    passwd = ''
    db = ''
    table = ''
    coloumn = ''


    connection = sql.connect(host, user, passwd, db)

    cursor = connection.cursor()
    
    #TODO where clause
    cursor.execute('SELECT {0} FROM {1}'.format(coloumn, table))

    password = cursor.fetchone()

    connection.close()
    return password

