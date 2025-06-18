import click
# print("DEBUG: student_cli.py is being loaded") # DEBUG - Removing this now
from school_management.models.database import SessionLocal
from school_management.models.student import Student

def add_student_commands(cli_group):
    @cli_group.command("add-student")
    @click.option('--first-name', prompt="First name", help="The student's first name.")
    @click.option('--last-name', prompt="Last name", help="The student's last name.")
    @click.option('--email', prompt="Email", help="The student's email address.")
    def add_student(first_name, last_name, email):
        """Adds a new student to the database."""
        db = SessionLocal()
        try:
            existing_student = db.query(Student).filter(Student.email == email).first()
            if existing_student:
                click.echo(f"Error: Student with email {email} already exists.")
                return

            student = Student(first_name=first_name, last_name=last_name, email=email)
            db.add(student)
            db.commit()
            db.refresh(student)
            click.echo(f"Student {student.first_name} {student.last_name} (ID: {student.id}) added successfully.")
        except Exception as e:
            db.rollback()
            click.echo(f"Error adding student: {e}")
        finally:
            db.close()

    @cli_group.command("list-students")
    def list_students():
        """Lists all students."""
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            if not students:
                click.echo("No students found.")
                return
            click.echo("Students:")
            for student in students:
                click.echo(f"- ID: {student.id}, Name: {student.first_name} {student.last_name}, Email: {student.email}, Status: {student.account_status}")
        finally:
            db.close()

    @cli_group.command("view-student")
    @click.argument('student_id', type=int)
    def view_student(student_id):
        """Displays details for a specific student by ID."""
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                click.echo(f"Student Details (ID: {student.id}):")
                click.echo(f"  First Name: {student.first_name}")
                click.echo(f"  Last Name: {student.last_name}")
                click.echo(f"  Email: {student.email}")
                click.echo(f"  Account Status: {student.account_status}")
            else:
                click.echo(f"Error: Student with ID {student_id} not found.")
        finally:
            db.close()
