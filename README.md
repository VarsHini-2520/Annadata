# Government Employment Portal

## Transparent Employment Allocation and OTP-Based Attendance System

---

## Abstract

The **Government Employment Portal** is a role-based web application developed to ensure transparent, fair, and efficient allocation of government employment opportunities. The system automates worker allocation using a priority-based algorithm and ensures secure attendance marking through OTP verification. The application supports three user roles—Government Officers, Workers, and Supervisors—each with a dedicated portal and functionality.

The project demonstrates a complete end-to-end workflow including job creation, worker allocation, attendance tracking, and wage calculation, using Flask and CSV-based persistent storage.

---

## Table of Contents

1. Introduction  
2. System Objectives  
3. Features  
4. Technology Stack  
5. System Architecture  
6. Project Structure  
7. Installation and Setup  
8. Application Workflow  
9. Priority Allocation Algorithm  
10. OTP Attendance System  
11. Configuration  
12. Data Storage Design  
13. Security Measures  
14. Troubleshooting  
15. System Statistics  
16. Conclusion  

---

## 1. Introduction

Manual allocation of employment often leads to bias, lack of transparency, and inefficiencies. This project addresses these issues by implementing an automated and data-driven allocation system that prioritizes workers based on predefined criteria such as disability status and work history.

The system is designed for demonstration, academic submission, and prototype-level deployment.

---

## 2. System Objectives

- Ensure fair and transparent worker allocation  
- Eliminate manual bias in job assignment  
- Provide secure attendance verification using OTP  
- Maintain accurate wage and attendance records  
- Support role-based access control  

---

## 3. Features

### 3.1 Authentication and Authorization

- Role-based login (Government Officer, Worker, Supervisor)  
- Session-based authentication  
- Secure password hashing using SHA-256  
- OTP-based verification for workers and supervisors  

### 3.2 Government Officer Portal

- Create and manage employment jobs  
- Automatic worker allocation using priority scoring  
- View worker allocation details  
- Monitor attendance records  
- Calculate and track wages  
- Generate transparency reports  

### 3.3 Worker Portal

- OTP-based secure login  
- View allocated jobs  
- Respond to AI call notifications (Accept / Not Interested / Decline)  
- Track attendance history  
- View wages earned  
- Profile view with masked Aadhaar  

### 3.4 Supervisor Portal

- OTP-based secure login  
- View assigned jobs  
- Verify worker identity using phone number  
- Mark daily attendance  
- Attendance audit logging  

---

## 4. Technology Stack

| Layer          | Technology                        |
|---------------|----------------------------------|
| Backend        | Python, Flask                    |
| Frontend       | HTML, CSS, JavaScript            |
| Data Handling  | Pandas                           |
| Storage        | CSV Files                        |
| Authentication | Flask Sessions                   |
| Security       | SHA-256 Hashing, OTP Verification|

---

## 5. System Architecture

- Flask handles routing and business logic  
- HTML templates render role-specific dashboards  
- CSV files act as persistent storage  
- OTP verification ensures secure attendance  
- Priority algorithm ensures fair allocation  

---

## 6. Project Structure

```
complete-portal/
├── app.py
├── requirements.txt
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── government_*.html
│   ├── worker_*.html
│   └── supervisor_*.html
├── static/
│   ├── css/style.css
│   └── js/script.js
└── data/
```

---

## 7. Installation and Setup

### 7.1 Prerequisites

- Python 3.7 or higher  
- pip package manager  

### 7.2 Install Dependencies

```bash
pip install flask pandas
```

### 7.3 Run Application

```bash
python app.py
```

### 7.4 Access Application

```
http://localhost:5000
```

---

## 8. Application Workflow

1. Government Officer creates jobs  
2. Workers register and login via OTP  
3. System allocates workers using priority logic  
4. Supervisors mark attendance using phone verification  
5. Wages are calculated based on attendance  

---

## 9. Priority Allocation Algorithm

```
Priority Score =
  + 100 if Disability = Yes
  + 50  if Days Worked < 50
  + (100 - Days Worked)
```

Workers with higher scores are allocated first.

---

## 10. OTP Attendance System

- OTP generated for attendance verification  
- OTP is single-use and time-bound  
- In demo mode, OTP is printed in terminal  

Example:
```
OTP for 9876543210: 123456
```

---

## 11. Configuration

Change application port in `app.py`:

```python
app.run(debug=True, port=5001)
```

Integrate SMS services such as Twilio or AWS SNS for real OTP delivery.

---

## 12. Data Storage Design

| File Name | Description |
|---------|------------|
| workers.csv | Worker data |
| jobs.csv | Job records |
| allocations.csv | Worker-job mapping |
| attendance.csv | Attendance logs |
| wages.csv | Wage records |
| otp.csv | OTP logs |

---

## 13. Security Measures

- Password hashing (SHA-256)  
- OTP-based authentication  
- Session validation  
- Role-based access control  
- Aadhaar masking  

---

## 14. Troubleshooting

### Port Busy
```
lsof -ti:5000 | xargs kill -9
```

### Reset Data
```
rm -rf data/
python app.py
```

---

## 15. System Statistics

- Registered workers  
- Active jobs  
- Allocated workers  
- Attendance percentage  
- Total wages paid  

---

## 16. Conclusion

The **Government Employment Portal** demonstrates a transparent, automated, and secure employment allocation system. It showcases real-world concepts such as priority-based decision making, OTP authentication, and role-based access control, making it suitable for academic submission and further real-world extension.

---

## Author

Developed as a complete end-to-end academic project for transparent government employment management using Flask and CSV-based storage.
