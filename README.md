# PhotoShare API 🚀

A powerful and secure REST API for sharing and managing photos, built with the modern FastAPI framework. This application provides a comprehensive suite of features including photo uploading with Cloudinary transformations, QR-code generation, commenting, rating systems, and robust user role management.


## ✨ Key Features

- **🔐 Secure Authentication:**
  - JWT-based authentication (Access & Refresh tokens).
  - Role-based access control: **User**, **Moderator**, **Administrator**.
  - Secure logout mechanism with token blacklisting.

- **📸 Photo Management:**
  - Upload photos with descriptions and automatic timestamping.
  - **Tagging System:** Add up to 5 unique tags per photo for easy categorization.
  - **Cloudinary Integration:** Perform image transformations (resize, crop, effects) on the fly.
  - **QR Codes:** Generate unique QR codes for instant access to transformed images.

- **💬 Social Interaction:**
  - **Comments:** Users can discuss photos. Authors can edit their comments; Moderators/Admins can moderate content.
  - **Rating System:** 5-star rating logic. Calculates average score. Prevents self-rating and duplicate votes.

- **🔍 Advanced Search & Filtering:**
  - Search photos by keywords or specific tags.
  - Sort and filter results by average rating or upload date.
  - Filter photos by specific users.

- **👤 User Profiles**
  - Public profiles displaying user statistics.
  - Dedicated endpoint for users to update their own profile information.

- **🛡️ Admin Control**
  - Administrators have full CRUD rights on all content.
  - Ban/Unban functionality to restrict user access.

## 🛠️ Technology Stack

- **Python 3.11+** — Core programming language.
- **FastAPI** — High-performance web framework for building APIs.
- **SQLAlchemy (Asyncpg)** — Asynchronous ORM for database interactions.
- **PostgreSQL** — Primary relational database.
- **Redis** — In-memory data store for caching and session management.
- **Docker & Docker Compose** — Containerization for easy deployment.
- **Poetry** — Dependency management and packaging.
- **Cloudinary** — Cloud-based image management service.
- **Pytest** — Testing framework ensuring code reliability.


# 🚀 Getting Started

Follow these steps to set up and run the project locally from scratch.

## 1. Prerequisites

Ensure you have **Docker** and **Docker Compose** installed on your machine.

### 1. Install Python

If you don't have Python installed, download and install the latest version from the official website:

- **[Download Python](https://www.python.org/downloads/)**

### 2. Install Poetry

Once Python is installed, install **Poetry** using the command appropriate for your system:

**Linux, macOS, Windows (WSL):**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

**Windows (Powershell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```

**Add Poetry to your PATH:**

The installer creates a `poetry` wrapper in a specific directory. If the command `poetry` is not found, add the following to your PATH:

* **Unix/Linux/macOS:** `$HOME/.local/bin`
* **Windows:** `%APPDATA%\Python\Scripts`

Alternatively, you can always use the full path to the poetry binary:

* **Unix/Linux:** `~/.local/share/pypoetry/venv/bin/poetry`
* **Windows:** `%APPDATA%\pypoetry\venv\Scripts\poetry`
* **macOS:** `~/Library/Application Support/pypoetry/venv/bin/poetry`

## 2. Clone the Repository
```bash
git clone https://github.com/TStakhniuk/photoshare-api.git
cd photoshare-api
```

## 3. Install Dependencies

Create a virtual environment and install all required packages:
```bash
poetry install
```

## 4. Set Up Environment Variables

Copy the example environment file and configure your credentials.
```bash
cp .env.example .env
```

Open the `.env` file and fill in the following details:
```env
# Database PostgreSQL
POSTGRES_USER=your_db_user
POSTGRES_PASSWORD=your_db_password
POSTGRES_DB=your_db_name
POSTGRES_TEST_DB=your_test_db_name
POSTGRES_HOST=your_db_host
POSTGRES_PORT=your_db_port
DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}
DATABASE_TEST_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_TEST_DB}

# JWT authentication
SECRET_KEY=your_secret_key_here
ALGORITHM=your_algorithm

# Redis
REDIS_HOST=your_redis_host
REDIS_PORT=your_redis_host
REDIS_URL=redis://${REDIS_HOST}:${REDIS_PORT}/0

# Cloudinary
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

## 5. Start with Docker Compose

Build and start the API, Database, and Redis containers:
```bash
docker-compose up -d --build
```

The API will be available at `http://localhost:8000`.

## 6. Run Database Migrations

Apply the database schema using Alembic inside the container:
```bash
docker-compose exec web alembic upgrade head
```

### 7. Access the Documentation

Once the application is running, you can access the interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`


## 📖 API Endpoints

A brief overview of the available endpoints. For full details and to try them out live, please visit the interactive Swagger UI documentation.

### 🔐 Authentication (`/auth`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/auth/signup` | Register a new user account |
| **POST** | `/auth/login` | Log in and receive access/refresh tokens |
| **POST** | `/auth/refresh` | Refresh an expired access token |
| **POST** | `/auth/logout` | Log out and invalidate the current token |

### 👤 Users (`/users`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/users/me` | Get current user's profile info |
| **PUT** | `/users/me` | Update current user's profile |
| **GET** | `/users/{username}` | Get public profile of a user |
| **PATCH** | `/users/{username}/ban` | Ban a user (Admin only) |
| **PATCH** | `/users/{username}/unban` | Unban a user (Admin only) |

### 📸 Photos (`/photos`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/photos/` | Upload a new photo |
| **GET** | `/photos/` | Get a paginated list of all photos |
| **GET** | `/photos/search` | Search photos by keyword, tag, rating, or date |
| **GET** | `/photos/{photo_id}` | Get details of a specific photo |
| **PUT** | `/photos/{photo_id}` | Update photo description |
| **DELETE** | `/photos/{photo_id}` | Delete a photo |
| **GET** | `/photos/user/{user_id}` | Get all photos uploaded by a specific user |
| **POST** | `/photos/{photo_id}/transform` | Apply transformations (crop, filter, blur) |
| **GET** | `/photos/{photo_id}/transformations`| Get list of applied transformations |
| **GET** | `/photos/{photo_id}/qr` | Get QR code linking to the photo |

### 💬 Comments (`/comments`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/comments/{photo_id}` | Add a comment to a photo |
| **PUT** | `/comments/{comment_id}` | Edit a comment |
| **DELETE** | `/comments/{comment_id}` | Delete a comment (Admin/Moderator) |

### ⭐ Ratings (`/ratings`)

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/ratings/{photo_id}` | Rate a photo (1-5 stars) |
| **GET** | `/ratings/{photo_id}/average` | Get average rating and vote count |
| **GET** | `/ratings/{photo_id}` | Get all individual ratings (Admin/Mod) |
| **DELETE** | `/ratings/{rating_id}` | Remove a rating (Admin/Mod) |


## 👥 Authors

Developed by the **PhotoShare Team**.