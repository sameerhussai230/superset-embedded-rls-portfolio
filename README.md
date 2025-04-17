# ✨ Superset Embedded RLS Portfolio Demo ✨

This project demonstrates how to securely embed Apache Superset dashboards into a custom web application (React + FastAPI), implementing dynamic **Row-Level Security (RLS)** based on user roles.

**Created by:** [Sameer Hussain](https://www.linkedin.com/in/hussainsameer/)

---

## 🚀 Live Demo GIF

![superset](https://github.com/user-attachments/assets/0abd3412-bd8c-40d3-8fd4-984bb7212e17)


*(GIF shows the login process, the RLS-filtered view for 'Cipla Ltd', and the full-access view for the 'admin' user.)*

---

## 🌟 Features

*   **Secure Superset Embedding:** Integrates Superset dashboards seamlessly into a React application.
*   **Dynamic Row-Level Security (RLS):** Filters dashboard data based on the logged-in manufacturer's role.
*   **Custom Authentication:** Uses a FastAPI backend to handle user logins (Manufacturer vs. Admin) and generate appropriate Superset guest tokens.
*   **Role-Based Views:** Provides distinct dashboard experiences:
    *   Manufacturers see data only relevant to them.
    *   Admin user has full visibility of the dashboard data.
*   **Clear Separation:** Frontend (React), Backend (FastAPI), and BI Tool (Superset via Docker) are distinctly managed.

---

## 🛠️ Tech Stack

*   **BI Tool:** Apache Superset
*   **Backend:** Python, FastAPI
*   **Frontend:** React, Superset Embedded SDK
*   **Containerization:** Docker, Docker Compose
*   **Database (Superset Metadata):** PostgreSQL (in Docker)

---

## 📊 Data Source

The data used in this demonstration dashboard originates from the following Kaggle dataset:

*   **Dataset:** [11000+ Medicine Details](https://www.kaggle.com/datasets/singhnavjot2062001/11000-medicine-details) on Kaggle.

*(Note: The data might have been slightly modified or filtered for the specific needs of this demo.)*

---

## 🔑 How to Use the Demo

Log in with the following credentials to experience the different views:

*   **RLS View (Manufacturer):**
    *   Username: `Cipla Ltd`
    *   Password: `cipla`
    *   *(Other configured manufacturers like `Torrent Pharmaceuticals Ltd`/`torrent` will also work)*
*   **Full Access View (Admin):**
    *   Username: `admin`
    *   Password: `admin`

---

## ⚙️ Setup & Running Locally

1.  **Prerequisites:**
    *   Docker & Docker Compose
    *   Python 3.8+ & Pip
    *   Node.js & npm (or yarn)
2.  **Clone:** `git clone https://github.com/sameerhussai230/superset-embedded-rls-portfolio.git`
3.  **Configure Environment:**
    *   Update `.env` files with your Superset URL, Admin credentials (for token generation), Dashboard ID, etc .
4.  **Run Superset (Docker):**
    *   `cd superset-embedded-rls-portfolio`
    *   `docker-compose up --build -d` (Wait for Superset to initialize)
    *   *(Optional: Setup Superset admin user, roles, upload data, create dashboard if not done)*
5.  **Run Backend (FastAPI):**
    *   `cd embedding_app`
    *   `python -m venv venv`
    *   `venv\scripts\activate` (for windows)
    *   `pip install -r requirements.txt`
    *   `python main.py`
6.  **Run Frontend (React):**
    *   `cd ../react_app`
    *   `npm install`
    *   `npm run dev` (Usually runs on `http://localhost:5173`)

---
