# PixWeight - AI-Powered Weight Estimation

A Django + DRF backend with a modern frontend for estimating object weight from images using AI vision and text models. Features category-specific intelligence for Food, Packages, Pets, and People with specialized calculations and insights.

## Features

### Backend
- **JWT Authentication**: Secure user registration and login
- **Password Reset**: Forgot password functionality with account recovery
- **Image Upload**: Store and manage uploaded images with drag-and-drop support
- **Object Identification**: Uses AI vision models to identify objects in images
- **Category Detection**: Automatic classification (Food, Package, Pet, Person, General)
- **Interactive Q&A**: Generates category-specific follow-up questions
- **Weight Estimation**: Estimates weight with confidence ranges using text models
- **Category-Specific Calculations**:
  - **Food**: Calorie and macro-nutrient calculation
  - **Package**: Shipping cost estimates for multiple carriers
  - **Pet**: Health assessment based on breed standards
  - **Person**: BMI and body composition analysis
- **User Feedback System**: Collect actual weights for accuracy tracking
- **Modular Architecture**: Clean separation of concerns across Django apps

### Frontend
- **Modern UI**: Vibrant gradient theme with glass-morphism effects
- **Responsive Design**: Mobile-first approach with Bootstrap 5
- **Drag-and-Drop Upload**: Intuitive image upload with preview
- **Category-Specific Displays**: Tailored result pages for each category
- **Weight Comparisons**: Contextual reference objects ("About 3 smartphones")
- **User Feedback Forms**: Submit actual weights and ratings
- **Enhanced History**: Search, filter, and export (CSV) functionality
- **Educational Content**: "How It Works" page explaining the AI pipeline
- **Custom Modal System**: Lightweight modal implementation
- **Login & Registration**: Beautiful authentication pages
- **Password Recovery**: Two-step password reset flow
- **Dashboard**: User-friendly interface for managing estimation sessions

## Project Structure

```
weight_estimator/
  ├── manage.py
  ├── weight_estimator/          # Main project settings
  ├── accounts/                   # User authentication & profiles
  │   ├── views.py               # Register, Profile, ForgotPassword, ResetPassword
  │   └── urls.py                # Authentication endpoints
  ├── frontend/                   # Frontend templates & static files
  │   ├── templates/             # Django templates
  │   │   ├── landing.html       # Homepage
  │   │   ├── login.html         # Login with forgot password modal
  │   │   ├── register.html      # User registration
  │   │   ├── dashboard.html     # Main dashboard
  │   │   └── ...
  │   └── static/                # CSS, JS, images
  │       ├── css/style.css      # Custom theme with animations
  │       └── js/
  │           ├── api.js         # API client
  │           ├── common.js      # Shared utilities
  │           ├── login.js       # Login & password reset logic
  │           └── ...
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
   cp env.example .env
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

6. **Access the application**:
   - Frontend: `http://localhost:8000/`
   - API: `http://localhost:8000/api/`

## Category-Specific Features

### Food & Produce
- Automatic nutrition calculation (calories, protein, carbs, fat, fiber)
- Portion size assessment
- Cooking status consideration
- 50+ common foods in reference database

### Packages & Parcels
- Volumetric weight calculation
- Shipping cost estimates (USPS, FedEx, UPS, DHL)
- Dimensional weight analysis
- Domestic and international rates

### Pets
- Breed-specific health assessment
- Comparison against 25+ dog and cat breed standards
- Ideal weight range calculation
- Personalized health recommendations
- Life stage considerations (puppy/adult/senior)

### People (Body Composition)
- BMI calculation and categorization
- Body fat percentage estimation
- Ideal weight range suggestions
- Activity level consideration
- Health recommendations with disclaimers

## API Endpoints

### Authentication
- `POST /api/accounts/register/` - Register new user
  ```json
  {
    "username": "user123",
    "email": "user@example.com",  // optional
    "password": "securepassword"
  }
  ```

- `POST /api/accounts/login/` - Login (returns JWT tokens)
  ```json
  {
    "username": "user123",
    "password": "securepassword"
  }
  ```

- `POST /api/accounts/refresh/` - Refresh access token
  ```json
  {
    "refresh": "refresh_token_here"
  }
  ```

- `GET /api/accounts/profile/` - Get user profile (requires authentication)
- `PATCH /api/accounts/profile/` - Update user profile (requires authentication)

- `POST /api/accounts/forgot-password/` - Find account by username/email
  ```json
  {
    "identifier": "user123"  // or "user@example.com"
  }
  ```
  Returns:
  ```json
  {
    "success": true,
    "found": true,
    "username": "user123",
    "masked_email": "us***@example.com",
    "message": "Account found for username: user123"
  }
  ```

- `POST /api/accounts/reset-password/` - Reset password
  ```json
  {
    "username": "user123",
    "new_password": "newsecurepassword",
    "confirm_password": "newsecurepassword"
  }
  ```

### Media
- `POST /api/media/upload/` - Upload an image (multipart/form-data, requires authentication)
  - Form field: `image` (file)

### Sessions
- `GET /api/sessions/` - List user's estimation sessions with filtering (requires authentication)
  - Query params: `?search=`, `?category=`, `?status=`, `?sort_by=`, `?date_from=`, `?date_to=`
  - Returns: `{ "sessions": [...], "statistics": {...} }`
- `POST /api/sessions/from-image/` - Create session from uploaded image (requires authentication)
  ```json
  {
    "image_id": "uuid-here",
    "user_hint": "optional hint"
  }
  ```
- `GET /api/sessions/{session_id}/` - Get session details with estimate and category data (requires authentication)
- `POST /api/sessions/{session_id}/answers/` - Submit answers to questions (requires authentication)
  ```json
  {
    "answers": [
      {"question_id": "uuid", "value": "answer"},
      {"question_id": "uuid", "value": 42}
    ]
  }
  ```

