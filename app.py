


# 29/06/2024 edited

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import razorpay

app = Flask(__name__)
db = SQLAlchemy(app)
CORS(app)

# Configuring the PostgreSQL database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://mbt_my_database_user:00xpUJcMgBTtkE4WUtLxqOZoz8mEQ4Oe@dpg-cpsk3j2j1k6c738otorg-a.oregon-postgres.render.com/mbt_my_database'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

RAZORPAY_KEY_ID = 'rzp_test_WyHwnCdtRvbGyl'
RAZORPAY_KEY_SECRET = 'LeolpcDe95a523E09l9835fn'

# Razorpay client setup
# razorpay_client = razorpay.Client(auth=("RAZORPAY_KEY_ID", "RAZORPAY_KEY_SECRET"))
razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

class Wallet(db.Model):
    wallet_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, unique=True, nullable=False)
    balance = db.Column(db.Float, default=0.0)

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(100))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(50))
    payment_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.String(100))
    order_id = db.Column(db.String(100))
    user_id = db.Column(db.Integer)
    payment_methods = db.Column(db.JSON)
    amount = db.Column(db.Float)
    time = db.Column(db.DateTime)
    status = db.Column(db.String(50))

class Article(db.Model):
    article_id = db.Column(db.Integer, primary_key=True)
    article_name = db.Column(db.String(100))
    article_amount = db.Column(db.Float)

    def to_dict(self):
        return {
            'article_id': self.article_id,
            'article_name': self.article_name,
            'article_amount': self.article_amount
        }

@app.route('/create_order', methods=['POST'])
def create_order():
    data = request.json
    user_id = data['user_id']
    amount = data['amount']
    payment_methods = {"wallet": False, "directPayment": False, "subscriptionPayment": False, "walletToSubscriptionPayment": False}


    order = razorpay_client.order.create({
        'amount': int(amount * 100),  # amount in paise
        'currency': 'INR',
        'payment_capture': '1'
    })

    # new_payment = Payment(
    #     payment_id=None,
    #     order_id=order['id'],
    #     user_id=user_id,
    #     payment_methods=payment_methods,
    #     amount=amount,
    #     time=None,
    #     status='created'
    # )
    # db.session.add(new_payment)
    # db.session.commit()

    return jsonify({'order_id': order['id'], 'amount': amount})

@app.route('/verify_payment', methods=['POST'])
def verify_payment():
    data = request.json
    order_id = data['order_id']
    payment_id = data['payment_id']
    signature = data['signature']

    try:
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        })

        payment = Payment.query.filter_by(order_id=order_id).first()
        payment.payment_id = payment_id
        payment.status = 'success'
        payment.time = datetime.now()

        wallet = Wallet.query.filter_by(user_id=payment.user_id).first()
        if wallet:
            wallet.balance += payment.amount
        else:
            new_wallet = Wallet(user_id=payment.user_id, balance=payment.amount)
            db.session.add(new_wallet)

        new_transaction = Transaction(
            user_id=payment.user_id,
            payment_id=payment_id,
            amount=payment.amount,
            payment_method='Razorpay',
            payment_time=datetime.now()
        )
        db.session.add(new_transaction)

        db.session.commit()
        return jsonify({'status': 'success'})

    except razorpay.errors.SignatureVerificationError:
        payment = Payment.query.filter_by(order_id=order_id).first()
        payment.payment_id = payment_id
        payment.status = 'failed'
        db.session.commit()
        return jsonify({'status': 'failed'}), 400

@app.route('/wallet/<int:user_id>', methods=['GET'])
def get_wallet_balance(user_id):
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if wallet:
        return jsonify({'balance': wallet.balance})
    print(wallet.balance)
    return jsonify({'balance': 0}), 404

@app.route('/transactions/<int:user_id>', methods=['GET'])
def get_transactions(user_id):
    transactions = Transaction.query.filter_by(user_id=user_id).all()
    print("hieeeeee",transactions)
    return jsonify([{
        'id': transaction.id,
        'payment_id': transaction.payment_id,
        'amount': transaction.amount,
        'payment_method': transaction.payment_method,
        'payment_time': transaction.payment_time,
        'user_id': transaction.user_id
    } for transaction in transactions])


