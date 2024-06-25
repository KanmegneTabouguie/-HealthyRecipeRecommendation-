# Healthy Recipe Recommendation  API

This is a Flask-based backend API for a Healthy Recipe Recommendation system. It provides endpoints for user registration, login, profile management, rating recipes, and getting personalized recipe recommendations.

## Getting Started

### Prerequisites

- Python 3.x
- pip (Python package installer)

### Installation

1. Clone the repository:
    
    ```
    git clone <repository-url>
    cd healthy-recipe-backend
    
    ```
    
2. Create and activate a virtual environment:
    
    ```
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\\Scripts\\activate`
    
    ```
    
3. Install the required packages:
    
    ```
    pip install -r requirements.txt
    
    ```
    

### Configuration

Update the `main.py` file with your JWT secret key and Spoonacular API key:

```python
app.config['JWT_SECRET_KEY'] = 'your_secret_key'
apiKey = 'your_spoonacular_api_key'

```

### Running the Application

1. Initialize the database and run the Flask application:
    
    ```
    python main.py
    
    ```
    
2. The API will be available at `http://127.0.0.1:7070`.

### API Endpoints

### User Registration

- **Endpoint:** `/api/register`
- **Method:** `POST`
- **Description:** Registers a new user.
- **Request Body:**
    
    ```json
    {
        "email": "test@example.com",
        "password": "password"
    }
    
    ```
    
- **Response:**
    
    ```json
    {
        "message": "User registered successfully"
    }
    
    ```
    

### User Login

- **Endpoint:** `/api/login`
- **Method:** `POST`
- **Description:** Logs in a user.
- **Request Body:**
    
    ```json
    {
        "email": "test@example.com",
        "password": "password"
    }
    
    ```
    
- **Response:**
    
    ```json
    {
        "token": "<JWT_TOKEN>"
    }
    
    ```
    

### Get User Profile

- **Endpoint:** `/api/profile`
- **Method:** `GET`
- **Description:** Fetches the profile of the logged-in user.
- **Headers:**
    
    ```
    Authorization: Bearer <JWT_TOKEN>
    
    ```
    
- **Response:**
    
    ```json
    {
        "dietary_restrictions": "vegetarian",
        "allergies": "peanuts"
    }
    
    ```
    

### Update User Profile

- **Endpoint:** `/api/profile`
- **Method:** `POST`
- **Description:** Updates the profile of the logged-in user.
- **Headers:**
    
    ```
    Authorization: Bearer <JWT_TOKEN>
    
    ```
    
- **Request Body:**
    
    ```json
    {
        "dietary_restrictions": "vegetarian",
        "allergies": "peanuts"
    }
    
    ```
    
- **Response:**
    
    ```json
    {
        "message": "Profile updated successfully"
    }
    
    ```
    

### Rate Recipe

- **Endpoint:** `/api/rate`
- **Method:** `POST`
- **Description:** Submits a rating for a recipe.
- **Headers:**
    
    ```
    Authorization: Bearer <JWT_TOKEN>
    
    ```
    
- **Request Body:**
    
    ```json
    {
        "recipe_id": 123,
        "rating": 4
    }
    
    ```
    
- **Response:**
    
    ```json
    {
        "message": "Rating submitted successfully"
    }
    
    ```
    

### Get User Ratings

- **Endpoint:** `/api/ratings`
- **Method:** `GET`
- **Description:** Fetches the ratings submitted by the logged-in user.
- **Headers:**
    
    ```
    Authorization: Bearer <JWT_TOKEN>
    
    ```
    
- **Response:**
    
    ```json
    [
        {
            "recipe_id": 123,
            "rating": 4
        }
    ]
    
    ```
    

### Get Recommendations

- **Endpoint:** `/api/recommendations`
- **Method:** `GET`
- **Description:** Fetches personalized recipe recommendations for the logged-in user.
- **Headers:**
    
    ```
    Authorization: Bearer <JWT_TOKEN>
    
    ```
    
- **Response:**
    
    ```json
    [
        {
            "id": 1,
            "title": "Recipe Title",
            "summary": "Recipe Summary",
            "ingredients": ["ingredient1", "ingredient2"]
        },
        ...
    ]
    
    ```
    

### Note

Ensure that the backend server is running and the frontend is properly configured to interact with the backend API. Use tools like Postman or curl to test the API endpoints during development.
