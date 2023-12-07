import ast
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
    distance, stroke = eval(selected_events)
    
    SQL1 = f"""
    SELECT swimmer_id
    FROM swimmers
    WHERE name = "{swimmer_name}"
    AND age = "{swimmer_age}"
"""

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL1)
        swimmer_id_result = db.fetchall()  # Fetch the result

    if swimmer_id_result:
        swimmer_id = swimmer_id_result[0][0]  # Access the first element of the first row
        print(f"Swimmer ID: {swimmer_id}")
    else:
        print("Swimmer not found.")
        
    print(swimmer_id)
        
    SQL2 = f"""
    SELECT event_id
    FROM events
    WHERE distance = "{distance}"
    AND event = "{stroke}"
    """
    
    with DBcm.UseDatabase(config) as db:
        db.execute(SQL2)
        event_id_result = db.fetchall()  # Fetch the result

    if event_id_result:
        event_id = event_id_result[0][0]  # Access the first element of the first row
        print(f"Event ID: {event_id}")
    else:
        print("Event not found.")

    SQL3 = f"""
    SELECT times
    FROM times
    WHERE swimmer_id = {swimmer_id}
    AND event_id = {event_id}
    """

    with DBcm.UseDatabase(config) as db:
        db.execute(SQL3)
        chart_data = db.fetchall()
        
    print(chart_data)
    
    time_values = [time_tuple[0] for time_tuple in chart_data]
    
    
    the_converts = [swim_utils.convert2hundreths(time) for time in time_values]
    
    from_max = max(the_converts) + 50
    
     # Calculate the average time
    average = sum(the_converts) / len(the_converts)
    average_time_string = swim_utils.build_time_string(average)

    time_values = list(reversed(time_values))
    the_converts = list(reversed(the_converts))

    data = [hfpy_utils.convert2range(n, 0, from_max, 0, 350) for n in the_converts]
    
    print (data)
    
    zipped_data = zip(the_converts, time_values)

    return render_template("chart.html", average = average_time_string, data = zipped_data, t=time_values, c=data)





if __name__ == "__main__":
    app.run(debug=True)