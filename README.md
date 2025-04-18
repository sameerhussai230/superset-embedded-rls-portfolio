# ✨ Superset Embedded RLS Portfolio Demo ✨

This project demonstrates how to securely embed Apache Superset dashboards into a custom web application (React + FastAPI), implementing dynamic **Row-Level Security (RLS)** based on user roles.

---

## 🚀 Live Demo GIF

![superset](https://github.com/user-attachments/assets/0abd3412-bd8c-40d3-8fd4-984bb7212e17)


*(GIF shows the login process, the RLS-filtered view for 'Cipla Ltd', and the full-access view for the 'admin' user.)*

---

## 📖 Detailed Walkthrough

For a step-by-step guide on how this project was built, including detailed explanations of the Superset setup, FastAPI backend logic, and React frontend integration, check out my Medium article:

➡️ [**Building Secure, Role-Based Embedded Dashboards with Apache Superset, FastAPI, and React**](https://medium.com/@sameerhussain230/building-secure-role-based-embedded-dashboards-with-apache-superset-fastapi-and-react-3798ed7f8651)

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

2.  **Clone Repository:**
    ```bash
    git clone https://github.com/sameerhussai230/superset-embedded-rls-portfolio.git
    cd superset-embedded-rls-portfolio
    ```

3.  **Configure Backend Environment:**
    *   Navigate to the `embedding_app` directory.
    *   Create a `.env` file (you can copy `.env.example` if one exists).
    *   Ensure `SUPERSET_URL=http://localhost:8088` is set.
    *   Set `SUPERSET_ADMIN_USER` and `SUPERSET_ADMIN_PASSWORD` to the credentials the backend will use to talk to the Superset API (e.g., `admin`/`admin` if using the default Superset admin).
    *   Leave `SUPERSET_DASHBOARD_ID` blank for now.

4.  **Configure Frontend Environment:**
    *   Navigate to the `react_app` directory.
    *   Create a `.env` file.
    *   Set `VITE_API_BASE_URL=http://localhost:8000` (or your FastAPI port).
    *   Set `VITE_SUPERSET_URL=http://localhost:8088`.
    *   Leave `VITE_SUPERSET_DASHBOARD_ID` blank for now.

5.  **Run Superset (Docker):**
    *   Navigate back to the project root directory (`superset-embedded-rls-portfolio`).
    *   Build and start the Docker containers:
        ```bash
        docker-compose up --build -d
        ```
    *   **First Time Setup Only:** Initialize Superset and create the admin user (use the same credentials as set for `SUPERSET_ADMIN_USER`/`PASSWORD` in the backend `.env`):
        ```bash
        # Create admin user
        docker exec -it superset_app superset fab create-admin \
          --username admin \
          --firstname Admin \
          --lastname User \
          --email admin@example.com \
          --password admin

        # Initialize database and roles
        docker exec -it superset_app superset db upgrade
        docker exec -it superset_app superset init
        ```
    *   Wait a minute for services to stabilize. Access Superset UI at `http://localhost:8088` and log in (`admin`/`admin`).

6.  **Setup Superset UI & Get Dashboard ID:**
    *   Log in to Superset (`http://localhost:8088`).
    *   Upload your data (e.g., the Kaggle CSV) via `Data -> Upload a CSV`.
    *   Create your charts and assemble your dashboard.
    *   Verify the `Gamma` role exists (`Settings -> List Roles`) and has `datasource access` and `dashboard access` for your data and dashboard.
    *   Navigate to your dashboard, click `Share -> Embed dashboard`, and **copy the Dashboard ID (UUID)**.

7.  **Update Dashboard ID in Environment Files:**
    *   Paste the copied Dashboard ID into `embedding_app/.env`:
        ```dotenv
        SUPERSET_DASHBOARD_ID=your-copied-dashboard-uuid-here
        ```
    *   Paste the same Dashboard ID into `react_app/.env`:
        ```dotenv
        VITE_SUPERSET_DASHBOARD_ID=your-copied-dashboard-uuid-here
        ```

8.  **Run Backend (FastAPI):**
    *   Navigate to `embedding_app`.
    *   Set up a virtual environment:
        ```bash
        python -m venv venv
        # Activate (Windows):
        venv\Scripts\activate
        # Activate (Linux/macOS):
        # source venv/bin/activate
        ```
    *   Install dependencies:
        ```bash
        pip install -r requirements.txt
        ```
    *   Run the FastAPI server:
        ```bash
        # Using uvicorn for development with auto-reload
        uvicorn main:app --reload --port 8000
        # Or simply: python main.py
        ```

9.  **Run Frontend (React):**
    *   Open a **new terminal**.
    *   Navigate to `react_app`.
    *   Install dependencies:
        ```bash
        npm install
        ```
    *   Run the React development server:
        ```bash
        npm run dev
        ```
    *   Access the application, usually at `http://localhost:5173`.

---
