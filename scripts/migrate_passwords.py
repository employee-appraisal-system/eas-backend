from database.connection import SessionLocal
from models.employee import Employee
from services.password_utils import hash_password


def migrate_passwords():

    db = SessionLocal()

    employees = db.query(Employee).all()

    for employee in employees:

        if employee.password.startswith("$argon2"):
            continue

        employee.password = hash_password(employee.password)

    db.commit()

    db.close()

    print("Password migration completed")


if __name__ == "__main__":
    migrate_passwords()
