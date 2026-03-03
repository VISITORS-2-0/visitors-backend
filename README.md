# Visitors Backend

This repository contains the backend service for the Visitors application. It is built using FastAPI.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. **Clone the repository** (if you haven't already) and navigate to the project directory:
   ```bash
   cd visitors-backend
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On **Windows**:
     ```bash
     venv\Scripts\activate
     ```
   - On **macOS / Linux**:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Note: The server requires `uvicorn` and `fastapi` to run. If they are not included in your `requirements.txt`, you can install them manually by running: `pip install fastapi uvicorn`)*

## Running the Application

To start the development server, run the following command from the root of the project:

```bash
uvicorn app.main:app --reload --port 8000
```

- `--reload`: Enables hot-reloading so the server restarts automatically when you make code changes.
- `--port 8000`: Runs the application on port 8000.

Once the server is running, the API will be accessible at:  
**http://localhost:8000**

Interactive API documentation (Swagger UI) is automatically generated and can be accessed at:  
**http://localhost:8000/docs**
