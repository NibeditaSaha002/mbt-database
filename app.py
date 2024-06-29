# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from sqlalchemy.dialects.postgresql import JSONB
# from flask_cors import CORS

# app = Flask(__name__)
# CORS(app)

# # Configuring the PostgreSQL database
# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbt_my_database_user:00xpUJcMgBTtkE4WUtLxqOZoz8mEQ4Oe@dpg-cpsk3j2j1k6c738otorg-a.oregon-postgres.render.com/mbt_my_database'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# db = SQLAlchemy(app)

# # Define a User model
# class Register(db.Model):
#     __tablename__ = 'register'
#     id = db.Column(db.Integer, primary_key=True)
#     asid = db.Column(db.String, unique=True, nullable=False)
#     name = db.Column(db.String, nullable=False)
#     phone_number = db.Column(db.String, nullable=False)
#     token = db.Column(db.String, nullable=False)
#     email = db.Column(db.String, nullable=False)
#     identity = db.Column(JSONB, nullable=False)
#     status = db.Column(db.String, nullable=False)
#     fingerprint = db.Column(JSONB, nullable=False)

# # Create the database and tables
# with app.app_context():
#     db.create_all()

# @app.route('/submit', methods=['POST'])
# def submit():
#     try:
#         data = request.get_json()
#         asid = data.get('asid')
#         name = data.get('name')
#         phone_number = data.get('phoneNumber')
#         token = data.get('token')
#         email = data.get('email')
#         identity = data.get('identity')
#         status = data.get('status')
#         fingerprint = data.get('fingerprint')

#         # Create a new User instance
#         new_user = Register(
#             asid=asid,
#             name=name,
#             phone_number=phone_number,
#             token=token,
#             email=email,
#             identity=identity,
#             status=status,
#             fingerprint=fingerprint
#         )

#         # Add the new user to the session and commit to the database
#         db.session.add(new_user)
#         db.session.commit()

#         return jsonify({'message': 'Data submitted successfully'}), 200

#     except Exception as e:
#         # Log the exception (you can also log this to a file or monitoring service)
#         print(f"Error: {e}")
#         return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

# if __name__ == '__main__':
#     app.run(debug=True)


# 29/06/2024 edited

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuring the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbt_my_database_user:00xpUJcMgBTtkE4WUtLxqOZoz8mEQ4Oe@dpg-cpsk3j2j1k6c738otorg-a.oregon-postgres.render.com/mbt_my_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define a User model
class User(db.Model):
    __tablename__ = "MBI_USER_INFO"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT)
    email = db.Column(db.TEXT)
    phone_number = db.Column(db.TEXT)
    token = db.Column(db.TEXT)
    session = db.Column(db.JSON)
    active_session = db.Column(db.JSON)
    last_login = db.Column(db.DateTime, default=datetime.now)

    def __init__(self, name, email, phone_number, token, session, active_session):
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.token = token
        self.session = session
        self.active_session = active_session

# Create the database and tables
with app.app_context():
    db.create_all()

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone_number = data.get('phoneNumber')
        token = data.get('token')

        session = {
            "network": data['session']['network'],
            "deviceInfo": data['session']['deviceInfo']
        }

        active_session = {
            "network": data['active_session']['network'],
            "deviceInfo": data['active_session']['deviceInfo']
        }

        # Create a new User instance
        new_user = User(
            name=name,
            email=email,
            phone_number=phone_number,
            token=token,
            session=session,
            active_session=active_session
        )

        # Add the new user to the session and commit to the database
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'Data submitted successfully'}), 200

    except Exception as e:
        # Log the exception (you can also log this to a file or monitoring service)
        print(f"Error: {e}")
        return jsonify({'error': 'Internal Server Error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


