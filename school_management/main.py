import click
from .models.database import SessionLocal, engine, Base
from .models.student import Student # Ensure models are imported for Base.metadata
from .models.teacher import Teacher
from .models.course import Course

# Import the function to add student commands
from school_management.cli.student_cli import add_student_commands

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

@click.group()
def cli():
    """School Management System CLI"""
    pass

# Add commands to the CLI group
add_student_commands(cli)

if __name__ == '__main__':
    cli()
