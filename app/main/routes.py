from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.main import bp
from app.models import Gym, Membership, Booking, GymClass, MembershipPlan
from app import db
from datetime import datetime, timedelta

@bp.route('/')
def index():
    return render_template('main/index.html')

@bp.route('/dashboard')
@login_required
def dashboard():
    user_memberships = Membership.query.filter_by(user_id=current_user.id).all()
    upcoming_bookings = Booking.query.filter_by(
        user_id=current_user.id,
        status='confirmed'
    ).order_by(Booking.booking_date).limit(5).all()
    
    return render_template('main/dashboard.html',
                         memberships=user_memberships,
                         upcoming_bookings=upcoming_bookings)

@bp.route('/gyms')
def gyms():
    page = request.args.get('page', 1, type=int)
    gyms = Gym.query.paginate(page=page, per_page=9)
    return render_template('main/gyms.html', gyms=gyms)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    return render_template('main/edit_profile.html')

@bp.route('/membership_plans')
@login_required
def membership_plans():
    plans = MembershipPlan.query.filter_by(is_active=True).all()
    return render_template('main/membership_plans.html', plans=plans)

@bp.route('/renew_membership/<int:membership_id>', methods=['GET', 'POST'])
@login_required
def renew_membership(membership_id):
    membership = Membership.query.get_or_404(membership_id)
    if membership.user_id != current_user.id:
        abort(403)
    
    if request.method == 'POST':
        # Add payment processing logic here
        membership.end_date = membership.end_date + timedelta(days=30 * membership.plan.duration_months)
        membership.status = 'active'
        db.session.commit()
        flash('Your membership has been renewed successfully.', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/renew_membership.html', membership=membership)

@bp.route('/book_class')
@login_required
def book_class():
    page = request.args.get('page', 1, type=int)
    classes = GymClass.query.paginate(page=page, per_page=10)
    return render_template('main/book_class.html', classes=classes)

@bp.route('/cancel_booking/<int:booking_id>')
@login_required
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    if booking.user_id != current_user.id:
        abort(403)
    
    booking.status = 'cancelled'
    booking.gym_class.current_bookings -= 1
    db.session.commit()
    flash('Your booking has been cancelled.', 'success')
    return redirect(url_for('main.dashboard')) 