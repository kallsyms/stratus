import os

class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY', os.urandom(32))
    POSTGRES_USER = os.environ.get('POSTGRES_USER', 'postgres')
    POSTGRES_PASS = os.environ.get('POSTGRES_PASS', 'postgres')
    POSTGRES_HOST = os.environ.get('POSTGRES_HOST', 'localhost')
    POSTGRES_PORT = int(os.environ.get('POSTGRES_PORT', 5464))
    POSTGRES_DB = os.environ.get('POSTGRES_DB', 'postgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    INGEST_MONGO_SERVER_URI = os.environ.get('INGEST_MONGO_SERVER_URI', 'mongodb://localhost:27017/')
    INGEST_MONGO_DATABASE = os.environ.get('INGEST_MONGO_DATABASE', 'wx')
    INGEST_MONGO_COLLECTION = os.environ.get('INGEST_MONGO_COLLECTION', 'wx')

Config.SQLALCHEMY_DATABASE_URI = f"postgresql://{Config.POSTGRES_USER}:{Config.POSTGRES_PASS}@{Config.POSTGRES_HOST}:{Config.POSTGRES_PORT}/{Config.POSTGRES_DB}"