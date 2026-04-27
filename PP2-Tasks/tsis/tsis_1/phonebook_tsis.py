import csv
import json
from datetime import date
from connect import connect

def setup_db():
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id   SERIAL PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL
            );
            INSERT INTO groups (name) VALUES
                ('Family'),('Work'),('Friend'),('Other')
            ON CONFLICT (name) DO NOTHING;

            ALTER TABLE contacts
                ADD COLUMN IF NOT EXISTS email    VARCHAR(100),
                ADD COLUMN IF NOT EXISTS birthday DATE,
                ADD COLUMN IF NOT EXISTS group_id INTEGER REFERENCES groups(id);

            CREATE TABLE IF NOT EXISTS phones (
                id         SERIAL PRIMARY KEY,
                contact_id INTEGER REFERENCES contacts(id) ON DELETE CASCADE,
                phone      VARCHAR(20) NOT NULL,
                type       VARCHAR(10) CHECK (type IN ('home','work','mobile'))
            );
        """)

        cur.execute("""
            INSERT INTO phones (contact_id, phone, type)
            SELECT id, phone, 'mobile' FROM contacts
            WHERE phone IS NOT NULL
              AND id NOT IN (SELECT DISTINCT contact_id FROM phones)
            ON CONFLICT DO NOTHING;
        """)
        conn.commit()
    conn.close()

def get_or_create_group(cur, group_name: str) -> int | None:
    if not group_name:
        return None
    cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group_name,))
    row = cur.fetchone()
    if row:
        return row[0]
    cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (group_name,))
    return cur.fetchone()[0]


def print_contact_row(row):
    cid, name, email, birthday, grp, phones = row
    print(f"[{cid}] {name}")
    print(f"Phones: {phones or '—'}")
    print(f"Email: {email or '—'}")
    print(f"Birthday: {birthday or '—'}")
    print(f"Group: {grp or '—'}")


def list_groups():
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("SELECT id, name FROM groups ORDER BY name")
        rows = cur.fetchall()
    conn.close()
    return rows


def pick_phone_type() -> str:
    while True:
        t = input("  Phone type (home / work / mobile) [mobile]: ").strip().lower() or "mobile"
        if t in ("home", "work", "mobile"):
            return t
        print("  Invalid type. Enter home, work, or mobile.")

def add_contact_console():

    name     = input("Name        : ").strip()
    email    = input("Email       : ").strip() or None
    birthday = input("Birthday    (YYYY-MM-DD, blank to skip): ").strip() or None
    phone    = input("Phone number: ").strip()
    ptype    = pick_phone_type()

    print("Groups:", ", ".join(g[1] for g in list_groups()))
    group    = input("Group (blank to skip): ").strip() or None

    conn = connect()
    with conn.cursor() as cur:
        cur.execute("CALL upsert(%s, %s)", (name, phone))

        gid = get_or_create_group(cur, group) if group else None
        cur.execute(
            "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE name=%s",
            (email, birthday, gid, name)
        )
        cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
        cid = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s) "
            "ON CONFLICT DO NOTHING",
            (cid, phone, ptype)
        )
        conn.commit()
    conn.close()
    print(f"  ✓ Contact '{name}' saved.")


def add_phone_to_contact():
    name  = input("Contact name : ").strip()
    phone = input("Phone number : ").strip()
    ptype = pick_phone_type()
    conn = connect()
    with conn.cursor() as cur:
        try:
            cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
            conn.commit()
            print(f"  ✓ Phone added.")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Error: {e}")
    conn.close()


def move_contact_to_group():
    name  = input("Contact name : ").strip()
    print("Existing groups:", ", ".join(g[1] for g in list_groups()))
    group = input("Group name   : ").strip()
    conn = connect()
    with conn.cursor() as cur:
        try:
            cur.execute("CALL move_to_group(%s, %s)", (name, group))
            conn.commit()
            print(f"  ✓ Done.")
        except Exception as e:
            conn.rollback()
            print(f"  ✗ Error: {e}")
    conn.close()


def search_all(pattern: str):
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
        rows = cur.fetchall()
    conn.close()
    return rows


def print_search_results(rows):
    if not rows:
        print("  No contacts found.")
        return
    for row in rows:
        print_contact_row(row)

def filter_by_group():
    groups = list_groups()
    print("\n  Available groups:")
    for gid, gname in groups:
        print(f"    {gid}. {gname}")
    choice = input("  Enter group name (or part of it): ").strip()

    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE g.name ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """, (f"%{choice}%",))
        rows = cur.fetchall()
    conn.close()
    print_search_results(rows)

