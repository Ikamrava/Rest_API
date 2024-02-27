from flask import Flask
import os
from dotenv import load_dotenv
import psycopg2
from flask import request
from datetime import datetime
from datetime import timezone





CREATE_ROOMS_TABLE = ("CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY,name TEXT);")
CREATE_TEMPS_TABLE = ("CREATE TABLE IF NOT EXISTS temps (room_id INTEGER, temp REAL,date TIMESTAMP,FOREIGN KEY(room_id) REFERENCES rooms(id) on DELETE CASCADE);")

    



load_dotenv()

app = Flask(__name__)
url = os.getenv("DATABASE_URL")
connection = psycopg2.connect(url)


@app.post("/api/room")
def create_room():
    data = request.get_json()
    name = data["name"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_ROOMS_TABLE)
            cursor.execute("INSERT INTO rooms (name) VALUES (%s) RETURNING id", (name,))
            room_id = cursor.fetchone()[0]
    return {"id": room_id,"message": f"Room {name} created"},201
    
@app.post("/api/temp")
def create_temp():
    data = request.get_json()
    room_id = data["room_id"]
    temp = data["temp"]
    try:
        date = datetime.strptime(data["date"], "%d-%m-%Y %H:%M:%S")
    except KeyError:
        date = datetime.now(timezone.utc)
        
  
    with connection:
        with connection.cursor() as cursor:
                cursor.execute(CREATE_TEMPS_TABLE)
                cursor.execute("INSERT INTO temps (room_id, temp, date) VALUES (%s, %s, %s)", (room_id, temp, date))
    return {"message": f"Temperature {temp} recorded for room {room_id}"},201



@app.get("/api/average")
def get_average():
    data = request.get_json()
    room_id = data["room_id"]
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT AVG(temp) FROM temps WHERE room_id = %s", (room_id, ))
            average = cursor.fetchone()[0]
            days = cursor.execute("SELECT COUNT(DISTINCT date) FROM temps WHERE room_id = %s", (room_id,))
            days = cursor.fetchone()[0]
    return {"average": round(average , 2),"days":days},200
      
