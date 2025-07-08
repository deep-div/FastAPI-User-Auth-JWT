# FastAPI JWT Auth Project

This project is a FastAPI-based web application that demonstrates how to implement JWT (JSON Web Token) authentication. It provides a modular structure with support for user authentication, database management, and data validation using Pydantic and SQLAlchemy.

## Features

* JWT-based authentication (Bearer token)
* Modular and scalable codebase
* SQLAlchemy ORM for database interaction
* Pydantic models for request and response validation
* Jupyter notebook included for API testing
* Utility functions for common tasks

## Project Structure

```
app/
├── __init__.py           # Makes the directory a package
├── api_tester.ipynb      # Jupyter notebook for API testing
├── auth_bearer.py        # JWT token creation and verification
├── database.py           # Database session and engine setup
├── main.py               # Entry point for FastAPI app
├── models.py             # SQLAlchemy models
├── schemas.py            # Pydantic schemas
├── utils.py              # Utility/helper functions
.gitignore                # Git ignore rules
LICENSE                   # License file
README.md                 # Project documentation
```

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo-name.git
   cd your-repo-name
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:

   ```bash
   uvicorn app.main:app --reload
   ```

## API Testing

You can use the included `api_tester.ipynb` notebook to interact with the API endpoints and test token authentication flows.

Alternatively, you can use tools like Postman or HTTPie.

## Configuration

Environment variables for secrets (e.g., JWT secret keys) and database URLs should be added via a `.env` file or set manually.

## License

This project is licensed under the terms of the LICENSE file included in this repository.


