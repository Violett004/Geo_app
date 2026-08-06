import hashlib
import os
from sqlalchemy.orm import Session
from models.user_model import UserModel

class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_password(password: str, salt: bytes = None) -> str:
        """Szyfrowanie PBKDF2 z wygenerowaną solą (Salt)"""
        if salt is None:
            salt = os.urandom(16)
        # PBKDF2 z HMAC-SHA256 i 100,000 iteracji
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return salt.hex() + '$' + key.hex()

    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """Weryfikacja podanego hasła z zapisanym hashem i solą"""
        try:
            salt_hex, key_hex = stored_password.split('$')
            salt = bytes.fromhex(salt_hex)
            new_key = hashlib.pbkdf2_hmac('sha256', provided_password.encode('utf-8'), salt, 100000)
            return new_key.hex() == key_hex
        except Exception:
            # Kompatybilność wsteczna ze starym prostopadłym SHA256
            return stored_password == hashlib.sha256(provided_password.encode('utf-8')).hexdigest()

    def get_user_by_username(self, username: str):
        return self.db.query(UserModel).filter(UserModel.username == username).first()

    def get_user_by_email(self, email: str):
        return self.db.query(UserModel).filter(UserModel.email == email).first()

    def create_user(self, username: str, email: str, password: str):
        hashed_pwd = self.hash_password(password)
        new_user = UserModel(username=username, email=email, hashed_password=hashed_pwd)
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        return new_user

    def authenticate_user(self, username: str, password: str):
        user = self.get_user_by_username(username)
        if not user:
            return None
        if self.verify_password(user.hashed_password, password):
            return user
        return None