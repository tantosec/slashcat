"""Peewee migrations -- 002_remove_list_cache.py.

Some examples (model - class or model name)::

    > Model = migrator.orm['table_name']            # Return model in current state by name
    > Model = migrator.ModelClass                   # Return model in current state by name

    > migrator.sql(sql)                             # Run custom SQL
    > migrator.run(func, *args, **kwargs)           # Run python function with the given args
    > migrator.create_model(Model)                  # Create a model (could be used as decorator)
    > migrator.remove_model(model, cascade=True)    # Remove a model
    > migrator.add_fields(model, **fields)          # Add fields to a model
    > migrator.change_fields(model, **fields)       # Change fields
    > migrator.remove_fields(model, *field_names, cascade=True)
    > migrator.rename_field(model, old_field_name, new_field_name)
    > migrator.rename_table(model, new_table_name)
    > migrator.add_index(model, *col_names, unique=False)
    > migrator.add_not_null(model, *field_names)
    > migrator.add_default(model, field_name, default)
    > migrator.add_constraint(model, name, sql)
    > migrator.drop_index(model, *col_names)
    > migrator.drop_not_null(model, *field_names)
    > migrator.drop_constraints(model, *constraints)

"""

from contextlib import suppress

import peewee as pw
from peewee_migrate import Migrator


with suppress(ImportError):
    import playhouse.postgres_ext as pw_pext


MIGRATE_SQL = """
DROP TABLE "maskfile";
DROP TABLE "rule";
DROP TABLE "wordlist";
""".strip().splitlines()

ROLLBACK_SQL = """
CREATE TABLE IF NOT EXISTS "wordlist" ("wordlist" TEXT NOT NULL PRIMARY KEY);
CREATE TABLE IF NOT EXISTS "rule" ("rule" TEXT NOT NULL PRIMARY KEY);
CREATE TABLE IF NOT EXISTS "maskfile" ("maskfile" TEXT NOT NULL PRIMARY KEY);
""".strip().splitlines()


# Using raw sql here as otherwise would have to keep a backup of the model state for each specific version
def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    with database.atomic():
        for l in MIGRATE_SQL:
            migrator.sql(l)


def rollback(migrator: Migrator, database: pw.Database, *, fake=False):
    with database.atomic():
        for l in ROLLBACK_SQL:
            migrator.sql(l)
