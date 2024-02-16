import sqlite3
from time import sleep
from prettytable import PrettyTable
import os
import json

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    x = PrettyTable(['Tables'])
    for table in tables:
        x.add_row(table)
    
    print(x)

def print_table_data(cursor, table_name):
    cls()
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        table = PrettyTable(column_names)

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        for row in rows:
            table.add_row(row)

        # Print the table
        print(table)
        input("Press ENTER")
    except Exception as e:
        input(str(e) + "\nPress ENTER")

class TerminalColors:
    # ANSI escape codes for text colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_colored_text(text, color):
    print(f"{color}{text}{TerminalColors.RESET}")


def check_db(db_name):
    if db_name is not None and os.path.isfile(db_name):
        return db_name
    else:
        raise FileNotFoundError("Error! You have not selected any database or the database does not exist.")


def main():
    checkd_db = check_db(input("Path to .db file: "))
    conn = sqlite3.connect(checkd_db)
    cursor = conn.cursor()

    while True:
        cls()
        print_table_names(cursor)
        table_name = input("Table name | command (>help): ")
        
        if table_name.lower() == '>exit':
            cls()
            break
        if table_name.lower() == '>help':
            cls()
            print(">help - This Command\n>create <table|column|row> - Create something\n>delete <table|row> - Delete something\n>edit row - Edit row\n>sql - Run own sql query")
            input("Press ENTER")
            continue
        if table_name.lower() == ">create table":
            name = input("Table name: ")
            columns = []
            print("Type 'Done' if you finished")
            while True:
                column_name = input("Column name: ")
                if column_name.lower() == "done":
                    break
                column_type = input("Column type: ")
                if column_type.lower() == "done":
                    break

                columns.append('{"name":"' + column_name + '","type":"' + column_type + '"}')

            print("Creating...")
            print(columns)

            sql_req = f"CREATE TABLE IF NOT EXISTS {name}(\n"

            for a in columns:
                data = json.loads(a)
                sql_req += f"{data['name']} {data['type']},\n"

            sql_req = sql_req.rstrip(',\n')  # Remove trailing comma and newline
            sql_req += ");"

            cursor.execute(sql_req)
            conn.commit()
            continue
        
        if table_name.lower() == ">create column":
            name = input("Column name: ")
            ctype = input("Column type: ")
            tname = input("Table name: ")
            cursor.execute(f"ALTER TABLE {tname} ADD COLUMN {name} {ctype};")
            conn.commit()
            continue

        if table_name.lower() == ">create row":
            table = input("Table name: ")
            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()
            values = []
            for col in columns:
                val = input(f"{col[1]}: ")
                if col[2] == "INTEGER":
                    values.append(int(val))
                if col[2] == "TEXT":
                    values.append("'" + val + "'")
                if col[2] == "NUMERIC":
                    values.append(float(val))
                
            strng = ""

            for a in values:
                strng += f"{a}, "

            strng = strng.rstrip(", ")

            print(strng)

            cursor.execute(f"INSERT INTO {table} VALUES ({strng})")
            conn.commit()
            continue

        if table_name.lower() == ">delete table":
            table = input("Table name: ")
            cursor.execute(f"DROP TABLE {table}")
            conn.commit
            continue

        if table_name.lower() == ">delete row":
            table = input("Table name: ")
            column = input("Column name to navigate by: ")
            value = input("Column value (if column type is text, don't forget ' at the beginning and end): ")

            cursor.execute(f"DELETE FROM {table} WHERE {column} = {value}")
            conn.commit()
            continue

        if table_name.lower() == ">edit row":
            table = input("Table name: ")
            column = input("Column name to navigate by: ")
            value = input("Column value (if column type is text, don't forget ' at the beginning and end): ")
            new_value = input("New value: ")

            cursor.execute(f"UPDATE {table} SET {column} = {new_value} WHERE {column} = {value}")
            conn.commit()
            continue
        
        
        if table_name.lower() == ">sql":
            sql_query = input("Your sql query: ")
            cursor.execute(sql_query)
            conn.commit()
            for result in cursor.fetchall():
                print(result)
            input("Press ENTER")
            continue

        if table_name.lower() == "":
            print_colored_text("Error! You have not selected more than one table", TerminalColors.RED)
            sleep(0.7)
        else:
            print_table_data(cursor, table_name)
        

    conn.close()

if __name__ == "__main__":
    main()
