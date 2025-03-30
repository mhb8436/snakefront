# Snakefront

Snakefront is a web-based interface for managing workflows and projects, built on top of Django. It provides functionality for creating, editing, and managing workflows and projects, as well as integrating with S3 storage and Git repositories.

## Features

- **Project Management**: Create, edit, and delete projects.
- **Workflow Management**: Create, edit, and delete workflows associated with projects.
- **S3 Integration**: Upload, download, and manage files in S3 storage.
- **Git Integration**: Fetch workflow source code from Git repositories.
- **User Authentication**: Secure access to features with user authentication.
- **Rate Limiting**: Optional rate limiting for views to prevent abuse.

## Installation

1. Clone the repository:
    ```bash
    git clone <repository-url>
    cd snakefront
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Configure the application:
    - Update `snakefront/settings.py` with your database, S3, and other configurations.

4. Apply migrations:
    ```bash
    python manage.py migrate
    ```

5. Run the development server:
    ```bash
    python manage.py runserver
    ```

6. Access the application at `http://127.0.0.1:8000`.

## Usage

### Projects

- **Create a Project**: Navigate to the "New Project" page and fill out the form.
- **Edit a Project**: Use the "Edit" button in the project list.
- **Delete a Project**: Use the "Delete" button in the project list.

### Workflows

- **Create a Workflow**: Navigate to the "New Workflow" page, select a project, and configure the workflow.
- **Edit a Workflow**: Use the "Edit" button in the workflow list.
- **Delete a Workflow**: Use the "Delete" button in the workflow list.

### S3 Integration

- Upload and manage files in S3 storage using the S3 browser interface.

### Git Integration

- Fetch workflow source code from Git repositories during workflow creation or editing.

## Code Structure

- **`main/`**: Contains views, templates, and logic for workflows and dashboard.
- **`project/`**: Handles project-related views, templates, and forms.
- **`s3browser/`**: Manages S3 file operations like upload, download, and folder creation.
- **`api/`**: Provides utility functions and API endpoints for workflows and projects.
- **`base/static/css/`**: Contains CSS files for styling the application.

## Key Files

- `main/views.py`: Core logic for workflows and dashboard.
- `project/views.py`: Logic for project management.
- `s3browser/views.py`: S3 file operations.
- `main/templates/`: HTML templates for the application.
- `base/static/css/`: CSS files for styling.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Commit your changes and push to your fork.
4. Submit a pull request.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- Built with Django and Bootstrap.
- Inspired by Snakemake for workflow management.

For more details, refer to the source code and comments within the project.  