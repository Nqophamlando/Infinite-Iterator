from flask.cli import with_appcontext
import click
from app.models.user import create_admin

@click.command(name='create-admin')
@with_appcontext
def create_admin_command():
    """Create admin user if it doesn't exist."""
    create_admin()
