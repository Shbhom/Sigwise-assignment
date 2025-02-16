# Sigwise Event Trigger Platform 
[live-demo](https://sigwise-assignment.onrender.com/)

## Overview

The **Sigwise Event Trigger Platform** is a backend application that allows customers to create and manage event triggers. Triggers can be either **scheduled** (firing at a specified time or interval) or **API** (triggered by an external API call). When a trigger fires, an event is logged and the system automatically manages these logs: events remain active for 2 hours, are then archived for 46 additional hours, and finally are deleted after a total of 48 hours. The application also includes JWT-based authentication so that only registered users can create, view, or manage their triggers.

test creds for live demo:
```
    email test@test.in
    password: 12345678
```
---

## Tech Stack

The application is built entirely using Python and relies on the following key packages:

- **FastAPI:**  
  Provides a fast and easy-to-use framework for building RESTful APIs with asynchronous support, automatic Swagger documentation, and dependency injection.

- **SQLModel:**  
  An ORM built on top of SQLAlchemy and Pydantic. It is used for defining models and handling database interactions in a type-safe manner.

- **APScheduler:**  
  Used to schedule background jobs for automated log archiving and cleanup. Its ease of integration made it the first choice for handling scheduled triggers.

- **python-jose:**  
  Handles JSON Web Token (JWT) encoding and decoding for secure authentication. It ensures that tokens are created and validated according to industry standards.

- **psycopg2:**  
  The PostgreSQL database adapter for Python, enabling connectivity and operations with a PostgreSQL database.

- **Jinja2:**  
  Used by FastAPI for rendering HTML templates for the UI.

- **Docker:**  
  Although not a Python package, Docker is used to containerize the application so that it can run reliably on any system without additional setup.

---

## API Endpoints

### Authentication Endpoints (`/auth`)

- **GET /auth/login:**  
  Renders a login page with fields for email and password.

- **POST /auth/login:**  
  Processes login credentials. On successful authentication, a JWT is created and stored in an HTTP-only cookie.

- **GET /auth/register:**  
  Renders a registration page with fields for email and password.

- **POST /auth/register:**  
  Processes registration data, creates a new user in the database, and sets a JWT cookie.

- **GET /logout:**  
  Clears the JWT cookie and redirects the user to the login page.

### Trigger Endpoints (`/api/v1/triggers`)

- **POST /api/v1/triggers:**  
  Creates a new trigger.  
  - Input: A JSON body matching the `TriggerCreate` model (fields: type, structured schedule_details, api_payload, expires_at, is_test).  
  - Authentication: Requires a valid JWT. The created trigger is associated with the current user (owner_id).  
  - Behavior: For scheduled triggers, it validates that the run_at value (inside schedule_details) is in the future. If `is_test` is true, a test event is logged immediately; otherwise, APScheduler is used to schedule the trigger.

- **GET /api/v1/triggers:**  
  Returns all triggers for the authenticated user.

- **GET /api/v1/triggers/triggers_html:**  
  Renders an HTML table of triggers for the current user via a Jinja2 template.

- **GET /api/v1/triggers/{trigger_id}:**  
  Returns a specific trigger by its ID (only if it belongs to the authenticated user).

- **PUT /api/v1/triggers/{trigger_id}:**  
  Updates a specific trigger (only if it belongs to the authenticated user).

- **DELETE /api/v1/triggers/{trigger_id}:**  
  Deletes a specific trigger (only if it belongs to the authenticated user).

- **POST /api/v1/triggers/{trigger_id}/test:**  
  Manually fires a test event for the specified trigger.

- **POST /api/v1/triggers/{trigger_id}/fire:**  
  Fires an API trigger by accepting a JSON payload (only applicable for API triggers and only if the trigger is owned by the authenticated user).

### Event Log Endpoints (`/api/v1/event_logs`)

- **GET /api/v1/event_logs:**  
  Returns event logs (as JSON) filtered by a status query parameter (`active`, `archived`, or `all`), showing only logs related to triggers owned by the authenticated user.

- **GET /api/v1/event_logs/event_logs_html:**  
  Renders an HTML table of event logs via a Jinja2 template.

- **GET /api/v1/event_logs/aggregated:**  
  Returns aggregated event log counts per trigger for events from the last 48 hours.

---

## Background Jobs

### APScheduler Jobs

- **archive_old_logs:**  
  Runs at regular intervals to update event logs. Events that were created more than 2 hours ago (in IST) and are still marked as **ACTIVE** are updated to **ARCHIVED**.

- **cleanup_archived_logs:**  
  Also runs at regular intervals to delete event logs. Any log that has been in the database for more than 48 hours is removed from the database.

Both jobs are configured to use IST (Indian Standard Time) for scheduling.

---

## Local Setup Instructions

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/sigwise-assignment.git
   cd sigwise-assignment
   ```

2. **Configuration:**
   - Update `.env` with your PostgreSQL connection string (e.g., `"postgresql://user:password@localhost/dbname"`) and JWT-related settings (e.g., `JWT_SECRET`).
   
3. **Build and Run with Docker:**
   - Build the Docker image:
     ```bash
     docker build -t sigwise-app .
     ```
   - Run the container:
     ```bash
     docker run -p 8000:8000 sigwise-app
     ```
   - This will start the FastAPI application on port 8000.

4. **Access the Application:**
   - Open your browser and go to `http://127.0.0.1:8000`.
   - If not logged in, you'll be redirected to the login page at `/auth/login`.
   - Use the login or registration pages to authenticate.

5. **Swagger Documentation:**
   - Visit `http://127.0.0.1:8000/docs` to view automatically generated API documentation.

---

## Prominent Tools & Packages Used

- **FastAPI:**  
  Used for its ease of setting up a fully asynchronous API with automatic Swagger UI generation and dependency injection patterns.

- **SQLModel:**  
  Provides an ORM layer with model validation and seamless integration with SQLAlchemy and Pydantic.

- **APScheduler:**  
  Handles background task scheduling for trigger execution and log management.

- **Neovim (nvim):**
  It's lightweight, highly configurable, and perfectly suited for my workflow, real reason is I'm a linux neckbeard, I user Arch BTW!!

- **ChatGPT:**
  ChatGPT served as a senior developer mentor for resolving doubts and suggesting improvements when I encountered challenges. Although it doesn't always generate perfect code, it helped me find solutions and verify best practices, also it can write decent docs :) .

- **DuckDuckGo:**
  I used DuckDuckGo for quick, privacy-respecting searches on best practices and troubleshooting tips when setting up the various components of the stack, and I love its bangs.
