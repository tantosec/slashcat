from peewee import SqliteDatabase

from env_vars import SQLITE_PATH

db = SqliteDatabase(SQLITE_PATH, pragmas={"foreign_keys": 1})
