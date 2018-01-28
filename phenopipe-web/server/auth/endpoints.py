from flask import Blueprint
from flask import jsonify
from flask import request
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_refresh_token_required

from server.auth.authentication import authenticate

auth = Blueprint('auth', __name__, url_prefix='/auth')


@auth.route('/auth', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    user_info = authenticate(username, password)
    if user_info is None:
        return jsonify({"msg": "Bad username or password"}), 401
    ret = {
        'access_token': create_access_token(identity=user_info),
        'refresh_token': create_refresh_token(identity=user_info),
        'user_info': user_info
    }
    return jsonify(ret), 200


@auth.route('/reauth', methods=['POST'])
@jwt_refresh_token_required
def reauth():
    current_user = get_jwt_identity()
    ret = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(ret), 200
