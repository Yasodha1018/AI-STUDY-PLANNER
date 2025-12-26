from flask import Flask, render_template, request
import math
import random

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/planner', methods=['POST'])
def planner():
    return render_template('planeer.html')

@app.route('/timetable', methods=['POST'])
def timetable():

    # 1️⃣ Read form data
    subjects = request.form.get('subjects')
    time_value = int(request.form.get('time_value'))
    time_unit = request.form.get('time_unit')
    allocation = request.form.get('allocation')

    # 2️⃣ Convert time into total hours
    if time_unit == 'hours':
        total_hours = time_value
    elif time_unit == 'days':
        total_hours = time_value * 2   # 2 hrs/day
    else:  # months
        total_hours = time_value * 30 * 2

    # 3️⃣ Process subjects
    subject_list = [s.strip() for s in subjects.split(',') if s.strip()]
    num_subjects = len(subject_list)

    timetable = []

    # ================= AI LOGIC =================
    if allocation == "equal":
        per_subject = round(total_hours / num_subjects, 1)

        for s in subject_list:
            timetable.append({
                "subject": s,
                "hours": per_subject
            })

    else:
        # 🧠 AI MODE (Smart Allocation)
        weights = {}
        total_weight = 0

        # Assign random difficulty weight (AI decision)
        for s in subject_list:
            weight = random.uniform(1.0, 2.5)  # AI intelligence
            weights[s] = weight
            total_weight += weight

        remaining_hours = total_hours

        for i, s in enumerate(subject_list):
            hours = round((weights[s] / total_weight) * total_hours, 1)

            # Last subject gets remaining hours (perfect balance)
            if i == num_subjects - 1:
                hours = round(remaining_hours, 1)

            remaining_hours -= hours

            timetable.append({
                "subject": s,
                "hours": hours
            })

    # 5️⃣ Send to HTML
    return render_template(
        'timetable.html',
        timetable=timetable,
        total_hours=total_hours,
        allocation=allocation
    )
@app.route('/generate')
def generate():
    return render_template('planeer.html')
if __name__ == '__main__':
    app.run(debug=True)
