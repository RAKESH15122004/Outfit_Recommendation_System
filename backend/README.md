# Outfit Recommendation System - Backend

FastAPI-based backend for the AI-powered Outfit Recommendation System.

## Features

- **User Authentication & Authorization**: JWT-based auth with role-based access control
- **Wardrobe Management**: CRUD operations for wardrobe items with image upload
- **AI Recommendations**: Intelligent outfit generation based on preferences, weather, and occasions
- **Subscription Management**: Basic and Premium plans with Stripe integration
- **Admin Panel**: User management, analytics, and recommendation rule configuration
- **Security**: Encrypted data storage, secure file uploads, session management

## Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (python-jose)
- **File Upload**: Pillow for image processing
- **Payments**: Stripe
- **Migrations**: Alembic

## Setup

1. **Install dependencies**:
```bash
pip install -r requirements.txt
```

2. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Initialize database**:

   For **SQLite** (default, no setup needed):
   ```bash
   cd backend
   set PYTHONPATH=.   # Windows: set PYTHONPATH=.
   python scripts/init_db.py
   ```

   For **PostgreSQL**: set `DATABASE_URL` in `.env`, then:
   ```bash
   createdb outfit_db
   alembic upgrade head
   python scripts/init_db.py
   ```

4. **Run the server**:
   ```bash
   cd backend
   # Windows:
   run.bat
   # Or: set PYTHONPATH=. && python -m uvicorn app.main:app --reload
   # macOS/Linux:
   PYTHONPATH=. python -m uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Wardrobe
- `GET /api/v1/wardrobe/items` - Get wardrobe items
- `POST /api/v1/wardrobe/items` - Add wardrobe item
- `POST /api/v1/wardrobe/items/upload` - Upload wardrobe item with image
- `PUT /api/v1/wardrobe/items/{id}` - Update wardrobe item
- `DELETE /api/v1/wardrobe/items/{id}` - Delete wardrobe item

### Outfits
- `GET /api/v1/outfits` - Get user's outfits
- `GET /api/v1/outfits/{id}` - Get specific outfit
- `POST /api/v1/outfits/{id}/save` - Save outfit
- `POST /api/v1/outfits/{id}/rate` - Rate outfit

### Recommendations
- `POST /api/v1/recommendations/generate` - Generate AI recommendation
- `GET /api/v1/recommendations` - Get recommendation history
- `POST /api/v1/recommendations/{id}/accept` - Accept recommendation
- `POST /api/v1/recommendations/{id}/reject` - Reject recommendation

### Subscriptions
- `GET /api/v1/subscriptions/plans` - Get subscription plans
- `GET /api/v1/subscriptions/me` - Get current subscription
- `POST /api/v1/subscriptions/checkout` - Create checkout session
- `POST /api/v1/subscriptions/cancel` - Cancel subscription

### Admin
- `GET /api/v1/admin/stats` - Get dashboard statistics
- `GET /api/v1/admin/users` - Get all users
- `GET /api/v1/admin/subscriptions` - Get all subscriptions
- `POST /api/v1/admin/recommendation-rules` - Create recommendation rule

## Environment Variables

See `.env.example` for all required environment variables.

## Database Schema

The database includes the following main models:
- **Users**: User accounts with preferences
- **WardrobeItems**: User's clothing items
- **Outfits**: Generated outfit combinations
- **Subscriptions**: User subscription plans
- **Recommendations**: AI-generated recommendations
- **PaymentTransactions**: Payment history

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based access control (User/Admin)
- Secure file upload validation
- CORS configuration
- Session timeout management
