# School Management System

This is a Django-based school management system.

## Prerequisites

- Python 3.x
- Django
- Other dependencies as defined in a potential `requirements.txt` (Note: we haven't explicitly created one for the Django project yet, but it's good practice).

## Project Structure

- The main Django project is located in the `school_management_system/` directory.
- `manage.py` is located at `school_management_system/manage.py`.

## Running the Development Server

This project includes helper scripts to simplify starting the development server. Ensure you have Python installed and have set up the project dependencies.

**For Windows users:**

1.  Navigate to the root directory of this repository in your file explorer.
2.  Double-click the `run_server.bat` file.
3.  This will open a command prompt window and start the Django development server.
4.  Access the application by opening your web browser and going to `http://127.0.0.1:8000/`.

**For macOS/Linux users:**

1.  Open your terminal and navigate to the root directory of this repository.
2.  Make the script executable (if you haven't already or if it lost permissions, e.g., after cloning):
    ```bash
    chmod +x run_server.sh
    ```
3.  Run the script:
    ```bash
    ./run_server.sh
    ```
4.  This will start the Django development server.
5.  Access the application by opening your web browser and going to `http://127.0.0.1:8000/`.

**Traditional Method (using command line):**

1.  Open your terminal or command prompt.
2.  Navigate to the Django project directory: `cd school_management_system`
3.  Run the server: `python manage.py runserver`

## Admin Panel

The Django admin panel can be accessed at `http://127.0.0.1:8000/admin/` once the server is running.
You will need to create a superuser first if you haven't:
```bash
# Navigate to school_management_system/ directory first
python manage.py createsuperuser
```
