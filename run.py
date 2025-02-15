from app import create_app, db
from app.models import User, Gym, Membership, MembershipPlan, GymClass, Booking, Review, Payment

app = create_app()
if app.config['ENV'] == 'production':
    app.config.from_object('config.ProductionConfig')

def init_db():
    with app.app_context():
        db.create_all()

if __name__ == '__main__':
    init_db()
    app.run() 