### Estimates
- `GET /api/estimates/{estimate_id}/` - Get weight estimate details with category-specific data (requires authentication)
- `POST /api/estimates/{estimate_id}/feedback/` - Submit feedback (actual weight, rating)
- `GET /api/estimates/{estimate_id}/feedback/get/` - Retrieve submitted feedback

## Frontend Pages

### Public Pages
- `/` - Landing page with feature overview
- `/login/` - Login page with forgot password modal
- `/register/` - User registration page

### Authenticated Pages
- `/dashboard/` - Main dashboard with drag-and-drop upload
- `/history/` - View past sessions with search, filter, and CSV export
- `/profile/` - User profile management
- `/session/{session_id}/questions/` - Answer category-specific questions
- `/session/{session_id}/result/` - View estimate with category insights and feedback form

### Public Pages
- `/how-it-works/` - Educational page explaining the AI pipeline

## Password Reset Flow

1. **User clicks "Forgot password?"** on login page
2. **Step 1 - Find Account**: User enters username or email
3. **Backend validates** and returns account info (username + masked email)
4. **Step 2 - Reset Password**: User enters new password and confirmation
5. **Backend updates** password securely using Django's password hashing
6. **Success**: User can now log in with new password

## API Workflow

1. **Register/Login** → Get JWT access token
2. **Upload Image** → Get `image_id` (drag-and-drop supported)
3. **Create Session** → Backend:
   - Calls vision model to identify object
   - Detects category (food, package, pet, person, general)
   - Generates base + category-specific questions
4. **Submit Answers** → Backend:
   - Calls text model to estimate weight
   - Performs category-specific calculations
   - Creates specialized estimate records
5. **View Estimate** → Get:
   - Weight estimate with confidence range
   - Category-specific insights (nutrition, shipping, health, BMI)
   - Weight comparisons to common objects
   - Feedback form for accuracy tracking
6. **Submit Feedback** (Optional) → Provide actual weight for improvement

## Frontend Architecture

### Custom Modal System
The application uses a lightweight custom modal implementation that:
- **No Bootstrap JS dependency** - Pure CSS/JavaScript for better performance
- **Isolated rendering** - Uses CSS containment to prevent conflicts with page animations
- **Smooth transitions** - Simple CSS transitions instead of heavy animations
- **Accessible** - Keyboard navigation (Escape to close) and focus management

### Theme & Styling
- **Vibrant gradients** - Purple, teal, pink, orange color scheme
- **Glass-morphism effects** - Backdrop blur on cards and navbar
- **Animated backgrounds** - Subtle gradient animations (paused during modals)
- **Responsive design** - Mobile-first with Bootstrap 5 grid system

### JavaScript Architecture
- **API Client** (`api.js`) - Centralized API calls with JWT token management
- **Common Utilities** (`common.js`) - Shared functions (alerts, navigation, auth checks)
- **Page-specific scripts** - Each page has its own JS file for specific functionality

## Environment Variables

See `env.example` for all available configuration options.

**Required**:
- `OPENROUTER_API_KEY` - Your OpenRouter API key

**Optional**:
- `OPENROUTER_VISION_MODEL` - Vision model (default: `qwen/qwen2.5-vl-32b-instruct`)
- `OPENROUTER_TEXT_MODEL` - Text model (default: `openai/gpt-4o-mini`)

## Technology Stack

### Backend
- Django 5.0+
- Django REST Framework 3.14+
- JWT Authentication (djangorestframework-simplejwt)
- AI Vision & Text Models (OpenRouter/Groq)
- SQLite database
- Pillow (image handling)
- Category-specific calculation modules

### Frontend
- Bootstrap 5.3 (CSS only)
- Vanilla JavaScript (ES6+)
- Custom CSS with CSS Variables and Gradients
- Drag-and-Drop File Upload
- CSV Export functionality
- Dynamic category-specific rendering
- SVG icons (Feather Icons style)

### Data
- 43 food items with nutrition data
- 11 shipping carrier services with rates
- 25 pet breed standards (dogs and cats)
- 4 BMI categories with health recommendations
- Weight comparison reference objects

## Development Notes

### Modal Performance
The custom modal system was designed to prevent freezing issues caused by GPU compositing conflicts. Key optimizations:
- CSS `contain: layout style paint` for isolation
- Disabling page animations when modal is open
- No backdrop-filter on modal elements
- Simple opacity/transform transitions

### Security Considerations
- Password reset requires username verification
- Email addresses are masked in responses (e.g., `us***@example.com`)
- Passwords are hashed using Django's default password hasher
- JWT tokens stored in localStorage (consider httpOnly cookies for production)

## Academic Features

This project includes features designed for academic presentation and research:

- **Feedback System**: Collect actual weights to analyze estimation accuracy
- **CSV Export**: Export session history for statistical analysis
- **Category Breakdown**: Track which object types are most accurately estimated
- **Confidence Metrics**: Analyze correlation between confidence and accuracy
- **Educational Content**: "How It Works" page for explaining AI concepts
- **Comprehensive Logging**: All estimates stored with full metadata for research

## Management Commands

### Load Reference Data
```bash
python manage.py load_reference_data
```
Loads all reference data (food nutrition, shipping rates, breed standards, BMI categories) into the database.

## Future Enhancements

Potential improvements for future development:
- Real-time estimation using WebSockets
- Mobile app (React Native/Flutter)
- Advanced image preprocessing
- Multi-language support
- API rate limiting and usage analytics
- Social features (share estimates, leaderboards)
- Integration with smart scales for feedback collection

## Contributing

This is an academic project. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT
