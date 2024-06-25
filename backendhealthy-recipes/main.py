from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
import requests
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel, cosine_similarity

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = '6ef104d88a94c15a238d47a743641026bf3d0ed3548f17e53724d1580e3011c8'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "http://localhost:3004", "methods": ["GET", "POST", "PUT", "DELETE"], "allow_headers": ["Content-Type", "Authorization"]}})


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    dietary_restrictions = db.Column(db.String(120), nullable=True)
    allergies = db.Column(db.String(120), nullable=True)

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    user = db.relationship('User', backref=db.backref('ratings', lazy=True))

@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    new_user = User(email=data['email'], password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User registered successfully'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        access_token = create_access_token(identity=user.id)
        return jsonify({'token': access_token}), 200
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/api/profile', methods=['GET'])
@jwt_required()
def get_profile():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    profile = {
        'dietary_restrictions': user.dietary_restrictions,
        'allergies': user.allergies
    }
    return jsonify(profile), 200

@app.route('/api/profile', methods=['POST'])
@jwt_required()
def update_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    user = User.query.get(user_id)
    user.dietary_restrictions = data.get('dietary_restrictions')
    user.allergies = data.get('allergies')
    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'}), 200

@app.route('/api/rate', methods=['POST'])
@jwt_required()
def rate_recipe():
    user_id = get_jwt_identity()
    data = request.get_json()
    rating = Rating(user_id=user_id, recipe_id=data['recipe_id'], rating=data['rating'])
    db.session.add(rating)
    db.session.commit()
    return jsonify({'message': 'Rating submitted successfully'}), 201

@app.route('/api/ratings', methods=['GET'])
@jwt_required()
def get_ratings():
    user_id = get_jwt_identity()
    ratings = Rating.query.filter_by(user_id=user_id).all()
    return jsonify([{ 'recipe_id': r.recipe_id, 'rating': r.rating } for r in ratings]), 200

@app.route('/api/recipes/<int:recipe_id>', methods=['GET', 'OPTIONS'])
@jwt_required()
def get_recipe(recipe_id):
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:3004')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response

    response = requests.get(f'https://api.spoonacular.com/recipes/{recipe_id}/information', params={
        'apiKey': '9528b23057c940a5a8d9ec75e55c1f99'
    })
    data = response.json()
    recipe = {
        "id": data.get("id"),
        "title": data.get("title"),
        "summary": data.get("summary"),
        "ingredients": [ingredient['name'] for ingredient in data.get("extendedIngredients", [])],
        "instructions": data.get("instructions")
    }
    return jsonify(recipe), 200


def preprocess_data(recipes):
    df = pd.DataFrame(recipes)
    df['ingredients'] = df['title'] + ' ' + df['summary']
    tfidf = TfidfVectorizer(stop_words='english')
    tfidf_matrix = tfidf.fit_transform(df['ingredients'])
    return df, tfidf_matrix

def train_model(tfidf_matrix):
    cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
    return cosine_sim

def get_recommendations(title, df, cosine_sim):
    indices = pd.Series(df.index, index=df['title']).drop_duplicates()
    idx = indices[title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:11]
    recipe_indices = [i[0] for i in sim_scores]
    return df.iloc[recipe_indices]

def collaborative_filtering(user_id):
    user_ratings = Rating.query.filter_by(user_id=user_id).all()
    if not user_ratings:
        return pd.Series([])

    all_ratings = Rating.query.all()
    df_ratings = pd.DataFrame([{'user_id': r.user_id, 'recipe_id': r.recipe_id, 'rating': r.rating} for r in all_ratings])
    user_rating_matrix = df_ratings.pivot_table(index='user_id', columns='recipe_id', values='rating').fillna(0)

    user_similarity = cosine_similarity(user_rating_matrix)
    user_similarity_df = pd.DataFrame(user_similarity, index=user_rating_matrix.index, columns=user_rating_matrix.index)

    similar_users = user_similarity_df[user_id].sort_values(ascending=False)[1:6].index
    similar_users_ratings = user_rating_matrix.loc[similar_users]

    recommended_recipes = similar_users_ratings.mean(axis=0).sort_values(ascending=False).index
    return recommended_recipes[:10]

@app.route('/api/recommendations', methods=['GET'])
@jwt_required()
def get_recommendations():
    user_id = get_jwt_identity()
    recommended_recipes = collaborative_filtering(user_id)
    if recommended_recipes.empty:
        return jsonify([]), 200

    response = requests.get('https://api.spoonacular.com/recipes/complexSearch', params={
        'apiKey': '9528b23057c940a5a8d9ec75e55c1f99',
        'includeRecipeInformation': True,
        'ids': ','.join(map(str, recommended_recipes))
    })
    recipes = response.json().get('results', [])
    return jsonify(recipes), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=7070)
