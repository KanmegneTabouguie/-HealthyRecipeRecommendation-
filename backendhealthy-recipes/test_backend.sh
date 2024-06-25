#!/bin/bash

# Base URL of the API
BASE_URL="http://127.0.0.1:7070/api"

# User credentials
EMAIL="test2@example.com"
PASSWORD="password"

# Function to log messages
log() {
    echo "$1"
    echo "$1" >> backend_test.log
}

# Clean up log file
> backend_test.log

log "Starting backend tests..."

# 1. Register a new user
log "Registering a new user..."
REGISTER_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/register" -H "Content-Type: application/json" -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

if [ "$REGISTER_RESPONSE" -eq 201 ]; then
    log "User registered successfully."
else
    log "Failed to register user. HTTP status code: $REGISTER_RESPONSE"
    exit 1
fi

# 2. Log in with the registered user
log "Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")
TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.token')

if [ "$TOKEN" != "null" ]; then
    log "Login successful. Token: $TOKEN"
else
    log "Failed to log in. Response: $LOGIN_RESPONSE"
    exit 1
fi

# 3. Fetch user profile
log "Fetching user profile..."
PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/profile")
log "Profile response: $PROFILE_RESPONSE"

# 4. Update user profile
log "Updating user profile..."
UPDATE_PROFILE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/profile" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"dietary_restrictions\": \"vegetarian\", \"allergies\": \"peanuts\"}")

if [ "$UPDATE_PROFILE_RESPONSE" -eq 200 ]; then
    log "User profile updated successfully."
else
    log "Failed to update profile. HTTP status code: $UPDATE_PROFILE_RESPONSE"
    exit 1
fi

# 5. Submit a recipe rating
log "Submitting a recipe rating..."
RATE_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/rate" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "{\"recipe_id\": 123, \"rating\": 4}")

if [ "$RATE_RESPONSE" -eq 201 ]; then
    log "Rating submitted successfully."
else
    log "Failed to submit rating. HTTP status code: $RATE_RESPONSE"
    exit 1
fi

# 6. Fetch user ratings
log "Fetching user ratings..."
RATINGS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/ratings")
log "Ratings response: $RATINGS_RESPONSE"

# 7. Fetch personalized recommendations
log "Fetching personalized recommendations..."
RECOMMENDATIONS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/recommendations")
log "Recommendations response: $RECOMMENDATIONS_RESPONSE"

log "Backend tests completed."
