from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from supabase import create_client, Client
import os
import hashlib
from datetime import datetime
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = 'ai_study_planner_secret_123_change_this_later'
CORS(app)

# =================== SUPABASE CONFIGURATION ===================

SUPABASE_URL = "https://rvtwotjtbnqhfxzssusm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ2dHdvdGp0Ym5xaGZ4enNzdXNtIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NjMxMzIzOSwiZXhwIjoyMDgxODg5MjM5fQ.l1nlXT36IHNnLVN7jY3o9w_QB_ygTXVRRK_aghDCe1A"

# Initialize Supabase client
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ Connected to Supabase successfully!")
    
    # Test the connection
    test_result = supabase.table('users').select('count', count='exact').execute()
    print(f"✅ Database test passed. Users count: {test_result.count}")
    
    supabase_connected = True
except Exception as e:
    print(f"❌ Supabase connection failed: {e}")
    print("⚠️ Using in-memory storage")
    supabase = None
    supabase_connected = False

# In-memory storage (fallback)
users_db = {}
plans_db = {}

# =================== MAIN ROUTE ===================

@app.route('/')
def index():
    """Main route - serves the homepage"""
    logged_in = 'user_id' in session
    contact = session.get('contact', '')
    
    # Get user's plans if logged in
    user_plans = []
    if logged_in:
        user_plans = get_user_plans(session['user_id'])
    
    return render_template('index.html', 
                         logged_in=logged_in, 
                         contact=contact, 
                         user_plans=user_plans)

# =================== API ROUTES ===================

@app.route('/api/check_login', methods=['GET'])
def check_login():
    """Check login status"""
    return jsonify({
        'logged_in': 'user_id' in session,
        'contact': session.get('contact', '')
    })

@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle login - WORKS WITH SUPABASE"""
    try:
        # Get the contact data
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'})
        
        email_or_phone = data.get('contact', '').strip()
        
        if not email_or_phone:
            return jsonify({'success': False, 'error': 'Contact info required'})
        
        # Determine if it's email or phone
        is_email = '@' in email_or_phone
        
        # Try Supabase first
        if supabase_connected:
            try:
                # Check if user exists
                if is_email:
                    response = supabase.table('users').select('*').eq('email', email_or_phone).execute()
                else:
                    response = supabase.table('users').select('*').eq('phone', email_or_phone).execute()
                
                if response.data and len(response.data) > 0:
                    # User exists
                    user = response.data[0]
                    user_id = str(user['id'])
                    print(f"✅ User found in Supabase: {email_or_phone}")
                else:
                    # Create new user
                    user_data = {
                        'email': email_or_phone if is_email else None,
                        'phone': email_or_phone if not is_email else None,
                        'created_at': datetime.now().isoformat()
                    }
                    print(f"Creating new user in Supabase: {user_data}")
                    
                    response = supabase.table('users').insert(user_data).execute()
                    user_id = str(response.data[0]['id'])
                    print(f"✅ New user created in Supabase with ID: {user_id}")
                
            except Exception as supabase_error:
                print(f"❌ Supabase error: {supabase_error}")
                # Fallback to in-memory
                user_id = hashlib.md5(email_or_phone.encode()).hexdigest()
                users_db[user_id] = {
                    'id': user_id,
                    'contact': email_or_phone,
                    'created_at': datetime.now().isoformat()
                }
                print(f"⚠️ Using in-memory storage for user: {email_or_phone}")
        else:
            # Use in-memory storage
            user_id = hashlib.md5(email_or_phone.encode()).hexdigest()
            users_db[user_id] = {
                'id': user_id,
                'contact': email_or_phone,
                'created_at': datetime.now().isoformat()
            }
            print(f"📝 Using in-memory storage: {email_or_phone}")
        
        # Store in session
        session['user_id'] = user_id
        session['contact'] = email_or_phone
        
        return jsonify({
            'success': True, 
            'user_id': user_id,
            'contact': email_or_phone
        })
        
    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Logout user"""
    session.clear()
    return jsonify({'success': True})

