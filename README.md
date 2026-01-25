# Weight Estimator Using Image Analysis

A Django + DRF backend for estimating object weight from images using OpenRouter's vision and text models.

## Features

- **JWT Authentication**: Secure user registration and login
- **Image Upload**: Store and manage uploaded images
- **Object Identification**: Uses OpenRouter vision models to identify objects in images
- **Interactive Q&A**: Generates follow-up questions based on image analysis
- **Weight Estimation**: Estimates weight with confidence ranges using text models
- **Modular Architecture**: Clean separation of concerns across Django apps

## Project Structure

```
weight_estimator/
  ├── manage.py
  ├── weight_estimator/          # Main project settings
  ├── accounts/                   # User authentication & profiles
  ├── media_store/                # Image upload handling
  ├── sessions/                   # Estimation sessions & Q&A
  └── estimates/                  # Weight estimates storage
```

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENROUTER_API_KEY
   ```

3. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create superuser** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run development server**:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/accounts/register/` - Register new user
- `POST /api/accounts/login/` - Login (returns JWT tokens)
- `POST /api/accounts/refresh/` - Refresh access token
- `GET /api/accounts/profile/` - Get user profile
- `PATCH /api/accounts/profile/` - Update user profile

### Media
- `POST /api/media/upload/` - Upload an image (multipart/form-data)

### Sessions
- `GET /api/sessions/` - List user's estimation sessions
- `POST /api/sessions/from-image/` - Create session from uploaded image
- `GET /api/sessions/{session_id}/` - Get session details
- `POST /api/sessions/{session_id}/answers/` - Submit answers to questions

### Estimates
- `GET /api/estimates/{estimate_id}/` - Get weight estimate details

## API Workflow

1. **Register/Login** → Get JWT access token
2. **Upload Image** → Get `image_id`
3. **Create Session** → Backend calls OpenRouter vision model to identify object and generate questions
4. **Submit Answers** → Backend calls OpenRouter text model to estimate weight
5. **View Estimate** → Get weight estimate with confidence range

## Environment Variables

See `.env.example` for all available configuration options.

**Required**:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

**Optional**:
- `OPENROUTER_VISION_MODEL` - Vision model (default: `qwen/qwen2.5-vl-32b-instruct`)
- `OPENROUTER_TEXT_MODEL` - Text model (default: `openai/gpt-4o-mini`)

## Technology Stack

- Django 5.0+
- Django REST Framework 3.14+
- JWT Authentication (djangorestframework-simplejwt)
- OpenRouter API (vision & text models)
- SQLite database
- Pillow (image handling)

## License

MIT

