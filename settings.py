from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="DYNACONF",
    settings_files=["settings.toml", "secrets.toml"],
)

class Config:
    SECRET_KEY = settings.SECRET_KEY
    SQLALCHEMY_DATABASE_URI = settings.DATABASE_URI
    SQLALCHEMY_TRACK_MODIFICATIONS = settings.MODIFICATIONS

class DevelopmentConfig(Config):
    DEBUG = True
