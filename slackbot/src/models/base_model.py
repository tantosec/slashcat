from peewee import Model
from models.db import db


class BaseModel(Model):
    class Meta:
        database = db
