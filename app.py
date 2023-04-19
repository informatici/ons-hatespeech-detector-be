# coding=utf-8
#!/usr/bin/env python
#thanks to https://github.com/miguelgrinberg/REST-auth
import os
import logging
import sys

from flask import Flask, abort, request, jsonify, g, make_response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event
from flask_httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context as pwd_context
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from unsupervised_models import Hurtlext
from unsupervised_models import HateSpeechDictionary
from chatter_models import VeryDummyChatter,DummyChatter,Chatter

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://sys.stdout',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# initialization
app = Flask(__name__)
handler = logging.StreamHandler(sys.stdout)
app.logger.addHandler(handler)

app.config.from_pyfile('settings.py')

# General config
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{app.root_path}/db.sqlite"
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


# extensions
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
hurtlextModel = Hurtlext("dataset/")
hatespeechdictionary_model = HateSpeechDictionary("dataset/")

very_dummy_chatter = VeryDummyChatter()
dummy_chatter = DummyChatter()
main_chatter = Chatter()


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(64))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None    # valid token, but expired
        except BadSignature:
            return None    # invalid token
        user = User.query.get(data['id'])
        return user

# Add a default user on database creation, if needed
@event.listens_for(User.__table__, 'after_create')
def create_default_user(*args, **kwargs):
    if 'DEFAULT_USER' in app.config and app.config['DEFAULT_USER'] and 'DEFAULT_PASSWORD' in app.config and app.config['DEFAULT_PASSWORD']:
        user = User(username=app.config['DEFAULT_USER'])
        user.hash_password(app.config['DEFAULT_PASSWORD'])
        db.session.add(user)
        db.session.commit()
        print("Added default user \"" + app.config['DEFAULT_USER'] + "\" inferred from environment")

@auth.verify_password
def verify_password(username_or_token, password):
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route('/api-hs/signup', methods=['POST'])
def new_user():

    # Check if signup is enabled
    if not app.config['SIGNUP_ENABLED']:
        return (jsonify({'response': 'Signup disabled'}), 406)

    username = request.json.get('username')
    password = request.json.get('password')

    if username is None or password is None:
        abort(400)    # missing arguments
    if User.query.filter_by(username=username).first() is not None:
        abort(400)    # existing user
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()
    return (jsonify({'username': user.username}), 201)

@app.route('/')
def liveness_check():
    response = make_response("<h1>Success</h1>")
    response.status_code = 200
    return response

@app.route('/api-hs/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})


@app.route('/api-hs/signin', methods=['GET'])
@auth.login_required
def get_resource():
    return jsonify({'data': 'Hello, %s!' % g.user.username})


@app.route('/api-hs/predict/hurtlext', methods=['POST'])
@auth.login_required
def post_hurtlext_resource():
    response=[]

    source = request.json.get('source')
    items  = request.json.get('items')
    if source is None or items is None:
        abort(400)# missing arguments

    if not isinstance(items,list):
        abort(400) # malformed payload

    for item in items:
        if 'id' not in item or 'text' not in item:
            abort(400) # malformed payload

        if not isinstance(item['text'], str):
            abort(400)  # malformed payload

        score = hurtlextModel.inclusive_score(item['text'])
        print(score)
        if score > 0:
            prediction = 1
        else:
            prediction = 0
        response.append({'id':item['id'], 'prediction':prediction})

    return jsonify({'response': response})


@app.route('/api-hs/predict/hatespeechdictionary', methods=['POST'])
@auth.login_required
def post_hatespeechdictionary_resource():
    response=[]

    source = request.json.get('source')
    items  = request.json.get('items')
    if source is None or items is None:
        abort(400) # missing arguments

    if not isinstance(items,list):
        abort(400) # malformed payload

    for item in items:
        if 'id' not in item or 'text' not in item:
            abort(400) # malformed payload

        if not isinstance(item['text'], str):
            abort(400) # malformed payload

        score, dimensions, tokens = hatespeechdictionary_model.score(item['text'])
        if score > 0:
            prediction = 1
        else:
            prediction = 0
        response.append({'id':item['id'], 'prediction':prediction, 'dimension': " ".join(dimensions), 'tokens': " ".join(sorted(x['word'] for x in tokens)), 'score' : score})

    return jsonify({'response': response})


@app.route('/api-hs/chatter/verydummychatter', methods=['POST'])
@auth.login_required
def post_very_dummy_chatter_resource():

    source = request.json.get('source')
    text = request.json.get('text')
    if source is None or text is None:
        abort(400) # missing arguments

    if not isinstance(text,str):
        abort(400) # malformed payload

    answer=very_dummy_chatter.return_answer()

    return jsonify({'response': answer})


@app.route('/api-hs/chatter/dummychatter', methods=['POST'])
@auth.login_required
def post_dummy_chatter_resource():

    source = request.json.get('source')
    text  = request.json.get('text')
    if source is None or text is None:
        abort(400)# missing arguments

    if not isinstance(text,str):
        abort(400) # malformed payload

    answer=dummy_chatter.return_answer(text)

    return jsonify({'response': answer})


@app.route('/api-hs/chatter/mainchatter', methods=['POST'])
@auth.login_required
def post_main_chatter_resource():

    source = request.json.get('source')
    text = request.json.get('text')
    if source is None or text is None:
        abort(400)# missing arguments

    if not isinstance(text,str):
        abort(400) # malformed payload

    answer=main_chatter.return_answer(text)

    return jsonify({'response': answer})

# Main block
# Create database if it doesn't exist
if not os.path.exists('db.sqlite'):
    with app.app_context():
        db.create_all()