@app.route('/article/<int:article_id>', methods=['GET'])
def get_article(article_id):
    article = Article.query.get(article_id)
    if article:
        return jsonify({
            'article_id': article.article_id,
            'article_name': article.article_name,
            'article_amount': article.article_amount
        })
    return jsonify({'error': 'Article not found'}), 404

# @app.route('/articles', methods=['GET'])
# def get_articles():
#     try:
#         articles = Article.query.all()
#         articles_list = [article.to_dict() for article in articles]
#         return jsonify(articles_list), 200
#     except Exception as e:
#         # Print the full traceback for debugging
#         print(f"Error fetching articles: {e}")
#         print(traceback.format_exc())
#         return jsonify({"error": "Internal Server Error"}), 500


@app.route('/add_funds', methods=['POST'])
def add_funds():
    data = request.json
    user_id = data['user_id']
    amount = data['amount']
    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if wallet:
        wallet.balance += amount

        new_transaction = Transaction(
            user_id=user_id,
            payment_id=f'payment_{datetime.now().timestamp()}',
            amount=amount,
            payment_method='Razorpay',
            payment_time=datetime.now()
        )
        db.session.add(new_transaction)
        db.session.commit()
        return jsonify({'balance': wallet.balance})
    return jsonify({'error': 'Wallet not found'}), 404


@app.route('/pay_article', methods=['POST'])
def pay_article():
    data = request.json
    print("hiiiiiiiiiiiiiii",data)
    print("hiiiiiiiiiiiiii",data['user_id'])
    print("hiiiiiiiiiiiiii",data['article_id'])
    try:
        user_id = int(data['user_id'])
        article_id = int(data['article_id'])  # Ensure article_id is an integer

        print(user_id,article_id)
    except (KeyError, ValueError, TypeError):
        return jsonify({'status': 'failure', 'message': 'Invalid user_id or article_id'}), 400

    article = Article.query.get(article_id)
    if not article:
        return jsonify({'status': 'failure', 'message': 'Article not found'}), 404

    wallet = Wallet.query.filter_by(user_id=user_id).first()
    if wallet and wallet.balance >= article.article_amount:
        wallet.balance -= article.article_amount
        db.session.commit()

        # Log the transaction
        transaction = Transaction(
            user_id=user_id,
            payment_id=f'payment_{datetime.now().timestamp()}',
            amount=article.article_amount,
            payment_method='wallet',
            payment_time=datetime.now()
        )
        db.session.add(transaction)
        db.session.commit()

        return jsonify({'status': 'success'})
    return jsonify({'status': 'failure', 'message': 'Insufficient balance'}), 400

# @app.route('/pay_article', methods=['POST'])
# def pay_article():
#     try:
#         data = request.json  # Assuming JSON payload
#         user_id = data.get('user_id')  # Extracting user_id from JSON payload
        
#         # Validate and process the payment
#         # Example: Fetch user details, verify article ID, process payment, update transactions
        
#         return jsonify({'status': 'success', 'message': 'Payment processed successfully'})
    
#     except Exception as e:
#         print(f"Error processing payment: {str(e)}")
#         return jsonify({'status': 'error', 'message': 'Payment processing failed'}), 500


@app.route('/record_payment_failure', methods=['POST'])
def record_payment_failure():
    data = request.json
    razorpay_payment_id = data['razorpay_payment_id']
    razorpay_order_id = data['razorpay_order_id']

    data['status'] = 'failed'
    save_payment(data, 'failed')

    return jsonify({'status': 'Payment failed'})

def save_payment(data, status):
    payment = Payment(
        order_id=data['razorpay_order_id'],
        payment_id=data['razorpay_payment_id'],
        amount=data['amount'],
        time=datetime.now(),
        status=status,
        user_id=1,
    )
    db.session.add(payment)
    db.session.commit()

if __name__ == '__main__':
 with app.app_context():
    db.create_all()
    app.run(debug=True)


