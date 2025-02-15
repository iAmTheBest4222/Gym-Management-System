from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.admin import bp
from app.models import User, Gym, Membership, MembershipPlan, GymClass, Booking
from app.extensions import db
from app.admin.forms import GymForm, MembershipPlanForm, GymClassForm
from app.admin.decorators import admin_required
from datetime import datetime, timedelta

@bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    # Get statistics for dashboard
    total_users = User.query.count()
    total_gyms = Gym.query.count()
    active_memberships = Membership.query.filter_by(status='active').count()
    today_bookings = Booking.query.filter(
        Booking.booking_date >= datetime.today(),
        Booking.booking_date < datetime.today() + timedelta(days=1)
    ).count()

    # Get recent activities
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    new_users = User.query.order_by(User.created_at.desc()).limit(5).all()

    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_gyms=total_gyms,
                         active_memberships=active_memberships,
                         today_bookings=today_bookings,
                         recent_bookings=recent_bookings,
                         new_users=new_users)

# Gym Management
@bp.route('/gyms')
@login_required
@admin_required
def gyms():
    page = request.args.get('page', 1, type=int)
    gyms = Gym.query.paginate(page=page, per_page=10)
    return render_template('admin/gyms.html', gyms=gyms)

@bp.route('/gym/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_gym():
    form = GymForm()
    if form.validate_on_submit():
        gym = Gym(
            name=form.name.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            country=form.country.data,
            latitude=form.latitude.data,
            longitude=form.longitude.data,
            phone=form.phone.data,
            email=form.email.data,
            amenities=form.amenities.data.split('\n') if form.amenities.data else [],
            opening_hours=form.opening_hours.data
        )
        db.session.add(gym)
        db.session.commit()
        flash('Gym has been added successfully.', 'success')
        return redirect(url_for('admin.gyms'))
    return render_template('admin/gym_form.html', form=form, title='Add Gym')

@bp.route('/gym/<int:gym_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_gym(gym_id):
    gym = Gym.query.get_or_404(gym_id)
    form = GymForm(obj=gym)
    if form.validate_on_submit():
        gym.name = form.name.data
        gym.description = form.description.data
        gym.address = form.address.data
        gym.city = form.city.data
        gym.country = form.country.data
        gym.latitude = form.latitude.data
        gym.longitude = form.longitude.data
        gym.phone = form.phone.data
        gym.email = form.email.data
        gym.amenities = form.amenities.data.split('\n') if form.amenities.data else []
        gym.opening_hours = form.opening_hours.data
        db.session.commit()
        flash('Gym has been updated successfully.', 'success')
        return redirect(url_for('admin.gyms'))
    return render_template('admin/gym_form.html', form=form, title='Edit Gym')

@bp.route('/gym/<int:gym_id>/details')
@login_required
@admin_required
def gym_details(gym_id):
    gym = Gym.query.get_or_404(gym_id)
    classes = GymClass.query.filter_by(gym_id=gym_id).order_by(GymClass.start_time).all()
    active_memberships = Membership.query.filter_by(gym_id=gym_id, status='active').count()
    
    # Get statistics
    stats = {
        'total_members': len(gym.memberships),
        'active_members': active_memberships,
        'total_classes': len(gym.classes),
        'total_bookings': sum(len(gym_class.bookings) for gym_class in gym.classes)
    }
    
    return render_template('admin/gym_details.html', gym=gym, classes=classes, stats=stats)

@bp.route('/gym/<int:gym_id>/add-class', methods=['GET', 'POST'])
@login_required
@admin_required
def add_gym_class(gym_id):
    gym = Gym.query.get_or_404(gym_id)
    form = GymClassForm()
    
    if form.validate_on_submit():
        gym_class = GymClass(
            gym_id=gym.id,
            name=form.name.data,
            description=form.description.data,
            instructor=form.instructor.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            capacity=form.capacity.data
        )
        db.session.add(gym_class)
        db.session.commit()
        flash('Class has been added successfully.', 'success')
        return redirect(url_for('admin.gym_details', gym_id=gym.id))
    
    return render_template('admin/gym_class_form.html', form=form, gym=gym, title='Add Class')

@bp.route('/gym/<int:gym_id>/edit-class/<int:class_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_gym_class(gym_id, class_id):
    gym_class = GymClass.query.get_or_404(class_id)
    if gym_class.gym_id != gym_id:
        abort(404)
    
    form = GymClassForm(obj=gym_class)
    if form.validate_on_submit():
        gym_class.name = form.name.data
        gym_class.description = form.description.data
        gym_class.instructor = form.instructor.data
        gym_class.start_time = form.start_time.data
        gym_class.end_time = form.end_time.data
        gym_class.capacity = form.capacity.data
        db.session.commit()
        flash('Class has been updated successfully.', 'success')
        return redirect(url_for('admin.gym_details', gym_id=gym_id))
    
    return render_template('admin/gym_class_form.html', form=form, gym=gym_class.gym, title='Edit Class')

@bp.route('/gym/<int:gym_id>/delete-class/<int:class_id>')
@login_required
@admin_required
def delete_gym_class(gym_id, class_id):
    gym_class = GymClass.query.get_or_404(class_id)
    if gym_class.gym_id != gym_id:
        abort(404)
    
    db.session.delete(gym_class)
    db.session.commit()
    flash('Class has been deleted successfully.', 'success')
    return redirect(url_for('admin.gym_details', gym_id=gym_id))

# Membership Plan Management
@bp.route('/membership-plans')
@login_required
@admin_required
def membership_plans():
    plans = MembershipPlan.query.all()
    return render_template('admin/membership_plans.html', plans=plans)

@bp.route('/membership-plan/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_membership_plan():
    form = MembershipPlanForm()
    if form.validate_on_submit():
        plan = MembershipPlan(
            name=form.name.data,
            description=form.description.data,
            duration_months=form.duration_months.data,
            price=form.price.data,
            features=form.features.data,
            is_active=form.is_active.data
        )
        db.session.add(plan)
        db.session.commit()
        flash('Membership plan has been added successfully.', 'success')
        return redirect(url_for('admin.membership_plans'))
    return render_template('admin/membership_plan_form.html', form=form, title='Add Membership Plan')

# User Management
@bp.route('/users')
@login_required
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    users = User.query.paginate(page=page, per_page=20)
    return render_template('admin/users.html', users=users)

@bp.route('/user/<int:user_id>/toggle-admin')
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    if user == current_user:
        flash('You cannot change your own admin status.', 'error')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        flash(f'Admin status for {user.username} has been updated.', 'success')
    return redirect(url_for('admin.users'))

# Booking Management
@bp.route('/bookings')
@login_required
@admin_required
def bookings():
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Booking.query
    if status:
        query = query.filter_by(status=status)
    
    bookings = query.order_by(Booking.booking_date.desc()).paginate(
        page=page, per_page=20)
    return render_template('admin/bookings.html', bookings=bookings, current_status=status)

@bp.route('/gym/<int:gym_id>/memberships')
@login_required
@admin_required
def gym_memberships(gym_id):
    gym = Gym.query.get_or_404(gym_id)
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    
    query = Membership.query.filter_by(gym_id=gym_id)
    if status:
        query = query.filter_by(status=status)
    
    memberships = query.order_by(Membership.start_date.desc()).paginate(
        page=page, per_page=20)
    
    return render_template('admin/gym_memberships.html', 
                         gym=gym, 
                         memberships=memberships,
                         current_status=status)

@bp.route('/gym/<int:gym_id>/membership/<int:membership_id>/update-status', methods=['POST'])
@login_required
@admin_required
def update_membership_status(gym_id, membership_id):
    membership = Membership.query.get_or_404(membership_id)
    if membership.gym_id != gym_id:
        abort(404)
    
    new_status = request.form.get('status')
    if new_status in ['active', 'expired', 'cancelled']:
        membership.status = new_status
        db.session.commit()
        flash(f'Membership status has been updated to {new_status}.', 'success')
    
    return redirect(url_for('admin.gym_memberships', gym_id=gym_id))

@bp.route('/gym/<int:gym_id>/membership/<int:membership_id>/extend', methods=['POST'])
@login_required
@admin_required
def extend_membership(gym_id, membership_id):
    membership = Membership.query.get_or_404(membership_id)
    if membership.gym_id != gym_id:
        abort(404)
    
    months = int(request.form.get('months', 1))
    if months > 0:
        membership.end_date = membership.end_date + timedelta(days=30 * months)
        membership.status = 'active'
        db.session.commit()
        flash(f'Membership has been extended by {months} months.', 'success')
    
    return redirect(url_for('admin.gym_memberships', gym_id=gym_id)) 