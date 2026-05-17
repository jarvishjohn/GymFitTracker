import psycopg2
from fastapi import FastAPI
from pydantic import BaseModel

class user(BaseModel):
    name: str
    email: str

class workout_session(BaseModel):
    user_id: int
    duration_minutes: int

class exercise_logs(BaseModel):
    workout_id: int
    exercise_id: int

class set(BaseModel):
    exercise_log_id: int
    sets: int
    reps: int
    weight: float

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
def create_user(u:user):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO users (name,email) VALUES (%s,%s) RETURNING id", (u.name, u.email))
        user_id = cur.fetchone()[0]
        c.commit()
        return {"data":u}
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post("/workout-session")
def workout_session(ws:workout_session):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO workout_sessions (user_id,workout_date,duration_minutes) VALUES (%s,CURRENT_DATE,%s) RETURNING id", (ws.user_id, ws.duration_minutes))
        workout_id = cur.fetchone()[0]
        c.commit()
        return {"data":ws }
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post('/exercise-logs')
def exercise_logs(els:exercise_logs):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("INSERT INTO exercise_logs (workout_id,exercise_id) VALUES (%s,%s) RETURNING id", (els.workout_id,els.exercise_id))
        exercise_log_id = cur.fetchone()[0]
        c.commit()
        return {"data":els}
    except Exception as e:
        c.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        c.close()


@app.post("/setreps")
def set_reps(s:set):
    c = get_conn()
    cur = c.cursor()
    try:
        cur.execute("SELECT MAX(sl.weight) FROM set_log sl JOIN exercise_logs el ON el.id=sl.exercise_log_id WHERE el.exercise_id=(SELECT exercise_id FROM exercise_logs WHERE id=%s)", (s.exercise_log_id,))
        max_weight = cur.fetchone()[0]
        is_pr = False
        if max_weight is None or s.weight > max_weight:
            is_pr = True
        cur.execute("INSERT INTO set_log (exercise_log_id,set_number,reps,weight) VALUES (%s,%s,%s,%s) RETURNING id", (s.exercise_log_id, s.sets, s.reps, s.weight))
        set_id = cur.fetchone()[0]
        c.commit()
        return {"data": set}
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
        cur.execute("SELECT e.exercise,el.exercise_id,sl.set_number,sl.reps,sl.weight FROM exercise e LEFT JOIN exercise_logs el ON el.exercise_id=e.id LEFT JOIN set_log sl ON sl.exercise_log_id=el.id")
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
        cur.execute("DELETE FROM USERS WHERE username=%s",(name,))
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

@app.delete('/delete_workoutses')
def delete_ws(id:int):
    c=get_conn()
    cur=c.cursor()
    try:
        cur.execute("DELETE FROM workout_sessions WHERE id = %s",(id,))
        c.commit()
        if cur.rowcount==0:
            return{"error":"Workout Session Doesnt exist"}
        return{"message":"workout session successfully deleted"}
    except Exception as e:
        c.rollback()
        return{"error":str(e)}
    finally:
        cur.close()
        c.close()