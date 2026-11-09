from sqlalchemy.ext.hybrid import hybrid_property
from marshmallow import Schema, fields

from config import db, bcrypt

class User(db.Model):
    """
    Represents a user in the database

    Stores the user's username and securely hashed password
    Provides methods for password hashing and authentication
    """

    __tablename__ = 'users'

    # Database columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String)
    _password_hash = db.Column(db.String)

    @hybrid_property
    def password_hash(self):
        """
        Prevent direct access to the stored password hash

        Raises:
            Exception: If an attempt is made to read password_hash
        """
        raise Exception("Password hashes may not be viewed")


    @password_hash.setter
    def password_hash(self, password):
        """
        Hash and store a user's password using Bcrypt

        Converts the generated hash from bytes to a UTF-8 string
        before assigning it to the database column

        Args:
            password (str): The plaintext password to hash
        """
        hashed_password = bcrypt.generate_password_hash(password)
        decoded_hashed_password = hashed_password.decode("utf-8")
        self._password_hash = decoded_hashed_password

    def authenticate(self, password):
        """
        Verify a supplied password against the stored Bcrypt hash

        Args:
            password (str): The plaintext password to verify

        Returns:
            bool: True if the password matches, otherwise False
        """
        return bcrypt.check_password_hash(self._password_hash, password)

    def __repr__(self):
        """
        Return a readable representation of the user

        Returns:
            str: The user's username and database ID
        """
        return f'User {self.username}, ID: {self.id}'

class UserSchema(Schema):
    """
    Marshmallow schema for serializing User objects

    Includes only the user's ID and username, ensuring that
    password hashes are excluded from API responses
    """
    
    id = fields.Int()
    username = fields.String()