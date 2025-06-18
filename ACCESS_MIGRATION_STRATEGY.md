### Data Migration Strategy: Access DB to Django Application

**1. Overview and Objectives:**
    *   Goal: Migrate data from the legacy Access DB to the new system.
    *   Identify key data entities to be migrated (e.g., students, teachers, representatives, academic records, financial information if applicable and in scope for this initial migration).

**2. Prerequisites & Tools:**
    *   **Access Database File:** Availability of the `.mdb` or `.accdb` file.
    *   **Connectivity:**
        *   Python: `pyodbc` library (or `pypyodbc`) for connecting to Access via ODBC drivers.
        *   Ensure appropriate ODBC drivers for Access are installed on the machine running the migration scripts.
    *   **Data Manipulation:**
        *   `pandas` library for efficient data handling, transformation, and mapping.
    *   **Django ORM:** For loading data into the new application's database.

**3. Migration Process (ETL - Extract, Transform, Load):**

    *   **3.1. Extraction:**
        *   Establish a connection to the Access database using `pyodbc`.
        *   Identify all relevant tables in the Access DB.
        *   Extract data from these tables into pandas DataFrames.
        *   Handle potential encoding issues if any.

    *   **3.2. Transformation & Mapping:**
        *   **User Data (Students, Teachers, Parents, Admin):**
            *   Map Access user table(s) fields (e.g., `FirstName`, `LastName`, `Email`, `Role_Legacy`) to Django `User` model fields (`first_name`, `last_name`, `email`, `username`, `password`, `role`).
            *   Generate unique usernames if not present or suitable.
            *   Handle password migration: Since passwords are likely hashed in Access (or should be), it's generally not possible to migrate them directly. Plan to generate temporary passwords and notify users to reset them, or set a default password.
            *   Map legacy roles to the new `User.role` choices.
        *   **Academic Structure (Levels, Years/Grades, Sections, Subjects):**
            *   Map corresponding Access tables to `Level`, `AcademicYear`, `Section`, `Subject` Django models.
            *   Recreate relationships (e.g., `AcademicYear` to `Level`).
        *   **Enrollment Data:**
            *   Map Access enrollment records to the `StudentEnrollment` model, linking to the newly created `User` (student), `Section`, and `AcademicPeriod` records.
            *   Carefully manage foreign key relationships. It might be necessary to store a mapping of old Access IDs to new Django object IDs during the migration.
        *   **Subject Assignments & Academic Periods:**
            *   Map to `SubjectAssignment` and `AcademicPeriod` models.
        *   **Data Cleaning:**
            *   Identify and handle inconsistencies, missing data, or formatting issues.
            *   Validate data against new model constraints (e.g., data types, choices).

    *   **3.3. Loading:**
        *   Write Python scripts that use the Django ORM (`YourModel.objects.create()` or `YourModel.objects.bulk_create()` for efficiency).
        *   Load data in a specific order to respect dependencies (e.g., Users and Levels first, then AcademicYears, then Sections, then Enrollments).
        *   **Error Handling:** Implement robust error logging for records that fail to migrate.
        *   **Idempotency:** Design scripts to be re-runnable if possible (e.g., by checking if a record already exists based on a unique identifier from the old system, or by clearing related tables before a run – use with caution). A common strategy is to store the old Access ID in a new, temporary field on the Django models during migration.

**4. Pre-Migration & Post-Migration Steps:**
    *   **Pre-Migration:**
        *   Backup the Access database.
        *   Backup the (empty or existing) Django database.
        *   Thoroughly analyze the Access DB schema. Document all tables, fields, data types, and relationships.
    *   **Post-Migration:**
        *   **Data Validation:**
            *   Compare record counts between Access tables and Django models.
            *   Spot-check individual records.
            *   Verify relationships (e.g., are students correctly enrolled in their sections?).
        *   **Testing:** Perform thorough testing of the application with migrated data.

**5. Potential Challenges & Mitigation:**
    *   **Schema Mismatches:** Differences in table structure, field names, data types. (Mitigation: Careful mapping, transformation scripts).
    *   **Data Inconsistencies:** Dirty data in the Access DB. (Mitigation: Data cleaning scripts, manual intervention for complex cases).
    *   **Relationship Complexity:** Complex joins or relationship logic in Access. (Mitigation: Careful planning of data loading order, mapping tables for old to new IDs).
    *   **Volume of Data:** Large datasets might require performance optimization for scripts (e.g., `bulk_create`, disabling signals during import).
    *   **Character Encoding:** Ensure consistent encoding between Access and the new system.

**6. Phased Approach (Recommended for complex migrations):**
    *   Consider migrating data in phases (e.g., core academic structure first, then users, then enrollments).
    *   Test each phase thoroughly.

**7. Migration Scripts - General Structure (Conceptual):**
    *   `config.py`: Database connection details (ensure this is not committed with sensitive info).
    *   `extract.py`: Functions to connect and pull data from Access into DataFrames.
    *   `transform_users.py`, `transform_academic.py`, etc.: Modules for specific data transformations.
    *   `load.py`: Main script orchestrating the ETL process, calling Django ORM.
    *   `utils.py`: Helper functions (e.g., ID mapping).

This document provides a strategic outline. The actual migration scripts will require detailed implementation based on the specific structure of the Access database.
