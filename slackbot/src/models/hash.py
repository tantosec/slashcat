from peewee import *

from models.base_model import BaseModel


class Hash(BaseModel):
    hash = TextField(primary_key=True)
    result = TextField(null=True)
