#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

class Signup(Resource):

    def post(self):
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        new_user = User(username=username)
        new_user.password_hash = password

        db.session.add(new_user)
        db.session.commit()

        session["user_id"] = new_user.id

        user_json = UserSchema().dump(new_user)
        
        return user_json, 201

class ClearSession(Resource):

    def delete(self):
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(ClearSession, '/clear', endpoint='clear')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
