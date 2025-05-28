# sunysnacks
A simple remove website made with Fastapi and Bootstrap. It allows users to review meals and view other reviews of food locations on the SUNY Oneonta campus.

## Table of Contents
  * [Tech Stack](#Tech-Stack)
  * [Features](#Features)
  * [Dependencies](#Required-Dependencies)
  * [Installation](#Installation)
  * [Deployment](#Deployment)
  * [Ideas](#Future-Ideas)


## 🧰 Tech Stack

| Layer       | Tech                  |
|-------------|-----------------------|
| Frontend    | HTML, CSS, Bootstrap, Jinja2 |
| Backend     | FastAPI, Python, JSON       |
| Database    | SQLite                |
| Deployment  | Docker Render                |

## ✨ Features
- ✅ **Mobile-friendly** user interface
- ✅ **Rate** and **review** meals
- ✅ Browse other students’ reviews
- ✅ Clean, Bootstrap-based layout
- ✅ Custom star rating component
- ✅ SQLite-backed data model

## ⚙️ Required Dependencies
- **FastAPI**
- **Uvicorn**
- **SQLite**
- **Python version > 3.9**
- **UV** or a virtual environment
- **Jinja2**

## 🛠 Installation
1️⃣ Clone the repo 
```sh
git clone https://github.com/aston-evans/sunysnacks.git
```
2️⃣ Navigate into the project directory
```sh
cd sunysnacks
```
3️⃣ Install dependencies with `uv`
```sh
uv sync
```
4️⃣ Run the FastAPI server
```sh
uv run uvicorn snacks.main:app --reload
```
5️⃣ Open the browser and go to http://127.0.0.1:8000

### Cli Commands
- To initialized the db
```sh
uv run py_src/snacks/db.py init-db
```
- To delete/reset the db
```sh
uv run py_src/snacks/db.py reset-db
```

## Deployment
This project is currently deployed on Render - https://sunysnacks.onrender.com

## Future Ideas
- Using js tokens to allow people to crete an account.
- Give those same users a profile image.
- Allow reviews to be posted with an image of the food.
- Voting system that allows users to agree or disagree with reviews.
- A comment section. 
