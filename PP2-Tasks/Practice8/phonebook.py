import csv
from connect import connect

# ----Create Table----

def table():
    conn = connect()
    sql = """CREATE TABLE IF NOT EXISTS contacts(
        id SERIAL PRIMARY KEY,
        name VARCHAR(50) NOT NULL,
        phone VARCHAR(50) NOT NULL UNIQUE);
        """
    with conn.cursor() as cur:
        cur.execute(sql)
        conn.commit()
    
# ----INSERT----

def insert(name, phone):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("CALL upsert(%s, %s)", (name, phone))
        conn.commit()

def insert_console():
    name = input("Enter phone: ")
    phone = input("Enter name: ")
    insert(name, phone)
    print(f"Added: {name} - {phone}")
    
def insert_csv(csv_file):
    conn = connect()
    sql = "INSERT INTO contacts(name, phone) VALUES(%s, %s)"
    with conn.cursor() as cur:
        with open(csv_file, "r") as f:
            read = csv.reader(f)
            next(read)
            for row in read:
                name, phone = row
                cur.execute("CALL upsert(%s, %s)", (name, phone))
        conn.commit()
    print(f"Imported contacts: {csv_file}")

# ----SELECT----

def select_all():
    conn = connect()
    sql = "SELECT * FROM contacts"
    with conn.cursor() as cur:
        cur.execute(sql)
        return cur.fetchall()   

def search(pattern):
    conn = connect()
    sql = "SELECT * FROM contacts WHERE name ILIKE %s or phone ILIKE %s"
    like_p = f"%{pattern}%"
    with conn.cursor() as cur:
        cur.execute(sql, (like_p, like_p))
        return cur.fetchall()
    
# ----UPDATE----

def upd_phone(name, nw_phone):
    conn = connect()
    sql = "CALL upsert_contact(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql, (nw_phone, name)) 
        conn.commit()
        print(f"Updated {cur.rowcount} row(s)")

def upd_name(phone, nw_name):
    conn = connect()
    sql = "CALL upsert(%s, %s)"
    with conn.cursor() as cur:
        cur.execute(sql, (nw_name, phone))
        conn.commit()
        print(f"Updated {cur.rowcount} row(s)")
        
# ----DELETE----

def d_name(name):
    conn = connect()
    sql = "DELETE FROM contacts WHERE name = %s"
    with conn.cursor() as cur:
        cur.execute(sql, (name,))
        conn.commit()
        print(f"Deleted {cur.rowcount} row(s)")

def d_phone(phone):
    conn = connect()
    sql = "DELETE FROM contacts WHERE phone = %s"
    with conn.cursor() as cur:
        cur.execute(sql, (phone,))
        conn.commit()
        print(f"Deleted {cur.rowcount} row(s)")
    
# ----Main Menu----

def print_contacts(contacts):
    if not contacts:
        print("No contacts")
        return
    for i in contacts:
        print(f"[{i[0]}] {i[1]} - {i[2]}")
        
def main():
    table()
    
    while True:
        conn = connect()
        print("\n---- Phonebook ----")
        print("1. Show all contacts") 
        print("2. Add contacts from console") 
        print("3. Import from CSV")
        print("4. Search")
        print("5. Update phone by name")
        print("6. Update name by phone")
        print("7. Deleted by name") 
        print("8. Deleted by phone")
        print("0. Exit")
        
        choice = input("\nChoice: ")
        if choice == "1":
            print_contacts(select_all())
        elif choice == "2":
            insert_console()
        elif choice == "3":
            filename = input("CSV file: ")
            insert_csv(filename)
        elif choice == "4":
            pattern = input("Search: ")
            print_contacts(search(pattern))
        elif choice == "5":
            name = input("Name: ")
            nw_p = input("New phone: ")
            upd_phone(name, nw_p)
        elif choice == "6":
            phone = input("Phone: ")
            nw_n = input("New name: ")
            upd_name(phone, nw_n)
        elif choice == "7":
            dname = input("Name: ")
            d_name(dname)
        elif choice == "8":
            dphone = input("Phone: ")
            d_phone(dphone)
        elif choice == "0":
            break
        else:
            print("Инвалид другое число выбери")
    conn.close()
    print("Goodbye!")
    
if __name__ == "__main__":
    main()        
         
