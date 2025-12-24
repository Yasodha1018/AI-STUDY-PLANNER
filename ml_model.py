"""
Simple ML model for study plan generation
"""
from datetime import datetime, timedelta
import random

def generate_study_plan(subjects, hours_per_day, study_period, equal_time, 
                       difficulty, preference, exam_mode, include_breaks):
    """
    Generate a study plan
    """
    # Parse study period
    if 'day' in study_period.lower():
        total_days = int(study_period.split()[0])
    elif 'month' in study_period.lower():
        total_days = int(study_period.split()[0]) * 30
    else:
        total_days = 30
    
    # Process subjects
    subjects_list = []
    for subj in subjects:
        subj = subj.strip()
        diff = difficulty.get(subj, 'medium')
        
        # Calculate hours per subject
        if equal_time:
            daily_hours = hours_per_day / len(subjects)
        else:
            # Weight based on difficulty
            if diff == 'hard':
                weight = 3
            elif diff == 'medium':
                weight = 2
            else:
                weight = 1
            
            # Adjust for preference
            if preference == 'subject_important' and subjects.index(subj) == 0:
                weight *= 1.5
            
            total_weight = sum([3 if difficulty.get(s, 'medium') == 'hard' else 
                              2 if difficulty.get(s, 'medium') == 'medium' else 1 
                              for s in subjects])
            daily_hours = (weight / total_weight) * hours_per_day
        
        subjects_list.append({
            'name': subj,
            'difficulty': diff,
            'daily_hours': round(daily_hours, 2)
        })
    
    # Create schedule (first 7 days)
    schedule = []
    start_date = datetime.now()
    
    for day in range(1, min(7, total_days) + 1):
        day_plan = {
            'day': day,
            'date': (start_date + timedelta(days=day-1)).strftime('%Y-%m-%d'),
            'slots': []
        }
        
        current_hour = 9  # Start at 9 AM
        
        for subject in subjects_list:
            # Add study slot
            day_plan['slots'].append({
                'subject': subject['name'],
                'start_time': f"{current_hour:02d}:00",
                'duration': subject['daily_hours'],
                'difficulty': subject['difficulty']
            })
            
            current_hour += int(subject['daily_hours'])
            
            # Add break if requested
            if include_breaks and random.random() > 0.4:
                day_plan['slots'].append({
                    'activity': 'Break',
                    'start_time': f"{current_hour:02d}:00",
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