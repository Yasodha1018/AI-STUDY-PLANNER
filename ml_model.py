import random
from datetime import datetime, timedelta

def generate_study_plan(subjects, hours_per_day, study_period,
                        equal_time, difficulty,
                        preference, exam_mode, include_breaks):

    total_days = int(study_period.split()[0])
    subjects_list = []

    for s in subjects:
        subjects_list.append({
            'name': s,
            'difficulty': difficulty.get(s, 'medium'),
            'daily_hours': round(hours_per_day / len(subjects), 2)
        })

    schedule = []
    start_date = datetime.now()

    for day in range(1, min(7, total_days) + 1):
        daily_subjects = subjects_list.copy()
        random.shuffle(daily_subjects)

        current_hour = random.choice([7, 8, 9, 10])

        day_plan = {
            'day': day,
            'date': (start_date + timedelta(days=day-1)).strftime('%Y-%m-%d'),
            'slots': []
        }

        for subject in daily_subjects:
            day_plan['slots'].append({
                'subject': subject['name'],
                'start_time': f"{current_hour}:00",
                'duration': subject['daily_hours']
            })

            current_hour += subject['daily_hours']

            if include_breaks and random.random() > 0.6:
                day_plan['slots'].append({
                    'activity': 'Break',
                    'duration': 0.5,
                    'type': 'break'
                })
                current_hour += 0.5

        schedule.append(day_plan)

    return {
        'total_days': total_days,
        'daily_hours': hours_per_day,
        'subjects': subjects_list,
        'schedule': schedule
    }
