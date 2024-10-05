from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Chat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    psw = db.Column(db.String(500), nullable=True)
    email = db.Column(db.String(100), unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<users {self.id}>"

class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    message_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<chat {self.id}>"
    
class Profiles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=True)
    old = db.Column(db.Integer, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __repr__(self):
        return f"<users {self.id}>"



def user_exists(email):
    return db.session.query(Users).filter_by(email=email).first() is not None

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=('POST', 'GET'))
def registration():
    if request.method == 'POST':

        email = request.form.get('email')

        if user_exists(email):
            return render_template('exc-regiser.html')
        else:       
            try:
                hash = generate_password_hash(request.form['psw'])
                u = Users(email=request.form['email'], psw=hash)
                db.session.add(u)
                db.session.flush()


                p = Profiles(name=request.form['name'], 
                             old=request.form['old'], user_id=u.id)
                db.session.add(p)
                db.session.commit()

                return render_template('index_2.html')

            except Exception as e:
                db.session.rollback()
                return jsonify({'error' : str(e)}), 500
            
    return render_template('register.html')


@app.route('/login', methods=('POST', 'GET'))
def login():
    if request.method == 'POST':

        email = request.form.get('email')

        if user_exists(email):
            return render_template('index_2.html')
        else:
            return render_template('index_3.html')

    return render_template('login.html')


@app.route('/chat', methods=('POST', 'GET'))
def chat():
    chat = Chat.query.order_by(Chat.date).all()
    
    if request.method == 'POST':
        
        try:
            messages = Chat(message=request.form['message'], message_id=Users.id)

            db.session.add(messages)
            db.session.flush()
            db.session.commit()
        except:
            db.session.rollback()
            return 'Ошибка'

    return render_template('chat.html', chat=chat)

@app.route('/home')
def index_home():
    return render_template('index_2.html')


if __name__ == '__main__':
    app.run(debug=True)