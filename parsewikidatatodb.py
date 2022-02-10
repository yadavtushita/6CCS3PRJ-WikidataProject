import psycopg2
from config import config

# connect to the db

con = None

try:
    # read connection parameters
    params = config()

    # connect to PostgreSQL server
    print('Connecting to the PostgreSQL database...')
    con = psycopg2.connect(**params)

    # cursor
    cur = con.cursor()

    # execute a statement
    print('PostgreSQL database version:')
    cur.execute('SELECT version()')

    # display the PostgreSQL database server version
    db_version = cur.fetchone()
    print(db_version)

    # execute the query
    cur.execute("SELECT id, first_name, last_name, country_of_birth FROM person LIMIT 5")

    rows = cur.fetchall()

    for r in rows:
        print(f"id {r[0]} first_name {r[1]} last_name {r[2]} country_of_birth {r[3]}")

    # close the cursor
    cur.close()

except (Exception, psycopg2.DatabaseError) as error:
    print(error)
finally:
    if con is not None:
        # close the connection
        con.close()
        print('Database connection closed.')
