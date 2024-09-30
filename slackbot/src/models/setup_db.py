from models.db import db
from models.job import Job
from models.hash import Hash
from models.job_hash import JobHash
from peewee_migrate import Router
import os
import warnings


migrate_dir = os.path.join(os.path.dirname(__file__), "../migrations")
router = Router(db, migrate_dir=migrate_dir)


def db_migrate_up():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        router.run()


def db_migrate_down():
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)

        # done attribute indicates migrations that have been completed
        while router.done:
            # remove done migration
            router.rollback()


def setup_db():
    db.connect(reuse_if_open=True)
    db_migrate_up()
    db.create_tables([Job, Hash, JobHash])


def reset_db():
    db_migrate_down()
    db_migrate_up()
