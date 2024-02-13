import sqlite3
from prettytable import PrettyTable
import os

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

def main():
    conn = sqlite3.connect(input("Path to .db file: "))
    cursor = conn.cursor()

    while True:
        cls()
        print_table_names(cursor)
        table_name = input("Table name (or 'exit'): ")
        
        if table_name.lower() == 'exit':
            cls()
            break
        
        if table_name in ('..', '..', '..', '..'):
            continue

        
        print_table_data(cursor, table_name)

    conn.close()

if __name__ == "__main__":
    main()
