from __future__ import with_statement

from os import path
from logging.config import fileConfig

from alembic import context
from flask import current_app

config = context.config

# Flask-Migrate may resolve a config path that does not exist in some container
# layouts (for example "migrations/alembic.ini"). In that case we continue
# without file-based logging config.
if config.config_file_name and path.exists(config.config_file_name):
    fileConfig(config.config_file_name)

target_db = current_app.extensions["migrate"].db
target_metadata = target_db.metadata


def get_engine():
    return current_app.extensions["migrate"].db.engine


def get_engine_url():
    return get_engine().url.render_as_string(hide_password=False).replace("%", "%%")


config.set_main_option("sqlalchemy.url", get_engine_url())


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = get_engine()

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
