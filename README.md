# Mosquito Hunter ��

A web application that helps identify and track mosquito species through image submissions. Built with Flask backend and React frontend.

## Features

- 🖼️ Image upload and verification
- 🔍 Mosquito species identification
- 📊 Leaderboard system
- 👤 User profiles and authentication
- 📱 Responsive design
- 🔒 Secure file handling
- 📝 Detailed submission history

## Tech Stack

### Backend
- Python/Flask
- SQLite Database
- TensorFlow for image processing
- JWT Authentication

### Frontend
- React.js
- Axios for API calls
- Modern UI with CSS-in-JS
- Responsive design

## Project Structure

```
mosquito-hunter/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── image_routes.py
│   │   │   └── main_routes.py
│   │   ├── services/
│   │   │   ├── storage.py
│   │   │   └── verification.py
│   │   ├── database.py
│   │   └── __init__.py
│   ├── config.py
│   ├── requirements.txt
│   └── run.py
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Profile.js
│   │   │   └── Submission.js
│   │   ├── services/
│   │   │   └── api.js
│   │   └── App.js
│   └── package.json
└── README.md
```

## Setup Instructions

### Backend Setup

1. Create and activate virtual environment:
```bash
cd backend
python -m venv .venv
# On Windows
.venv\Scripts\activate
# On Unix or MacOS
source .venv/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file:
```bash
cp .env.example .env
```

4. Start the backend server:
```bash
python run.py
```

The backend server will run at `http://localhost:5000`

### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Start the development server:
```bash
npm start
```

The frontend will run at `http://localhost:3002`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile

### Image Submission
- `POST /api/submit` - Submit mosquito image
- `GET /api/submissions` - Get user submissions
- `GET /api/leaderboard` - Get leaderboard data

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- TensorFlow for image processing capabilities
- Flask and React communities for excellent documentation
- Contributors and maintainers of all dependencies 