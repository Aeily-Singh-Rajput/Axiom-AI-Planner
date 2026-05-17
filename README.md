Here is your **clean, final `README.md`** for AXIOM (ready to copy-paste into GitHub):

---

````md
# 🧠 Axiom Planner – Intelligent Academic Scheduler

Axiom Planner is an AI-powered academic management system designed to help students efficiently handle assignments, exams, and study planning. It intelligently distributes workload, reduces stress, and improves productivity using structured scheduling and AI-based assistance.

---

## 🚀 Problem Statement

Students often struggle to balance assignments, exams, and study workload. Existing tools mainly track deadlines but fail to consider:

- Overall workload pressure  
- Exam proximity impact  
- Subject-wise study balance  
- Time optimization across days  

This leads to inefficient planning and increased stress.

---

## 💡 Proposed Solution

Axiom Planner provides an intelligent academic planning system that:

- Accepts assignments and deadlines  
- Accepts exam schedules  
- Processes study materials (PDF uploads)  
- Extracts and summarizes content using AI modules  
- Calculates workload and stress levels  
- Generates optimized study schedules  
- Visualizes progress and planning data  

---

## ✨ Key Features

- 📄 PDF Upload & Text Extraction  
- 🧠 AI-Based Summarization System  
- 📊 Smart Workload Distribution Engine  
- 📅 Exam-Aware Scheduling Algorithm  
- 📚 Study Plan Generation  
- ⚠️ Stress Level Analysis  
- 📈 Data Visualization Dashboard  
- 📋 Daily Task Recommendations  

---

## 🏗️ Project Structure

```bash
axiom/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
│
├── modules/
│   ├── __init__.py
│   ├── ai_summarizer.py
│   ├── data_manager.py
│   ├── pdf_extractor.py
│   ├── scheduler.py
│   ├── stress_calculator.py
│   ├── study_plan_cache.py
│   ├── visualizer.py
│   └── __pycache__/
│
├── routes/
│   ├── __init__.py
│   ├── assignment_routes.py
│   ├── dashboard_routes.py
│   ├── exam_routes.py
│   ├── scheduler_routes.py
│   ├── settings_routes.py
│   ├── upload_routes.py
│   └── __pycache__/
│
├── static/
│   ├── css/
│   │   ├── style.css
│   │   └── toggle-artwork.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── pomodoro.html
│   ├── settings.html
│   ├── study_plan.html
│   └── upload.html
│
├── uploads/
│   └── (user uploaded files)
````

---

## ⚙️ Technologies Used

* Python (Core backend logic)
* Flask (Web framework)
* OOP (Modular architecture)
* JSON File Handling
* AI Modules (Summarization & analysis)
* NumPy & Pandas (Data processing)
* Matplotlib (Visualization)

---

## 🔄 System Workflow

User Input (Assignments + Exams + PDFs)
→ Upload Module
→ Data Storage
→ PDF Extraction
→ AI Summarization
→ Scheduler Engine
→ Stress Calculation
→ Study Plan Generation
→ Visualization Module
→ Final Dashboard Output

---

## 🧩 System Architecture

Frontend (Flask Templates)
↓
Route Layer (Flask Routes)
↓
Core Modules Layer
↓
Services:

* Scheduler
* AI Summarizer
* Data Manager
* Stress Calculator
* Visualizer

---

## 📊 Output

* Personalized daily study plan
* Workload distribution charts
* Exam-aware scheduling
* Stress level indicator
* Visual analytics dashboard

---

## 👥 Team Members

* Aeily Singh Rajput – Project Lead
* Shreya  
* Sweksha Singh  
* Divija Patel

---

## 📌 Future Scope

* Mobile application
* AI chatbot assistant
* Cloud database integration
* Real-time notifications
* Advanced analytics dashboard

---

## 🔐 Security

* API keys stored in `.env` file
* Sensitive files excluded using `.gitignore`
* No credentials hardcoded in source code

---

## 🧠 Conclusion

Axiom Planner is an intelligent academic assistant that helps students manage time efficiently by balancing assignments, exams, and study workloads using AI-powered scheduling and structured planning.

---

## 📄 License

All Rights Reserved © 2026
This project cannot be copied, modified, or reused without permission.

```