from peewee import *

from models.base_model import BaseModel
from models.hash import Hash
from models.job import Job


class JobHash(BaseModel):
    job = ForeignKeyField(Job, backref="hashes", on_delete="CASCADE")
    hash = ForeignKeyField(Hash)
