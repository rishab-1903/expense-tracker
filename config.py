import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'rishab1903'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///expense_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
