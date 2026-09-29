# Workout Tracker API

A simple **Workout Tracker REST API** built using **FastAPI** and **PostgreSQL**.

This project is mainly focused on learning how a backend API communicates with a PostgreSQL database. It allows users to create workout sessions, log exercises and sets, view workout information, and delete users or workout sessions.

## Tech Stack

* **Python**
* **FastAPI** – Used to build the REST API
* **Pydantic** – Used for validating request data
* **PostgreSQL** – Database
* **Psycopg2** – Connects Python with PostgreSQL

## How the Project Works

The basic flow is:

```text
Client
  ↓
FastAPI
  ↓
Pydantic Validation
  ↓
Psycopg2
  ↓
PostgreSQL
```

The API receives data from the client, validates it using Pydantic models, and then uses `psycopg2` to perform SQL operations on the PostgreSQL database.

## Database Structure

The API works with tables such as:

* `users`
* `workout_sessions`
* `exercise_logs`
* `set_log`
* `exercise`

The relationships are roughly:

```text
User
 ↓
Workout Session
 ↓
Exercise Log
 ↓
Set Log
```

## Pydantic Models

### User

Used when creating a user.

```python
class user(BaseModel):
    name: str
    email: str
```

### Workout Session

Stores the user associated with a workout and its duration.

```python
class workout_session(BaseModel):
    user_id: int
    duration_minutes: int
```

### Exercise Log

Connects an exercise to a particular workout session.

```python
class exercise_logs(BaseModel):
    workout_id: int
    exercise_id: int
```

### Set

Stores information about individual sets performed for an exercise.

```python
class set(BaseModel):
    exercise_log_id: int
    sets: int
    reps: int
    weight: float
```

## API Endpoints

### Create User

**POST `/session`**

Creates a new user in the `users` table.

Example request:

```json
{
    "name": "John",
    "email": "john@example.com"
}
```

---

### Create Workout Session

**POST `/workout-session`**

Creates a workout session for an existing user.

Example:

```json
{
    "user_id": 1,
    "duration_minutes": 75
}
```

The workout date is automatically set to the current date using PostgreSQL's `CURRENT_DATE`.

---

### Add Exercise Log

**POST `/exercise-logs`**

Adds an exercise to a workout session.

Example:

```json
{
    "workout_id": 1,
    "exercise_id": 3
}
```

---

### Add Set/Reps

**POST `/setreps`**

Stores the number of sets, reps, and weight used for an exercise.

Example:

```json
{
    "exercise_log_id": 1,
    "sets": 3,
    "reps": 10,
    "weight": 60
}
```

The endpoint also checks the previous maximum weight for that exercise and determines whether the current weight is a new personal record.

---

### Get Exercise Session Logs

**GET `/exercise-session-logs`**

Returns exercise logs along with the workout date and workout duration.

Example response:

```json
{
    "data": [
        {
            "id": 1,
            "date": "2026-09-29",
            "duration": 75
        }
    ]
}
```

---

### Get Exercise Details

**GET `/onclick_esl`**

Returns exercise information along with the logged sets, reps, and weights.

Example response:

```json
{
    "data": [
        {
            "exercise": "Bench Press",
            "exercise_id": 1,
            "set_number": 1,
            "reps": 10,
            "weight": 60
        }
    ]
}
```

---

### Delete User

**DELETE `/delete`**

Deletes a user using their name.

Example:

```text
/delete?name=John
```

If the user does not exist, the API returns an error message.

---

### Delete Workout Session

**DELETE `/delete_workoutses`**

Deletes a workout session using its ID.

Example:

```text
/delete_workoutses?id=1
```

## Running the Project

### 1. Install the required packages

```bash
pip install fastapi uvicorn psycopg2-binary pydantic
```

### 2. Make sure PostgreSQL is running

Create a PostgreSQL database and make sure the credentials in the Python file match your local PostgreSQL setup.

### 3. Start the FastAPI server

If the Python file is named `main.py`:

```bash
uvicorn main:app --reload
```

The API will normally be available at:

```text
http://127.0.0.1:8000
```

## API Documentation

FastAPI automatically generates interactive API documentation.

Open:

```text
http://127.0.0.1:8000/docs
```

You can use this page to test the API endpoints without needing Postman.

## Error Handling

The database operations are wrapped in `try/except/finally` blocks.

If an SQL operation fails:

1. The transaction is rolled back.
2. The error is returned to the client.
3. The cursor and database connection are closed.

For example:

```python
except Exception as e:
    c.rollback()
    return {"error": str(e)}
finally:
    cur.close()
    c.close()
```

## Important Note

For a real project, the PostgreSQL password should **not** be written directly inside the Python source code.

Instead of:

```python
password='your_password'
```

it would be better to use environment variables or a `.env` file.

Also, the database credentials should never be committed to GitHub.

## Project Purpose

This project was built to understand the basics of:

* Building REST APIs with FastAPI
* Validating API requests with Pydantic
* Connecting Python applications to PostgreSQL
* Executing SQL queries from Python
* Using database transactions
* Creating, reading, and deleting database records
* Connecting different database tables using SQL joins
* Handling API and database errors

