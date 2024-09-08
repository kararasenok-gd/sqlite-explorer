import sqlite3
from time import sleep
from rich.console import Console
from rich.table import Table
from rich.syntax import Syntax
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
import os
import json
import logging
import shutil

console = Console()
history = InMemoryHistory()

logging.basicConfig(filename='db_actions.log', level=logging.INFO)

def cls():
    os.system('cls' if os.name == 'nt' else 'clear')

def log_action(action, status):
    logging.info(f"Action: {action}, Status: {status}")

def print_table_names(cursor):
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    table = Table(title="Tables")

    table.add_column("Table Name", justify="left", style="cyan")

    for tbl in tables:
        table.add_row(tbl[0])
    
    console.print(table)

def print_table_data(cursor, table_name, page_size=10):
    cls()
    try:
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]

        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        total_rows = cursor.fetchone()[0]
        pages = (total_rows // page_size) + (1 if total_rows % page_size > 0 else 0)

        current_page = 0
        while True:
            offset = current_page * page_size
            cursor.execute(f"SELECT * FROM {table_name} LIMIT {page_size} OFFSET {offset};")
            rows = cursor.fetchall()

            table = Table(title=f"Data from {table_name} (Page {current_page + 1}/{pages})")

            for col_name in column_names:
                table.add_column(col_name, justify="left", style="magenta")

            for row in rows:
                table.add_row(*[str(cell) for cell in row])

            console.print(table)

            if current_page + 1 >= pages:
                input("No more pages. Press ENTER")
                break

            next_action = prompt("Next page (n), Previous page (p), or Exit (e): ", history=history).lower()
            if next_action == "n" and current_page + 1 < pages:
                current_page += 1
            elif next_action == "p" and current_page > 0:
                current_page -= 1
            elif next_action == "e":
                break

        input("Press ENTER")
    except Exception as e:
        log_action(f"Error displaying table {table_name}", "FAILED")
        input(str(e) + "\nPress ENTER")

def print_sql_query(query):
    syntax = Syntax(query, "sql", theme="monokai", line_numbers=True)
    console.print(syntax)

def check_db(db_name):
    if db_name is not None and os.path.isfile(db_name):
        return db_name
    else:
        raise FileNotFoundError("Error! You have not selected any database or the database does not exist.")

def backup_db(db_name):
    backup_name = db_name.replace('.db', '_backup.db')
    shutil.copy(db_name, backup_name)
    console.print(f"Backup created: {backup_name}", style="green")
    log_action(f"Backup created for {db_name}", "SUCCESS")

def restore_db(db_name):
    backup_name = db_name.replace('.db', '_backup.db')
    if os.path.exists(backup_name):
        shutil.copy(backup_name, db_name)
        console.print(f"Database restored from {backup_name}", style="green")
        log_action(f"Database {db_name} restored from backup", "SUCCESS")
    else:
        console.print("Backup file not found!", style="red")
        log_action(f"Backup file {backup_name} not found", "FAILED")

def export_to_file(cursor, table_name, file_format):
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    if file_format == "csv":
        output_file = table_name + ".csv"
        with open(output_file, "w") as f:
            cursor.execute(f"PRAGMA table_info({table_name})")
            col_names = [description[1] for description in cursor.fetchall()]
            f.write(",".join(col_names) + "\n")

            for row in rows:
                f.write(",".join([str(x) for x in row]) + "\n")
        
        console.print(f"Data exported to {output_file}", style="green")
        log_action(f"Table {table_name} exported to CSV", "SUCCESS")
    
    elif file_format == "sql":
        output_file = table_name + ".sql"
        with open(output_file, "w") as f:
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}';")
            create_table_sql = cursor.fetchone()[0]
            f.write(create_table_sql + ";\n")

            for row in rows:
                values = ', '.join([repr(x) for x in row])
                f.write(f"INSERT INTO {table_name} VALUES ({values});\n")
        
        console.print(f"Data exported to {output_file}", style="green")
        log_action(f"Table {table_name} exported to SQL", "SUCCESS")

def import_sql_script(cursor, filename):
    if not filename.endswith(".sql"):
        filename += ".sql"
    
    if os.path.exists(filename):
        with open(filename, "r") as file:
            sql_script = file.read()
        try:
            cursor.executescript(sql_script)
            console.print(f"Script {filename} executed successfully", style="green")
            log_action(f"Script {filename} executed", "SUCCESS")
        except sqlite3.Error as e:
            console.print(f"SQL Error: {e}", style="red")
            log_action(f"Error executing script {filename}", "FAILED")
    else:
        console.print(f"Script file {filename} not found!", style="red")
        log_action(f"Script file {filename} not found", "FAILED")

