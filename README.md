# Django Blog Starter

This repository contains a minimal, runnable Django blog starter with features:
- User registration, login, logout, password reset (Django auth)
- CRUD for posts with categories and tags
- Comments, like/dislike, search, pagination
- Author profiles, image uploads, slugs, featured posts
- Basic admin integration, static files, and dark-mode toggle

Quick start (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
cd .\
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Media files are saved to `media/` and static files are in `static/`.
