from . import main
from flask import request, jsonify, make_response, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from ..models import User, Covid, Comment
import uuid
from .. import db
import jwt
from functools import wraps
from datetime import datetime, timedelta


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):  # arbitrary functions
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
            if not current_user:
                return jsonify({'message': 'cannot perfom that function!'})
        except:
            return jsonify({'message': 'Token is invalid!'}), 401
        return f(*args, **kwargs)
    return decorated


@main.route('/user', methods=['GET'])
@token_required
def get_all_users():
    users = User.query.all()
    output = []
    for user in users:
        user_data = {}
        user_data['public_id'] = user.public_id
        user_data['name'] = user.name
        user_data['password'] = user.password
        user_data['email'] = user.email

        output.append(user_data)

    return jsonify({'users': output})


@main.route('/user/<public_id>', methods=['GET'])
@token_required
def get_one_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    user_data = {}
    user_data['public_id'] = user.public_id
    user_data['name'] = user.name
    user_data['password'] = user.password
    user_data['email'] = user.email

    return jsonify({'user': user_data})


@main.route('/user', methods=['POST'])
def create_user():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    new_user = User(public_id=str(
        uuid.uuid4()), name=data['name'], password=hashed_password, email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'new user created!'})


@main.route('/user/<public_id>', methods=['DELETE'])
@token_required
def delete_user(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if not user:
        return jsonify({'message': 'No user found!'})
    db.session.delete(user)
    db.session.commit()
    return jsonify({'message': 'User has been deleted'})


@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or not data["email"] or not data["password"]:
        return make_response('Missing email or password fields', 401, {'WWW-Authenticate': 'Basic realm = "Login required!"'})

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return jsonify({'message': 'Wrong email or password'}), 401
    if check_password_hash(user.password, data["password"]):
        token = jwt.encode(
            {
                'public_id': user.public_id,
                'exp':  datetime.utcnow() + timedelta(minutes=720)
            }, current_app.config["SECRET_KEY"])
        return jsonify ({'token' : token, "user": user.as_dict()}), 200
    return jsonify({'message': 'Wrong email or password'}), 401


@main.route('/user/<public_id>/post', methods=['POST'])
@token_required
def create_post(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if user:
        data = request.get_json()
        new_post = Covid(country=data['country'], cases=data['cases'], tests=data['tests'], deaths=data['deaths'],
                         recovered=data['recovered'], date_created=data['date_created'], user_id=user.id)
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'message': 'new covid post created!'})
    return jsonify({'message': 'No user found!'})


@main.route('/user/post', methods=['GET'])
def get_all_posts():
    posts = Covid.query.all()
    output = []
    for post in posts:
        post_data = {}
        post_data['country'] = post.country
        post_data['cases'] = post.cases
        post_data['tests'] = post.tests
        post_data['deaths'] = post.deaths
        post_data['recovered'] = post.recovered
        post_data['date_created'] = post.date_created
        post_data['user_id'] = post.user_id
        post_data['id'] = post.id

        output.append(post_data)

    return jsonify({'posts': output})


@main.route('/post/<int:id>', methods=['GET'])
@token_required
def get_post(id):

    post = Covid.query.filter_by(id=id).first()
    if not post:
        return jsonify({'message': 'No post found!'})
    post_data = {}
    post_data['country'] = post.country
    post_data['cases'] = post.cases
    post_data['tests'] = post.tests
    post_data['deaths'] = post.deaths
    post_data['recovered'] = post.recovered
    post_data['date_created'] = post.date_created
    post_data['id'] = post.id

    return jsonify({'post': post_data})


@main.route('/post/<post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id):
    post = Covid.query.filter_by(id=post_id).first()
    if not post:
        return jsonify({'message': 'No post found!'})
    db.session.delete(post)
    db.session.commit()
    return jsonify({'message': 'Post has been deleted'})


@main.route('/user/<public_id>/post', methods=['PUT'])
@token_required
def update_post(public_id):
    user = User.query.filter_by(public_id=public_id).first()
    if user:
        data = request.get_json()
        new_post = Covid(country=data['country'], cases=data['cases'],
                         date_created=data['date_created'], user_id=data['user_id'])
        db.session.add(new_post)
        db.session.commit()
        return jsonify({'message': 'covid post successfully updated!'})
    return jsonify({'message': 'No user found!'})


@main.route('/user/<public_id>/post/<int:post_id>/comment', methods=['POST'])
@token_required
def create_comment(public_id, post_id):
    user = User.query.filter_by(public_id=public_id).first()
    post = Covid.query.filter_by(id=post_id).first()
    if user:
        data = request.get_json()
        new_comment = Comment(
            text=data['text'], date_created=data['date_created'], author=user.id, post=post.id)
        db.session.add(new_comment)
        db.session.commit()
        return jsonify({'message': 'new comment posted'})
    return jsonify({'message': 'No user found!'})


@main.route('/post/<int:id>/comments', methods=['GET'])
@token_required
def get_all_comments(id):
    post = Covid.query.filter_by(id=id).first()
    if not post:
        return jsonify({'message': f'Post with id: {id} not found!'}), 404

    comments = post.comments
    output = []
    for comment in comments:
        comment_data = {}
        comment_data['text'] = comment.text
        comment_data['date_created'] = comment.date_created
        user = User.query.filter_by(id=comment.author).first()
        comment_data['author'] = user.name
        comment_data["id"] = comment.id

        output.append(comment_data)

    return jsonify({'comments': output})


@main.route('/user/post/comment/<author>', methods=['GET'])
@token_required
def get_single_comment(author):
    comment = Comment.query.filter_by(author=author).first()
    if not comment:
        return jsonify({'message': 'No post found!'})
    comment_data = {}
    comment_data['text'] = comment.text
    comment_data['date_created'] = comment.date_created

    return jsonify({'user_comment': comment_data})


@main.route('/comment/<int:id>', methods=['DELETE'])
@token_required
def delete_comment( id):
    comment = Comment.query.filter_by(id=id).first()
    if not comment:
        return jsonify({'message': 'No comment found!'})
    db.session.delete(comment)
    db.session.commit()
    return jsonify({'message': 'Comment has been deleted'})
