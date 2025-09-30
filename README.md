# 📚 LMS Automation Helper – Flask + MongoDB

Web-based automation platform built with **Flask, MongoDB, Bootstrap, and JavaScript**.
This system helps generate **customized assignment files** and provides **quiz helpers** so students can easily download their own tasks.

---

## 🚀 Features

* 🔑 **Student Login** – each student has their own account
* ⚡ **Automated Task Generation** – assignments are adjusted per student (e.g., API URL, IDs)
* 📝 **Quiz Helper** – shows correct answers for quizzes
* 📥 **Self-Service Download** – students log in and download tasks directly
* 💾 **MongoDB Database** – stores user and task data
* 🎨 **Bootstrap UI** – clean and simple interface

---

## 🛠️ Tech Stack

* **Backend**: Python Flask
* **Database**: MongoDB
* **Frontend**: HTML, CSS, Bootstrap, JavaScript

---

## 📂 Project Structure

```
lms-automation/
│
├── app/
│   ├── routes.py         # Flask routes
│   ├── models.py         # MongoDB schema
│   ├── services/         # business logic
│   │   ├── file_generator.py
│   │   └── quiz_helper.py
│   ├── static/           # CSS, JS, Bootstrap
│   └── templates/        # HTML (Jinja2)
│
├── config.py             # settings
├── run.py                # Flask entrypoint
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

1. Clone the repo:

   ```bash
   git clone https://github.com/username/lms-automation.git
   cd lms-automation
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:

   ```bash
   flask run
   ```

---
