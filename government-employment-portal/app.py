from flask import Flask, render_template, request, redirect, session, flash
import pandas as pd
from datetime import datetime, timedelta
import os
import random
import hashlib

app = Flask(__name__)
app.secret_key = 'government-employment-portal-secret-2025'

# Ensure data directory exists
os.makedirs('data', exist_ok=True)

# Initialize CSV files
def init_data():
    if not os.path.exists('data/users.csv'):
        pd.DataFrame(columns=['user_id', 'name', 'email', 'phone', 'password', 'role', 'district', 'aadhaar', 'disability_status', 'days_worked', 'created_at']).to_csv('data/users.csv', index=False)
    if not os.path.exists('data/jobs.csv'):
        pd.DataFrame(columns=['job_id', 'district', 'work_type', 'start_date', 'duration', 'workers_required', 'daily_wage', 'status', 'created_by', 'created_at']).to_csv('data/jobs.csv', index=False)
    if not os.path.exists('data/allocations.csv'):
        pd.DataFrame(columns=['allocation_id', 'job_id', 'worker_id', 'allocation_status', 'response', 'priority_score', 'allocated_at']).to_csv('data/allocations.csv', index=False)
    if not os.path.exists('data/attendance.csv'):
        pd.DataFrame(columns=['attendance_id', 'job_id', 'worker_id', 'supervisor_id', 'date', 'status', 'marked_at']).to_csv('data/attendance.csv', index=False)
    if not os.path.exists('data/wages.csv'):
        pd.DataFrame(columns=['wage_id', 'worker_id', 'job_id', 'days_present', 'daily_wage', 'total_wage', 'payment_status', 'calculated_at']).to_csv('data/wages.csv', index=False)
    if not os.path.exists('data/otp.csv'):
        pd.DataFrame(columns=['phone', 'otp', 'created_at', 'used']).to_csv('data/otp.csv', index=False)

init_data()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp(phone, otp):
    print(f"\n{'='*50}")
    print(f"📱 OTP for {phone}: {otp}")
    print(f"{'='*50}\n")
    return True

def verify_otp(phone, otp):
    try:
        otp_df = pd.read_csv('data/otp.csv')
        valid = otp_df[(otp_df['phone'] == phone) & (otp_df['otp'] == otp) & (otp_df['used'] == False)]
        if not valid.empty:
            latest = valid.iloc[-1]
            created = datetime.strptime(latest['created_at'], '%Y-%m-%d %H:%M:%S')
            if datetime.now() - created < timedelta(minutes=10):
                otp_df.loc[otp_df.index == latest.name, 'used'] = True
                otp_df.to_csv('data/otp.csv', index=False)
                return True
    except:
        pass
    return False

def calc_priority(worker):
    score = 0
    if worker['disability_status'] == 'Yes':
        score += 100
    if worker['days_worked'] < 50:
        score += 50
    score += (100 - min(worker['days_worked'], 100))
    return score

