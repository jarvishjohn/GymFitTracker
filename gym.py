import psycopg2
from fastapi import FastAPI

app = FastAPI()

def get_conn():
    return psycopg2.connect(
        host='localhost',
        database='mydb',
        user='postgres',
        password='jonah@1709',
        port=5432
    )


@app.post("/session")
def create_user(name: str, email: str):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO users (name,email) VALUES (%s,%s) RETURNING id", (name, email))
        user_id = cur.fetchone()[0]
        c.commit()
        return {"data": {"user_id": user_id}}
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post("/workout-session")
def workout_session(user_id: int, duration_minutes: int):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO workout_sessions (user_id,workout_date,duration_minutes) VALUES (%s,CURRENT_DATE,%s) RETURNING id", (user_id, duration_minutes))
        workout_id = cur.fetchone()[0]
        c.commit()
        return {"data": {"workout_id": workout_id}}
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post('/exercise-logs')
def exercise_logs(workout_id: int, exercise_id: int):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO exercise_logs (workout_id,exercise_id) VALUES (%s,%s) RETURNING id", (workout_id, exercise_id))
        exercise_log_id = cur.fetchone()[0]
        c.commit()
        return {"data": {"exercise_log_id": exercise_log_id}}
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post("/setreps")
def set_reps(exercise_log_id: int, sets: int, reps: int, weight: float):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("""
            SELECT MAX(sl.weight)
            FROM set_logs sl
            JOIN exercise_logs el ON el.id = sl.exercise_log_id
            WHERE el.exercise_id = (
                SELECT exercise_id FROM exercise_logs WHERE id = %s
            )
        """, (exercise_log_id,))

        row = cur.fetchone()
        max_weight = row[0] if row else None  

        is_pr = False
        if max_weight is None or weight > max_weight:
            is_pr = True

        cur.execute("""
            INSERT INTO set_logs (exercise_log_id, set_number, reps, weight)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """, (exercise_log_id, sets, reps, weight))

        set_id = cur.fetchone()[0]
        c.commit()

        return {"data": {"set_id": set_id, "is_pr": is_pr}}

    except Exception as e:
        c.rollback()
        return {"error": str(e)}

    finally:
        cur.close()
        c.close()

@app.get("/exercise-session-logs")
def exercise_session_logs():
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("SELECT el.id,ws.workout_date,ws.duration_minutes FROM exercise_logs el JOIN workout_sessions ws ON ws.id=el.workout_id")
        rows = cur.fetchall()
        return {"data": [{"id": r[0], "date": str(r[1]), "duration": r[2]} for r in rows]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.get("/onclick_esl")
def onclick_esl():
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("""
SELECT e.name, el.exercise_id, sl.set_number, sl.reps, sl.weight
FROM exercises e
LEFT JOIN exercise_logs el ON el.exercise_id = e.id
LEFT JOIN set_logs sl ON sl.exercise_log_id = el.id
""")
        rows = cur.fetchall()
        return {"data": [{"exercise": r[0], "exercise_id": r[1], "set_number": r[2], "reps": r[3], "weight": r[4]} for r in rows]}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()

@app.delete('/delete')
def delete_user(name:str):
    c=get_conn()
    cur = c.cursor()
    try:
        cur.execute("DELETE FROM USERS WHERE name=%s",(name,))
        c.commit()
        if cur.rowcount==0:
            return{"error":"User doesnt exist"}
        return{"message":"User deleted successfully"}
    except Exception as e:
        c.rollback()
        return{"error":str(e)}
    finally:
        cur.close()
        c.close()