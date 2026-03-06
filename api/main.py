from flask.cli import with_appcontext
import click

from api import create_app
from api.core.extensions import db
from api.seed import seed_data

app = create_app()


@click.command("init-db")
@with_appcontext
def init_db_command() -> None:
    db.create_all()
    click.echo("Database initialized.")


@click.command("seed")
@with_appcontext
def seed_command() -> None:
    seed_data()
    click.echo("Seed data inserted.")


app.cli.add_command(init_db_command)
app.cli.add_command(seed_command)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
