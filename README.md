# AIPython Web API Project

A modern Python web API project using FastAPI with clean architecture and design patterns.

## 🏗️ Architecture

This project follows clean architecture principles with the following layers:

- **API Layer**: FastAPI routes and controllers
- **Service Layer**: Business logic and use cases
- **Repository Layer**: Data access abstraction
- **Domain Layer**: Core business entities
- **Infrastructure Layer**: External dependencies (database, external APIs)

## 🚀 Features

- **FastAPI Framework**: Modern, fast web framework for building APIs
- **Dependency Injection**: Clean separation of concerns
- **Repository Pattern**: Abstracted data access layer
- **Service Layer**: Business logic encapsulation
- **Pydantic Models**: Data validation and serialization
- **SQLAlchemy ORM**: Database abstraction
- **Alembic Migrations**: Database schema management
- **Pytest Testing**: Comprehensive test coverage
- **Logging**: Structured logging with different levels
- **Configuration Management**: Environment-based configuration
- **Error Handling**: Centralized exception handling
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **WOSA Reports System**: Complete system for processing and analyzing WOSA JSON reports
- **User Management**: Full CRUD operations for user management
- **Modern Web Interface**: Beautiful HTML5/CSS3/JavaScript frontend

## 🛠️ Installation

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- PostgreSQL (or SQLite for development)

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/waltercjunior/AIPython.git
   cd AIPython
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Run database migrations**
   ```bash
   alembic upgrade head
   ```

6. **Start the development server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 📖 Usage

### API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Example API Calls

```bash
# Get all users
curl -X GET "http://localhost:8000/api/v1/users"

# Create a new user
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Get user by ID
curl -X GET "http://localhost:8000/api/v1/users/1"
```

## 📁 Project Structure

```
AIPython/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py              # Configuration management
│   ├── database.py            # Database connection
│   ├── dependencies.py        # Dependency injection
│   ├── exceptions.py          # Custom exceptions
│   ├── middleware.py          # Custom middleware
│   ├── api/                   # API routes
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       └── auth.py
│   ├── core/                  # Core business logic
│   │   ├── __init__.py
│   │   ├── entities/          # Domain entities
│   │   │   ├── __init__.py
│   │   │   └── user.py
│   │   ├── repositories/      # Repository interfaces
│   │   │   ├── __init__.py
│   │   │   └── user_repository.py
│   │   └── services/          # Business services
│   │       ├── __init__.py
│   │       └── user_service.py
│   ├── infrastructure/        # External dependencies
│   │   ├── __init__.py
│   │   ├── database/          # Database implementations
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   └── repositories/
│   │   │       ├── __init__.py
│   │   │       └── user_repository_impl.py
│   │   └── external/          # External API clients
│   │       ├── __init__.py
│   │       └── email_service.py
│   └── schemas/               # Pydantic models
│       ├── __init__.py
│       ├── user.py
│       └── common.py
├── alembic/                   # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── tests/                     # Test files
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_repositories/
└── scripts/                   # Utility scripts
    ├── init_db.py
    └── seed_data.py
```

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_api/test_users.py
```

## 📊 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit your changes**
   ```bash
   git commit -m 'Add some amazing feature'
   ```
4. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Write meaningful commit messages
- Add tests for new features
- Update documentation as needed
- Use type hints throughout the codebase

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

If you have any questions or need help:

- Open an [issue](https://github.com/waltercjunior/AIPython/issues)
- Check the [documentation](docs/)
- Review [existing discussions](https://github.com/waltercjunior/AIPython/discussions)

## 📞 Contact

- **Author**: Walter Junior
- **Email**: waltercjunior@gmail.com
- **GitHub**: [@waltercjunior](https://github.com/waltercjunior)

## 🙏 Acknowledgments

- Thanks to the Python community for excellent libraries and tools
- Inspiration from various AI/ML projects and tutorials
- Contributors and users who help improve this project

---

⭐ **Star this repository if you found it helpful!**

## 📈 Roadmap

- [ ] Add authentication and authorization
- [ ] Implement caching with Redis
- [ ] Add API rate limiting
- [ ] Create Docker configuration
- [ ] Add CI/CD pipeline
- [ ] Performance optimizations
- [ ] Add monitoring and metrics

*Last updated: [Current Date]*