# =================== STUDY PLAN ROUTES ===================

@app.route('/api/generate_plan', methods=['POST'])
def generate_plan():
    """Generate study plan"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract data
        subjects_input = data.get('subjects', '')
        subjects = [s.strip() for s in subjects_input.split(',') if s.strip()]
        
        if not subjects:
            return jsonify({'error': 'Subjects required'}), 400
        
        hours_per_day = float(data.get('hours_per_day', 3))
        
        # Import and use ML model
        try:
            import ml_model
            plan = ml_model.generate_study_plan(
                subjects=subjects,
                hours_per_day=hours_per_day,
                study_period=data.get('study_period', '30 days'),
                equal_time=data.get('equal_time', 'no') == 'yes',
                difficulty=data.get('difficulty', {}),
                preference=data.get('preference', 'balanced'),
                exam_mode=data.get('exam_scheduled', 'no') == 'yes',
                include_breaks=data.get('break_time', 'no') == 'yes'
            )
        except Exception as ml_error:
            print(f"ML model error: {ml_error}")
            # Simple fallback plan
            plan = {
                'total_days': 30,
                'daily_hours': hours_per_day,
                'subjects': [
                    {'name': subj, 'difficulty': 'medium', 'daily_hours': round(hours_per_day/len(subjects), 2)}
                    for subj in subjects
                ],
                'schedule': []
            }
        
        # Save to Supabase or memory
        plan_data = {
            'user_id': session['user_id'],
            'plan_name': f"Plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'subjects': subjects,
            'hours_per_day': hours_per_day,
            'study_period': data.get('study_period', '30 days'),
            'plan_data': plan,
            'created_at': datetime.now().isoformat()
        }
        
        plan_id = save_plan_to_db(plan_data)
        
        return jsonify({
            'success': True,
            'plan': plan,
            'plan_id': plan_id
        })
        
    except Exception as e:
        print(f"❌ Generate plan error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/plans', methods=['GET'])
def get_plans():
    """Get user's plans"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        user_plans = get_user_plans(session['user_id'])
        
        return jsonify({
            'success': True,
            'plans': user_plans
        })
        
    except Exception as e:
        print(f"❌ Get plans error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/plans/<plan_id>', methods=['GET'])
def get_plan(plan_id):
    """Get specific plan"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        plan = None
        
        # Try Supabase
        if supabase_connected:
            try:
                response = supabase.table('study_plans').select('*').eq('id', plan_id).execute()
                if response.data:
                    plan = response.data[0]
            except Exception as e:
                print(f"Supabase get plan error: {e}")
        
        # Fallback to memory
        if not plan:
            try:
                plan_id_int = int(plan_id)
                plan = plans_db.get(plan_id_int)
            except:
                pass
        
        if plan and plan.get('user_id') == session['user_id']:
            return jsonify({'success': True, 'plan': plan})
        else:
            return jsonify({'error': 'Plan not found'}), 404
            
    except Exception as e:
        print(f"❌ Get plan error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/plans/<plan_id>', methods=['DELETE'])
def delete_plan(plan_id):
    """Delete plan"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Not logged in'}), 401
        
        success = False
        
        # Try Supabase
        if supabase_connected:
            try:
                response = supabase.table('study_plans').delete().eq('id', plan_id).execute()
                success = True
            except Exception as e:
                print(f"Supabase delete error: {e}")
        
        # Also delete from memory
        try:
            plan_id_int = int(plan_id)
            if plan_id_int in plans_db:
                del plans_db[plan_id_int]
                success = True
        except:
            pass
        
        if success:
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Failed to delete plan'}), 500
        
    except Exception as e:
        print(f"❌ Delete plan error: {e}")
        return jsonify({'error': str(e)}), 500

# =================== HELPER FUNCTIONS ===================

def get_user_plans(user_id):
    """Get plans for a user"""
    user_plans = []
    
    # Try Supabase first
    if supabase_connected:
        try:
            response = supabase.table('study_plans').select('*').eq('user_id', user_id).execute()
            user_plans = response.data
            print(f"📊 Found {len(user_plans)} plans in Supabase for user {user_id}")
        except Exception as e:
            print(f"Supabase get plans error: {e}")
    
    # Also check in-memory
    in_memory_plans = [p for p in plans_db.values() if p.get('user_id') == user_id]
    user_plans.extend(in_memory_plans)
    
    return user_plans

def save_plan_to_db(plan_data):
    """Save plan to database"""
    plan_id = None
    
    # Try Supabase
    if supabase_connected:
        try:
            print(f"💾 Saving plan to Supabase: {plan_data['plan_name']}")
            response = supabase.table('study_plans').insert(plan_data).execute()
            plan_id = response.data[0]['id']
            plan_data['id'] = plan_id
            print(f"✅ Plan saved to Supabase with ID: {plan_id}")
        except Exception as e:
            print(f"❌ Supabase save error: {e}")
            # Fallback to in-memory
            plan_id = len(plans_db) + 1
            plan_data['id'] = plan_id
            plans_db[plan_id] = plan_data
            print(f"📝 Plan saved to memory with ID: {plan_id}")
    else:
        # Use in-memory
        plan_id = len(plans_db) + 1
        plan_data['id'] = plan_id
        plans_db[plan_id] = plan_data
        print(f"📝 Plan saved to memory with ID: {plan_id}")
    
    return plan_id

# =================== TEST ROUTES ===================

@app.route('/test')
def test():
    """Test route"""
    return f"""
    <h1>AI Study Planner - Test Page</h1>
    <p>Flask server is working!</p>
    <p>Supabase connected: {supabase_connected}</p>
    <p>Session: {dict(session) if session else 'No session'}</p>
    <p><a href="/">Go to App</a></p>
    <p><a href="/api/test">Test API</a></p>
    """

@app.route('/api/test')
def api_test():
    """Test API"""
    # Test Supabase connection
    users_count = 0
    plans_count = 0
    
    if supabase_connected:
        try:
            users_result = supabase.table('users').select('count', count='exact').execute()
            users_count = users_result.count
            plans_result = supabase.table('study_plans').select('count', count='exact').execute()
            plans_count = plans_result.count
        except Exception as e:
            users_count = f"Error: {e}"
    
    return jsonify({
        'status': 'ok',
        'message': 'API is working!',
        'supabase_connected': supabase_connected,
        'supabase_users_count': users_count,
        'supabase_plans_count': plans_count,
        'memory_users_count': len(users_db),
        'memory_plans_count': len(plans_db),
        'session': dict(session) if session else 'No session',
        'server_time': datetime.now().isoformat()
    })

# =================== START SERVER ===================

if __name__ == '__main__':
    # Create folders
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    print("=" * 60)
    print("🚀 AI STUDY PLANNER - READY TO LAUNCH")
    print("=" * 60)
    print(f"📂 Working directory: {os.getcwd()}")
    print(f"📁 Templates folder: {'✅ Exists' if os.path.exists('templates') else '❌ Missing'}")
    print(f"📄 Template file: {'✅ Found' if os.path.exists('templates/index.html') else '❌ Missing'}")
    print(f"🔗 Supabase: {'✅ Connected' if supabase_connected else '❌ Not connected'}")
    print("=" * 60)
    print("🌐 ** OPEN YOUR BROWSER AND VISIT: **")
    print("👉 http://127.0.0.1:5000/ 👈")
    print("=" * 60)
    print("🔧 Test endpoints:")
    print("   http://127.0.0.1:5000/test")
    print("   http://127.0.0.1:5000/api/test")
    print("=" * 60)
    print("📊 To verify Supabase connection, check:")
    print("   1. Disable RLS in Supabase dashboard")
    print("   2. Visit /api/test to see user count")
    print("=" * 60)
    
    app.run(debug=True, port=5000, use_reloader=False)