def allocate_workers(job_id):
    users = pd.read_csv('data/users.csv')
    jobs = pd.read_csv('data/jobs.csv')
    allocations = pd.read_csv('data/allocations.csv')
    
    job = jobs[jobs['job_id'] == job_id].iloc[0]
    workers = users[(users['role'] == 'worker') & (users['district'] == job['district'])].copy()
    
    if workers.empty:
        return
    
    workers['priority_score'] = workers.apply(calc_priority, axis=1)
    workers = workers.sort_values('priority_score', ascending=False)
    
    required = int(job['workers_required'])
    selected = workers.head(required)
    waiting = workers.iloc[required:]
    
    for _, w in selected.iterrows():
        alloc_id = f"ALLOC{str(len(allocations) + 1).zfill(5)}"
        new_alloc = {
            'allocation_id': alloc_id,
            'job_id': job_id,
            'worker_id': w['user_id'],
            'allocation_status': 'Allocated',
            'response': 'Pending',
            'priority_score': w['priority_score'],
            'allocated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        allocations = pd.concat([allocations, pd.DataFrame([new_alloc])], ignore_index=True)
    
    for _, w in waiting.iterrows():
        alloc_id = f"ALLOC{str(len(allocations) + 1).zfill(5)}"
        new_alloc = {
            'allocation_id': alloc_id,
            'job_id': job_id,
            'worker_id': w['user_id'],
            'allocation_status': 'Waiting',
            'response': 'Pending',
            'priority_score': w['priority_score'],
            'allocated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        allocations = pd.concat([allocations, pd.DataFrame([new_alloc])], ignore_index=True)
    
    allocations.to_csv('data/allocations.csv', index=False)

# ========== HOME & AUTH ==========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            users = pd.read_csv('data/users.csv')
            name = request.form['name']
            email = request.form['email']
            phone = request.form['phone']
            password = hash_password(request.form['password'])
            role = request.form['role']
            district = request.form.get('district', '')
            aadhaar = request.form.get('aadhaar', '')
            disability = request.form.get('disability_status', 'No')
            
            if not users[(users['email'] == email) | (users['phone'] == phone)].empty:
                flash('User already exists!', 'error')
                return redirect('/signup')
            
            user_id = f"{role[:3].upper()}{str(len(users) + 1).zfill(4)}"
            new_user = {
                'user_id': user_id,
                'name': name,
                'email': email,
                'phone': phone,
                'password': password,
                'role': role,
                'district': district,
                'aadhaar': aadhaar,
                'disability_status': disability,
                'days_worked': 0,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            users = pd.concat([users, pd.DataFrame([new_user])], ignore_index=True)
            users.to_csv('data/users.csv', index=False)
            flash('Signup successful! Please login.', 'success')
            return redirect('/login')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            session.clear()
            users = pd.read_csv('data/users.csv')
            email = request.form['email']
            password = hash_password(request.form['password'])
            user = users[(users['email'] == email) & (users['password'] == password)]
            if not user.empty:
                u = user.iloc[0]
                session['user_id'] = str(u['user_id'])
                session['name'] = str(u['name'])
                session['role'] = str(u['role'])
                session['phone'] = str(u['phone'])
                if u['role'] == 'government':
                    return redirect('/government/dashboard')
                elif u['role'] == 'worker':
                    return redirect('/worker/dashboard')
                elif u['role'] == 'supervisor':
                    return redirect('/supervisor/dashboard')
            flash('Invalid credentials!', 'error')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect('/')

# ========== GOVERNMENT ==========
@app.route('/government/dashboard')
def gov_dashboard():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    users = pd.read_csv('data/users.csv')
    jobs = pd.read_csv('data/jobs.csv')
    allocations = pd.read_csv('data/allocations.csv')
    wages = pd.read_csv('data/wages.csv')
    stats = {
        'total_workers': len(users[users['role'] == 'worker']),
        'active_jobs': len(jobs[jobs['status'] == 'active']),
        'workers_allocated': len(allocations[allocations['allocation_status'] == 'Allocated']),
        'wages_paid': wages['total_wage'].sum() if not wages.empty else 0,
        'disabled_workers': len(users[(users['role'] == 'worker') & (users['disability_status'] == 'Yes')])
    }
    return render_template('government_dashboard.html', stats=stats)

@app.route('/government/create-job', methods=['GET', 'POST'])
def create_job():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    if request.method == 'POST':
        try:
            jobs = pd.read_csv('data/jobs.csv')
            job_id = f"JOB{str(len(jobs) + 1).zfill(4)}"
            new_job = {
                'job_id': job_id,
                'district': request.form['district'],
                'work_type': request.form['work_type'],
                'start_date': request.form['start_date'],
                'duration': request.form['duration'],
                'workers_required': int(request.form['workers_required']),
                'daily_wage': float(request.form['daily_wage']),
                'status': 'active',
                'created_by': session['user_id'],
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            jobs = pd.concat([jobs, pd.DataFrame([new_job])], ignore_index=True)
            jobs.to_csv('data/jobs.csv', index=False)
            allocate_workers(job_id)
            flash('Job created successfully!', 'success')
            return redirect('/government/jobs')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('create_job.html')

@app.route('/government/jobs')
def gov_jobs():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    jobs = pd.read_csv('data/jobs.csv')
    return render_template('government_jobs.html', jobs=jobs.to_dict('records'))

@app.route('/government/allocations/<job_id>')
def view_allocations(job_id):
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    allocations = pd.read_csv('data/allocations.csv')
    users = pd.read_csv('data/users.csv')
    jobs = pd.read_csv('data/jobs.csv')
    job = jobs[jobs['job_id'] == job_id].iloc[0] if not jobs[jobs['job_id'] == job_id].empty else None
    allocs = allocations[allocations['job_id'] == job_id]
    allocs = allocs.merge(users[['user_id', 'name', 'phone', 'disability_status', 'days_worked']], 
                          left_on='worker_id', right_on='user_id', how='left')
    allocated = allocs[allocs['allocation_status'] == 'Allocated'].to_dict('records')
    waiting = allocs[allocs['allocation_status'] == 'Waiting'].to_dict('records')
    return render_template('view_allocations.html', job=job, allocated=allocated, waiting=waiting)

@app.route('/government/attendance')
def gov_attendance():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    attendance = pd.read_csv('data/attendance.csv')
    users = pd.read_csv('data/users.csv')
    attendance = attendance.merge(users[['user_id', 'name']], left_on='worker_id', right_on='user_id', how='left')
    return render_template('government_attendance.html', attendance=attendance.to_dict('records'))

@app.route('/government/wages')
def gov_wages():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    wages = pd.read_csv('data/wages.csv')
    users = pd.read_csv('data/users.csv')
    wages = wages.merge(users[['user_id', 'name']], left_on='worker_id', right_on='user_id', how='left')
    return render_template('government_wages.html', wages=wages.to_dict('records'))

@app.route('/government/calculate-wages')
def calculate_wages():
    if 'user_id' not in session or session['role'] != 'government':
        return redirect('/login')
    attendance = pd.read_csv('data/attendance.csv')
    jobs = pd.read_csv('data/jobs.csv')
    wages = pd.read_csv('data/wages.csv')
    if not attendance.empty:
        grouped = attendance[attendance['status'] == 'Present'].groupby(['worker_id', 'job_id']).size().reset_index(name='days_present')
        for _, row in grouped.iterrows():
            job = jobs[jobs['job_id'] == row['job_id']]
            if not job.empty:
                daily_wage = job.iloc[0]['daily_wage']
                total = row['days_present'] * daily_wage
                wage_id = f"WAGE{str(len(wages) + 1).zfill(5)}"
                new_wage = {
                    'wage_id': wage_id,
                    'worker_id': row['worker_id'],
                    'job_id': row['job_id'],
                    'days_present': row['days_present'],
                    'daily_wage': daily_wage,
                    'total_wage': total,
                    'payment_status': 'Pending',
                    'calculated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                wages = pd.concat([wages, pd.DataFrame([new_wage])], ignore_index=True)
        wages.to_csv('data/wages.csv', index=False)
        flash('Wages calculated!', 'success')
    else:
        flash('No attendance data!', 'warning')
    return redirect('/government/wages')

# ========== WORKER ==========
@app.route('/worker/dashboard')
def worker_dashboard():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    users = pd.read_csv('data/users.csv')
    allocations = pd.read_csv('data/allocations.csv')
    attendance = pd.read_csv('data/attendance.csv')
    wages = pd.read_csv('data/wages.csv')
    worker = users[users['user_id'] == session['user_id']].iloc[0]
    stats = {
        'total_days_worked': int(worker['days_worked']),
        'active_jobs': len(allocations[(allocations['worker_id'] == session['user_id']) & (allocations['allocation_status'] == 'Allocated')]),
        'days_present': len(attendance[(attendance['worker_id'] == session['user_id']) & (attendance['status'] == 'Present')]),
        'total_earnings': wages[wages['worker_id'] == session['user_id']]['total_wage'].sum() if not wages.empty else 0
    }
    return render_template('worker_dashboard.html', worker=worker, stats=stats)

@app.route('/worker/profile')
def worker_profile():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    users = pd.read_csv('data/users.csv')
    worker = users[users['user_id'] == session['user_id']].iloc[0].to_dict()
    aadhaar = worker['aadhaar']
    worker['masked_aadhaar'] = 'XXXX-XXXX-' + str(aadhaar)[-4:] if aadhaar else 'Not Provided'
    return render_template('worker_profile.html', worker=worker)

@app.route('/worker/jobs')
def worker_jobs():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    allocations = pd.read_csv('data/allocations.csv')
    jobs = pd.read_csv('data/jobs.csv')
    allocs = allocations[allocations['worker_id'] == session['user_id']]
    allocs = allocs.merge(jobs, on='job_id', how='left')
    return render_template('worker_jobs.html', jobs=allocs.to_dict('records'))

@app.route('/worker/respond-job', methods=['POST'])
def respond_job():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    allocations = pd.read_csv('data/allocations.csv')
    alloc_id = request.form['allocation_id']
    response = request.form['response']
    allocations.loc[allocations['allocation_id'] == alloc_id, 'response'] = response
    allocations.to_csv('data/allocations.csv', index=False)
    flash(f'Job {response.lower()} successfully!', 'success')
    return redirect('/worker/jobs')

@app.route('/worker/attendance')
def worker_attendance():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    attendance = pd.read_csv('data/attendance.csv')
    jobs = pd.read_csv('data/jobs.csv')
    att = attendance[attendance['worker_id'] == session['user_id']]
    att = att.merge(jobs[['job_id', 'work_type']], on='job_id', how='left')
    return render_template('worker_attendance.html', attendance=att.to_dict('records'))

@app.route('/worker/wages')
def worker_wages():
    if 'user_id' not in session or session['role'] != 'worker':
        return redirect('/login')
    wages = pd.read_csv('data/wages.csv')
    jobs = pd.read_csv('data/jobs.csv')
    w = wages[wages['worker_id'] == session['user_id']]
    w = w.merge(jobs[['job_id', 'work_type']], on='job_id', how='left')
    return render_template('worker_wages.html', wages=w.to_dict('records'))

# ========== SUPERVISOR ==========
@app.route('/supervisor/dashboard')
def sup_dashboard():
    if 'user_id' not in session or session['role'] != 'supervisor':
        return redirect('/login')
    jobs = pd.read_csv('data/jobs.csv')
    attendance = pd.read_csv('data/attendance.csv')
    stats = {
        'total_jobs': len(jobs),
        'today_attendance': len(attendance[(attendance['supervisor_id'] == session['user_id']) & (attendance['date'] == datetime.today().strftime('%Y-%m-%d'))]),
        'total_marked': len(attendance[attendance['supervisor_id'] == session['user_id']])
    }
    return render_template('supervisor_dashboard.html', stats=stats)

@app.route('/supervisor/jobs')
def sup_jobs():
    if 'user_id' not in session or session['role'] != 'supervisor':
        return redirect('/login')
    jobs = pd.read_csv('data/jobs.csv')
    users = pd.read_csv('data/users.csv')
    sup = users[users['user_id'] == session['user_id']].iloc[0]
    district_jobs = jobs[jobs['district'] == sup['district']]
    return render_template('supervisor_jobs.html', jobs=district_jobs.to_dict('records'))

@app.route('/supervisor/mark-attendance/<job_id>', methods=['GET', 'POST'])
def mark_attendance(job_id):
    if 'user_id' not in session or session['role'] != 'supervisor':
        return redirect('/login')
    if request.method == 'POST':
        phone = request.form['phone']
        otp = request.form.get('otp')
        if not otp:
            otp_code = generate_otp()
            otp_df = pd.read_csv('data/otp.csv')
            new_otp = {
                'phone': phone,
                'otp': otp_code,
                'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'used': False
            }
            otp_df = pd.concat([otp_df, pd.DataFrame([new_otp])], ignore_index=True)
            otp_df.to_csv('data/otp.csv', index=False)
            send_otp(phone, otp_code)
            flash(f'OTP sent! Check console for demo OTP', 'info')
            return render_template('mark_attendance.html', job_id=job_id, phone=phone, otp_sent=True)
        else:
            if verify_otp(phone, otp):
                users = pd.read_csv('data/users.csv')
                attendance = pd.read_csv('data/attendance.csv')
                worker = users[users['phone'] == phone]
                if not worker.empty:
                    w = worker.iloc[0]
                    today = datetime.today().strftime('%Y-%m-%d')
                    exists = attendance[(attendance['worker_id'] == w['user_id']) & (attendance['job_id'] == job_id) & (attendance['date'] == today)]
                    if not exists.empty:
                        flash('Already marked today!', 'warning')
                    else:
                        att_id = f"ATT{str(len(attendance) + 1).zfill(5)}"
                        new_att = {
                            'attendance_id': att_id,
                            'job_id': job_id,
                            'worker_id': w['user_id'],
                            'supervisor_id': session['user_id'],
                            'date': today,
                            'status': 'Present',
                            'marked_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        attendance = pd.concat([attendance, pd.DataFrame([new_att])], ignore_index=True)
                        attendance.to_csv('data/attendance.csv', index=False)
                        users.loc[users['user_id'] == w['user_id'], 'days_worked'] = w['days_worked'] + 1
                        users.to_csv('data/users.csv', index=False)
                        flash(f'Attendance marked for {w["name"]}!', 'success')
                else:
                    flash('Worker not found!', 'error')
            else:
                flash('Invalid OTP!', 'error')
            return redirect(f'/supervisor/mark-attendance/{job_id}')
    jobs = pd.read_csv('data/jobs.csv')
    allocations = pd.read_csv('data/allocations.csv')
    users = pd.read_csv('data/users.csv')
    job = jobs[jobs['job_id'] == job_id].iloc[0] if not jobs[jobs['job_id'] == job_id].empty else None
    workers = allocations[(allocations['job_id'] == job_id) & (allocations['allocation_status'] == 'Allocated')]
    workers = workers.merge(users[['user_id', 'name', 'phone', 'aadhaar']], left_on='worker_id', right_on='user_id', how='left')
    return render_template('mark_attendance.html', job=job, workers=workers.to_dict('records'), job_id=job_id)

@app.route('/supervisor/attendance-summary')
def att_summary():
    if 'user_id' not in session or session['role'] != 'supervisor':
        return redirect('/login')
    attendance = pd.read_csv('data/attendance.csv')
    users = pd.read_csv('data/users.csv')
    jobs = pd.read_csv('data/jobs.csv')
    att = attendance[attendance['supervisor_id'] == session['user_id']]
    att = att.merge(users[['user_id', 'name']], left_on='worker_id', right_on='user_id', how='left')
    att = att.merge(jobs[['job_id', 'work_type']], on='job_id', how='left')
    return render_template('attendance_summary.html', attendance=att.to_dict('records'))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🏛️  GOVERNMENT EMPLOYMENT PORTAL")
    print("="*60)
    print("📍 Server: http://localhost:5000")
    print("✅ Ready to accept connections...")
    print("="*60 + "\n")
    app.run(debug=True, host='0.0.0.0', port=5000)
