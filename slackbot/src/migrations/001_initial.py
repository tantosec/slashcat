"""Peewee migrations -- 001_initial.py.

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
CREATE TABLE IF NOT EXISTS "job" ("id" INTEGER NOT NULL PRIMARY KEY, "owner_id" TEXT NOT NULL, "command_args_j" TEXT NOT NULL, "priority" INTEGER NOT NULL, "state" TEXT NOT NULL CHECK (state IN ('Q', 'R', 'P')), "last_seen_progress" INTEGER NOT NULL, "last_restore_point" INTEGER NOT NULL, "last_mask_len" INTEGER NOT NULL, "last_maskfile_ind" INTEGER NOT NULL, "max_progress" INTEGER NOT NULL, "max_maskfile_ind" INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS "hash" ("hash" TEXT NOT NULL PRIMARY KEY, "result" TEXT);
CREATE TABLE IF NOT EXISTS "jobhash" ("id" INTEGER NOT NULL PRIMARY KEY, "job_id" INTEGER NOT NULL, "hash_id" TEXT NOT NULL, FOREIGN KEY ("job_id") REFERENCES "job" ("id") ON DELETE CASCADE, FOREIGN KEY ("hash_id") REFERENCES "hash" ("hash"));
CREATE INDEX "jobhash_job_id" ON "jobhash" ("job_id");
CREATE INDEX "jobhash_hash_id" ON "jobhash" ("hash_id");
CREATE TABLE IF NOT EXISTS "wordlist" ("wordlist" TEXT NOT NULL PRIMARY KEY);
CREATE TABLE IF NOT EXISTS "rule" ("rule" TEXT NOT NULL PRIMARY KEY);
CREATE TABLE IF NOT EXISTS "maskfile" ("maskfile" TEXT NOT NULL PRIMARY KEY);
""".strip().splitlines()

ROLLBACK_SQL = """
DROP TABLE "maskfile";
DROP TABLE "rule";
DROP TABLE "wordlist";
DROP INDEX "jobhash_job_id";
DROP INDEX "jobhash_hash_id";
DROP TABLE "jobhash";
DROP TABLE "hash";
DROP TABLE "job";
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
