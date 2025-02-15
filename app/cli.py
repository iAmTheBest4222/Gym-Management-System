import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models import User

def register_commands(app):
    @app.cli.command('create-admin')
    @click.argument('username')
    @click.argument('email')
    @click.argument('password')
    @with_appcontext
    def create_admin(username, email, password):
        """Create an admin user."""
        try:
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                first_name='Admin',
                last_name='User'
            )
            admin.set_password(password)
            db.session.add(admin)
            db.session.commit()
            print(f'Admin user {username} created successfully!')
        except Exception as e:
            print(f'Error creating admin user: {e}') 