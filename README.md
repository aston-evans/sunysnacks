# sunysnacks
A simple remove website made with Fastapi and Bootstrap. It allows users to review meals and view other reviews of food locations on the SUNY Oneonta campus.

## Table of Contents
  * [Tech Stack](#Tech-Stack)
  * [Features](#Features)
  * [Dependencies](#Required-Dependencies)
  * [Installation](#Installation)
  * [Deployment](#Deployment)


## 🛠 Tech Stack
- **Frontend**: HTML, CSS, Bootstrap, Jinja2
- **Backend**: FastAPI, Python
- **Database**: SQLite
- **Deployment**: Render

## Features
-✅ Mobile-friendly UI  
-✅ Review and rate snacks 

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
git clone https://github.com/aston-evans/portfolio.git
```
2️⃣ Navigate into the project directory
```sh
cd sunysnacks
```
3️⃣ Install dependencies with `uv`
```sh
uv install .
```
4️⃣ Run the FastAPI server
```sh
uv run uvicorn snacks.main:app --reload
```
5️⃣ Open the browser and go to http://127.0.0.1:8000

## Deployment
This project is currently deployed on Render - https://sunysnacks.onrender.com
