# URL Shortener

A professional URL shortener service built with FastAPI, PostgreSQL, and modern web technologies.

## Features

- URL shortening with custom aliases
- User authentication and authorization
- Analytics tracking for URL visits
- URL expiration management
- Custom domain support
- Professional web interface

## Tech Stack

- Backend: FastAPI
- Database: PostgreSQL
- ORM: SQLAlchemy
- Authentication: JWT
- Frontend: HTML, CSS, JavaScript
- Deployment: AWS (EC2, RDS, Route 53)

## Setup Instructions

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file with the following variables:
   ```
   DATABASE_URL=postgresql://user:password@localhost:5432/urlshortener
   SECRET_KEY=your-secret-key
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```
5. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Project Structure

```
├── app/
│   ├── main.py
│   ├── config.py
│   ├── models/
│   ├── schemas/
│   ├── routes/
│   ├── services/
│   ├── templates/
│   └── static/
├── requirements.txt
├── README.md
└── .env
```

## API Documentation

Once the server is running, visit `/docs` for the interactive API documentation.