def search_by_email():
    pattern = input("  Email search: ").strip()
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            WHERE c.email ILIKE %s
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """, (f"%{pattern}%",))
        rows = cur.fetchall()
    conn.close()
    print_search_results(rows)

SORT_COLUMNS = {
    "1": ("c.name",        "Name"),
    "2": ("c.birthday",    "Birthday"),
    "3": ("c.id",          "Date added (ID)"),
}

def show_sorted():
    print("\n  Sort by:")
    for k, (_, label) in SORT_COLUMNS.items():
        print(f"    {k}. {label}")
    key = input("  Choice [1]: ").strip() or "1"
    col = SORT_COLUMNS.get(key, SORT_COLUMNS["1"])[0]

    conn = connect()
    with conn.cursor() as cur:
        cur.execute(f"""
            SELECT c.id, c.name, c.email, c.birthday, g.name,
                   STRING_AGG(ph.phone || ' (' || COALESCE(ph.type,'?') || ')', ', ')
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY {col} NULLS LAST
        """)
        rows = cur.fetchall()
    conn.close()
    print_search_results(rows)

PAGE_SIZE = 5

def paginated_browse():
    offset = 0
    conn = connect()
    while True:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM paginated(%s, %s)", (PAGE_SIZE, offset))
            rows = cur.fetchall()

        if not rows:
            print("  (no more contacts)")
            break

        print(f"\n  --- Page {offset // PAGE_SIZE + 1} ---")
        for r in rows:
            print(f"  {r[0]} — {r[1]}")  

        cmd = input("  [n]ext / [p]rev / [q]uit: ").strip().lower()
        if cmd == "n":
            if len(rows) < PAGE_SIZE:
                print("  Already on last page.")
            else:
                offset += PAGE_SIZE
        elif cmd == "p":
            offset = max(0, offset - PAGE_SIZE)
        elif cmd == "q":
            break
    conn.close()


def export_json():
    filename = input("  Output file [contacts.json]: ").strip() or "contacts.json"
    conn = connect()
    with conn.cursor() as cur:
        cur.execute("""
            SELECT c.id, c.name, c.email,
                   TO_CHAR(c.birthday, 'YYYY-MM-DD') AS birthday,
                   g.name AS group_name,
                   COALESCE(
                       JSON_AGG(
                           JSON_BUILD_OBJECT('phone', ph.phone, 'type', ph.type)
                       ) FILTER (WHERE ph.id IS NOT NULL),
                       '[]'::json
                   ) AS phones
            FROM contacts c
            LEFT JOIN groups g  ON g.id = c.group_id
            LEFT JOIN phones ph ON ph.contact_id = c.id
            GROUP BY c.id, c.name, c.email, c.birthday, g.name
            ORDER BY c.name
        """)
        rows = cur.fetchall()
    conn.close()

    contacts = []
    for cid, name, email, birthday, group, phones in rows:
        contacts.append({
            "id":       cid,
            "name":     name,
            "email":    email,
            "birthday": birthday,
            "group":    group,
            "phones":   phones if isinstance(phones, list) else [],
        })

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(contacts, f, ensure_ascii=False, indent=2)
    print(f"  ✓ Exported {len(contacts)} contacts → {filename}")



def import_json():
    filename = input("  JSON file path: ").strip()
    try:
        with open(filename, "r", encoding="utf-8") as f:
            contacts = json.load(f)
    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        return
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        return

    conn = connect()
    inserted = skipped = overwritten = 0

    for c in contacts:
        name     = c.get("name", "").strip()
        email    = c.get("email")
        birthday = c.get("birthday")
        group    = c.get("group")
        phones   = c.get("phones", [])  

        if not name:
            print("  ⚠ Skipping entry with no name.")
            continue

        with conn.cursor() as cur:
            cur.execute("SELECT id FROM contacts WHERE name = %s", (name,))
            existing = cur.fetchone()

            if existing:
                action = input(
                    f"  '{name}' already exists. [s]kip / [o]verwrite? "
                ).strip().lower()
                if action != "o":
                    skipped += 1
                    continue
             
                gid = get_or_create_group(cur, group) if group else None
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE name=%s",
                    (email, birthday, gid, name)
                )
                cid = existing[0]
  
                cur.execute("DELETE FROM phones WHERE contact_id=%s", (cid,))
                for p in phones:
                    cur.execute(
                        "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)",
                        (cid, p.get("phone"), p.get("type", "mobile"))
                    )
                overwritten += 1
            else:
                first_phone = phones[0].get("phone") if phones else "N/A"
                cur.execute("CALL upsert(%s, %s)", (name, first_phone))
                cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
                cid = cur.fetchone()[0]

                gid = get_or_create_group(cur, group) if group else None
                cur.execute(
                    "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE name=%s",
                    (email, birthday, gid, name)
                )
                for p in phones:
                    cur.execute(
                        "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)"
                        " ON CONFLICT DO NOTHING",
                        (cid, p.get("phone"), p.get("type", "mobile"))
                    )
                inserted += 1

        conn.commit()

    conn.close()
    print(f"  ✓ Done — inserted: {inserted}, overwritten: {overwritten}, skipped: {skipped}")

def import_csv_extended():
    filename = input("  CSV file path: ").strip()
    conn = connect()
    ok = errors = 0

    try:
        with open(filename, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                name     = row.get("name", "").strip()
                phone    = row.get("phone", "").strip()
                ptype    = row.get("type", "mobile").strip().lower()
                email    = row.get("email", "").strip() or None
                birthday = row.get("birthday", "").strip() or None
                group    = row.get("group", "").strip() or None

                if not name or not phone:
                    print(f"  ⚠ Skipping invalid row: {row}")
                    errors += 1
                    continue
                if ptype not in ("home", "work", "mobile"):
                    ptype = "mobile"

                with conn.cursor() as cur:
                    cur.execute("CALL upsert(%s, %s)", (name, phone))
                    gid = get_or_create_group(cur, group) if group else None
                    cur.execute(
                        "UPDATE contacts SET email=%s, birthday=%s, group_id=%s WHERE name=%s",
                        (email, birthday, gid, name)
                    )
                    cur.execute("SELECT id FROM contacts WHERE name=%s", (name,))
                    cid = cur.fetchone()[0]
                    cur.execute(
                        "INSERT INTO phones(contact_id, phone, type) VALUES(%s,%s,%s)"
                        " ON CONFLICT DO NOTHING",
                        (cid, phone, ptype)
                    )
                conn.commit()
                ok += 1

    except FileNotFoundError:
        print(f"  ✗ File not found: {filename}")
        conn.close()
        return

    conn.close()
    print(f"  ✓ CSV import done — {ok} imported, {errors} skipped.")

def main():
    setup_db()

    while True:
        print("""

 --- View ---                    
  1. Show all (sorted)           
  2. Paginated browse            
  3. Filter by group             
 --- Search ---                  
  4. Search (name/phone/email)   
  5. Search by email only        
 --- Add / Edit ---             
  6. Add contact (full)         
  7. Add extra phone to contact  
  8. Move contact to group       
 --- Import / Export ---         
  9. Import CSV (extended)       
 10. Export to JSON              
 11. Import from JSON            
 --- Exit ---                    
  0. Exit                        
""")

        choice = input("Choice: ").strip()

        if   choice == "1":  show_sorted()
        elif choice == "2":  paginated_browse()
        elif choice == "3":  filter_by_group()
        elif choice == "4":
            q = input("  Search query: ").strip()
            print_search_results(search_all(q))
        elif choice == "5":  search_by_email()
        elif choice == "6":  add_contact_console()
        elif choice == "7":  add_phone_to_contact()
        elif choice == "8":  move_contact_to_group()
        elif choice == "9":  import_csv_extended()
        elif choice == "10": export_json()
        elif choice == "11": import_json()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("  Invalid choice.")


if __name__ == "__main__":
    main()