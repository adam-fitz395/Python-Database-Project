from flask import Flask, render_template, request, session  # from module import Class.
import DBcm

import os
import hfpy_utils
import swim_utils

config = {
    "user": "swimuser",
    "password": "swimuserpasswd",
    "database": "swimmer_database",
    "host": "localhost",
}

app = Flask(__name__)

app.secret_key = os.urandom(12)


@app.get("/base")
def base():
    sample_title = "Training Session Select"
    return render_template("base.html", title=sample_title)

@app.route("/", methods=["GET", "POST"])
@app.route("/select", methods=["GET", "POST"])
def get_timestamp():
    SQL = """
    SELECT DISTINCT DATE(ts) AS date_only
    FROM times"""
    
    with DBcm.UseDatabase(config) as db:
            db.execute(SQL)
            timestamps = [row[0] for row in db.fetchall()]
    return render_template("select.html", timestamps = timestamps)
            
@app.route("/swimmer", methods=["GET", "POST"])
def get_swimmers():
    global selected_timestamp
    selected_timestamp = request.form.get("timestamp")

    SQL = """
    SELECT DISTINCT s.name, s.age
    FROM swimmers s
    JOIN times t ON s.swimmer_id = t.swimmer_id
    WHERE DATE(t.ts) = DATE(%s)
    """

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL, (selected_timestamp,))
        swimmers_info = db.fetchall()

    return render_template("swimmer.html", swimmers = swimmers_info)

@app.route("/event", methods=["GET", "POST"])
def get_event():
    selected_swimmer_details = request.form.get("swimmer")

    # Assuming selected_swimmer_details is in the format "Name, Age"
    global swimmer_name, swimmer_age
    swimmer_name, swimmer_age = eval(selected_swimmer_details)
    swimmer_name.strip()
    
    print(swimmer_name)
    

    SQL = """
    SELECT DISTINCT e.distance, e.event
    FROM events e
    JOIN times t ON e.event_id = t.event_id
    JOIN swimmers s ON t.swimmer_id = s.swimmer_id
    WHERE DATE(t.ts) = DATE(%s) AND s.name = %s AND s.age = %s
    """

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL, (selected_timestamp, swimmer_name, swimmer_age))
        events_info = db.fetchall()

    print (events_info)
    return render_template("event.html", events=events_info)

@app.route("/chart", methods=["GET", "POST"])
def display_chart():
    selected_events = request.form.get("event")
    
    global distance, stroke
    distance, stroke = eval(selected_events)
    print(distance)
    print(stroke)
    
    SQL = """
    SELECT times
    FROM times
    JOIN events ON times.event_id = events.event_id
    JOIN swimmers ON times.swimmer_id = swimmers.swimmer_id
    WHERE DATE(times.ts) = DATE(%s)
    """
    
    with DBcm.UseDatabase(config) as db:
        db.execute(SQL, (selected_timestamp,))
        chart_data = db.fetchall()
    print(chart_data)



if __name__ == "__main__":
    app.run(debug=True)