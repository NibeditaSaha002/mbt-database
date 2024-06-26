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
    id = db.Column(db.Integer, primary_key=True)
    asid = db.Column(db.String, unique=True, nullable=False)
    name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.String, nullable=False)
    token = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    identity = db.Column(JSONB, nullable=False)
    status = db.Column(db.String, nullable=False)
    fingerprint = db.Column(JSONB, nullable=False)

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/submit', methods=['POST'])
def submit():
    data = request.json
    asid = data.get('asid')
    name = data.get('name')
    phone_number = data.get('phoneNumber')
    token = data.get('token')
    email = data.get('email')
    identity = data.get('identity')
    status = data.get('status')
    fingerprint = data.get('fingerprint')
    new_user = Register(
        asid=asid,
        name=name,
        phone_number=phone_number,
        token=token,
        email=email,
        identity=identity,
        status=status,
        fingerprint=fingerprint
    )

    # Add the new user to the session and commit to the database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Data submitted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
