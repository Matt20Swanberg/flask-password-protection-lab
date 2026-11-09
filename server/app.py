#!/usr/bin/env python3

from flask import request, session
from flask_restful import Resource

from config import app, db, api
from models import User, UserSchema

class Signup(Resource):
    """
    Handles new user registration and automatic login
    """

    def post(self):
        """
        Create a new user with a securely hashed password

        Saves the user to the database and stores their ID
        in the session to automatically authenticate them

        Returns:
            dict: Serialized user data with HTTP 201
        """
        # Retrieve username and password from the request
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")

        # Create a new user and hash their password
        new_user = User(username=username)
        new_user.password_hash = password

        # Save the new user to the database
        db.session.add(new_user)
        db.session.commit()

        # Automatically log in the newly created user
        session["user_id"] = new_user.id

        # Serialize the user for the JSON response
        user_json = UserSchema().dump(new_user)

        return user_json, 201


class Login(Resource):
    """
    Handles user login and password authentication
    """

    def post(self):
        """
        Authenticate an existing user using their credentials

        Verifies the supplied password against the stored Bcrypt
        hash and creates a session when authentication succeeds

        Returns:
            dict: Serialized user data with HTTP 200 on success
            dict: Error message with HTTP 401 on failure
        """
        # Retrieve login credentials from the request
        username = request.get_json().get('username')
        password = request.get_json().get('password')

        # Find the user by their username
        user = User.query.filter(User.username == username).first()

        # Verify the password and create an authenticated session
        if user and user.authenticate(password):

            session['user_id'] = user.id
            return UserSchema().dump(user), 200

        # Reject invalid login credentials
        return {'message': 'Invalid username or password'}, 401


class Logout(Resource):
    """
    Handles user logout by clearing their authenticated session
    """

    def delete(self):
        """
        Log out the current user by clearing their session ID

        Returns:
            str: Empty response with HTTP 204
        """
        # Clear the authenticated user's ID
        session['user_id'] = None

        return '', 204


class CheckSession(Resource):
    """
    Checks whether the current user has an active session
    """

    def get(self):
        """
        Retrieve the authenticated user from the current session

        Returns:
            dict: Serialized user data with HTTP 200 if authenticated
            str: Empty response with HTTP 204 if unauthenticated
        """
        # Retrieve the user ID from the session
        user_id = session.get('user_id')

        if user_id:
            # Find the user associated with the session
            user = User.query.filter(User.id == user_id).first()

            # Return user data if the user exists
            if user:
                return UserSchema().dump(user), 200

        # No valid authenticated user was found
        return '', 204


class ClearSession(Resource):
    """
    Clears stored page views and user authentication session data
    """

    def delete(self):
        """
        Reset page views and the authenticated user ID

        Returns:
            dict: Empty response with HTTP 204
        """
        # Clear session values
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

# Register authentication and session management endpoints
api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(ClearSession, '/clear', endpoint='clear')

# Start the Flask development server
if __name__ == '__main__':
    app.run(port=5555, debug=True)