def main():
    db_name = check_db(prompt("Path to .db file: ", history=history))
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    while True:
        cls()
        print_table_names(cursor)
        table_name = prompt("Table name | command (>help): ", history=history)

        if table_name.lower() == '>exit':
            cls()
            log_action("User exit", "SUCCESS")
            break
        elif table_name.lower() == '>help':
            cls()
            console.print(">help - This Command", style="bold")
            console.print(">create <table|column|row> - Create something", style="bold")
            console.print(">delete <table|row> - Delete something", style="bold")
            console.print(">edit row - Edit row", style="bold")
            console.print(">sql - Run own sql query", style="bold")
            console.print(">import - Import SQL script", style="bold")
            console.print(">export <csv|sql> - Export table data", style="bold")
            console.print(">refresh - Refresh table list", style="bold")
            console.print(">backup - Backup database", style="bold")
            console.print(">restore - Restore database from backup", style="bold")
            input("Press ENTER")
            continue
        elif table_name.lower() == '>import':
            script_file = prompt("Enter SQL script filename (without .sql extension): ", history=history)
            import_sql_script(cursor, script_file)
            conn.commit()
            input("Press ENTER")
            continue
        elif table_name.lower() == '>export':
            file_format = prompt("Enter format for export (csv|sql): ", history=history)
            if file_format in ["csv", "sql"]:
                table = prompt("Enter table name for export: ", history=history)
                export_to_file(cursor, table, file_format)
                input("Press ENTER")
            else:
                console.print("Invalid format specified", style="red")
            continue
        elif table_name.lower() == '>refresh':
            cls()
            print_table_names(cursor)
            input("Press ENTER")
            continue
        elif table_name.lower() == '>backup':
            backup_db(db_name)
            input("Press ENTER")
            continue
        elif table_name.lower() == '>restore':
            restore_db(db_name)
            input("Press ENTER")
            continue
        elif table_name.lower() == '>sql':
            sql_query = prompt("Enter SQL query: ", history=history)
            print_sql_query(sql_query)
            try:
                cursor.execute(sql_query)
                conn.commit()
                results = cursor.fetchall()
                if results:
                    table = Table(title="Query Results")
                    for col in cursor.description:
                        table.add_column(col[0], justify="left", style="magenta")
                    for row in results:
                        table.add_row(*[str(cell) for cell in row])
                    console.print(table)
                else:
                    console.print("No results", style="yellow")
                log_action(f"Executed SQL query: {sql_query}", "SUCCESS")
            except sqlite3.Error as e:
                console.print(f"SQL Error: {e}", style="red")
                log_action(f"SQL query failed: {sql_query}", "FAILED")
            input("Press ENTER")
            continue
        elif table_name.lower() == "":
            console.print("Error! You have not selected more than one table", style="red")
            sleep(0.7)
        elif table_name.lower() == ">create table":
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
        
        elif table_name.lower() == ">create column":
            name = input("Column name: ")
            ctype = input("Column type: ")
            tname = input("Table name: ")
            cursor.execute(f"ALTER TABLE {tname} ADD COLUMN {name} {ctype};")
            conn.commit()
            continue

        elif table_name.lower() == ">create row":
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

        elif table_name.lower() == ">delete table":
            table = input("Table name: ")
            cursor.execute(f"DROP TABLE {table}")
            conn.commit
            continue

        elif table_name.lower() == ">delete row":
            table = input("Table name: ")
            column = input("Column name to navigate by: ")
            value = input("Column value (if column type is text, don't forget ' at the beginning and end): ")

            cursor.execute(f"DELETE FROM {table} WHERE {column} = {value}")
            conn.commit()
            continue

        elif table_name.lower() == ">edit row":
            table = input("Table name: ")
            column = input("Column name to navigate by: ")
            value = input("Column value (if column type is text, don't forget ' at the beginning and end): ")
            new_value = input("New value: ")

            cursor.execute(f"UPDATE {table} SET {column} = {new_value} WHERE {column} = {value}")
            conn.commit()
            continue
        else:
            print_table_data(cursor, table_name)

    conn.close()

if __name__ == "__main__":
    main()
