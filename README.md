# Gym Management System

"My Gym" is a full-stack web application built using React (frontend) and Django REST Framework (backend). It is designed to help gym owners and managers run their gym operations more efficiently.

## Features

- User authentication and authorization (JWT)
- User profile management
- Dashboard with gym statistics and revenue
- Manage gym members — add, edit, delete
- Manage gym staff/trainers — add, edit, delete
- Create and manage gym classes with scheduling
- Accept and manage payments for memberships and classes
- Generate member cards as PDF
- Image uploads for members, trainers, sport types and products
- Notifications system

## Technologies Used

- React for the client-side UI
- Tailwind CSS for responsive design
- Django for the backend server
- Django REST Framework for the API
- SQLite (default) / PostgreSQL for the database
- JWT (SimpleJWT) for authentication
- ReportLab for PDF generation

## Project Structure

```
├── src/              # React frontend
├── public/           # Static assets
├── django-server/    # Django backend
│   ├── api/          # Models, views, serializers, urls
│   ├── gym/          # Django project settings
│   ├── manage.py
│   └── requirements.txt
```

## Getting Started

### Frontend

```bash
npm install
npm start
```

### Backend

```bash
cd django-server
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Environment Variables

Copy `.env.example` to `.env` inside `django-server/` and fill in:

```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=*
BASE_URL=http://localhost:8000
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register a new user |
| POST | `/api/auth/signin` | Login |
| POST | `/api/auth/changePassword` | Change password |
| GET | `/api/users` | List all users |
| GET/POST | `/api/members/` | List / add members |
| GET/PATCH/DELETE | `/api/members/:id/` | Get / update / delete member |
| GET | `/api/members/card/:id/` | Generate member PDF card |
| GET/POST | `/api/trainers/` | List / add trainers |
| GET/PATCH/DELETE | `/api/trainers/:id/` | Get / update / delete trainer |
| GET/POST | `/api/sportTypes/` | List / add sport types |
| DELETE | `/api/sportTypes/:id/` | Delete sport type |
| GET/POST | `/api/schedule/` | List / add schedules |
| GET/POST | `/api/payment/` | List / add payments |
| GET/POST | `/api/notifications/` | List / add notifications |
| GET/POST | `/api/products/` | List / add products |
| POST | `/api/upload/:type/` | Upload image (member/trainer/sportType/products) |
| GET | `/api/dashboard/` | Aggregated dashboard data |
