# Getting Started

## Prerequisites

- [Python](https://www.python.org/downloads/) (via `py` launcher)
- [Git](https://git-scm.com/)

---

## Setup Guide

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Install Python 3.13

```bash
py install 3.13
```

### 3. Create a Virtual Environment

```bash
py -3.13 -m venv .venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
.\.venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/your_db_name
```

### 7. Run the Application

```bash
uvicorn main:app --reload
```

### 8. Open API Docs

- Swagger UI → http://localhost:8000/docs
- ReDoc → http://localhost:8000/redoc

---
