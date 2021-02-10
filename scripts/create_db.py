import os
import contextlib
import sqlite3

def main():

    db_creation_script = os.path.join(
        os.path.dirname(__file__),
        'NexusLIMS_db_creation_script.sql'
    )
    db_name = 'nexuslims_db.sqlite'

    with open(db_creation_script, 'r') as sql_file:
        sql_script = sql_file.read()
    with contextlib.closing(sqlite3.connect(db_name)) as conn:
        with conn:  # auto-commits
            with contextlib.closing(conn.cursor()) as cursor:  # auto-closes
                cursor.executescript(sql_script)


if __name__ == "__main__":
    main()