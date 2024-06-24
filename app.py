from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Configuring the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbt_my_database_user:00xpUJcMgBTtkE4WUtLxqOZoz8mEQ4Oe@dpg-cpsk3j2j1k6c738otorg-a.oregon-postgres.render.com/mbt_my_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a User model
class Register(db.Model):
    __tablename__ = 'register'
    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    number=Column(String(80), nullable=False)
    dob = Column(String(15), nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/submit', methods=['POST'])
def submit():
    print("hieeeeeeeeeeeeeBackend")
    data = request.json
    print("Request data:", data)
    name = data.get('name')
    email = data.get('email')
    number=data.get('number')
    dob = data.get('dob')

    # Create a new User instance
    new_user = Register(name=name, email=email, number=number, dob=dob)

    # Add the new user to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Data submitted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
