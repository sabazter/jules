import click
# print("DEBUG: student_cli.py is being loaded") # DEBUG - Removing this now
from school_management.models.database import SessionLocal
from school_management.models.student import Student

def add_student_commands(cli_group):
    @cli_group.command("add-student")
    @click.option('--first-name', prompt="Nombre", help="El nombre del estudiante.")
    @click.option('--last-name', prompt="Apellido", help="El apellido del estudiante.")
    @click.option('--email', prompt="Correo electrónico", help="La dirección de correo electrónico del estudiante.")
    def add_student(first_name, last_name, email):
        """Agrega un nuevo estudiante a la base de datos."""
        db = SessionLocal()
        try:
            existing_student = db.query(Student).filter(Student.email == email).first()
            if existing_student:
                click.echo(f"Error: El estudiante con el correo electrónico {email} ya existe.")
                return

            student = Student(first_name=first_name, last_name=last_name, email=email)
            db.add(student)
            db.commit()
            db.refresh(student)
            click.echo(f"Estudiante {student.first_name} {student.last_name} (ID: {student.id}) agregado exitosamente.")
        except Exception as e:
            db.rollback()
            click.echo(f"Error al agregar estudiante: {e}")
        finally:
            db.close()

    @cli_group.command("list-students")
    def list_students():
        """Lista todos los estudiantes."""
        db = SessionLocal()
        try:
            students = db.query(Student).all()
            if not students:
                click.echo("No se encontraron estudiantes.")
                return
            click.echo("Estudiantes:")
            for student in students:
                click.echo(f"- ID: {student.id}, Nombre: {student.first_name} {student.last_name}, Correo electrónico: {student.email}, Estado: {student.account_status}")
        finally:
            db.close()

    @cli_group.command("view-student")
    @click.argument('student_id', type=int)
    def view_student(student_id):
        """Muestra los detalles de un estudiante específico por ID."""
        db = SessionLocal()
        try:
            student = db.query(Student).filter(Student.id == student_id).first()
            if student:
                click.echo(f"Detalles del estudiante (ID: {student.id}):")
                click.echo(f"  Nombre: {student.first_name}")
                click.echo(f"  Apellido: {student.last_name}")
                click.echo(f"  Correo electrónico: {student.email}")
                click.echo(f"  Estado de la cuenta: {student.account_status}")
            else:
                click.echo(f"Error: No se encontró el estudiante con ID {student_id}.")
        finally:
            db.close()
