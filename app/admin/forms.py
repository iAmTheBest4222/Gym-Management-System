from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange

class GymForm(FlaskForm):
    name = StringField('Gym Name', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired(), Length(max=256)])
    city = StringField('City', validators=[DataRequired(), Length(max=64)])
    country = StringField('Country', validators=[DataRequired(), Length(max=64)])
    latitude = FloatField('Latitude', validators=[Optional()])
    longitude = FloatField('Longitude', validators=[Optional()])
    phone = StringField('Phone', validators=[DataRequired(), Length(max=20)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    amenities = TextAreaField('Amenities (one per line)', validators=[Optional()])
    opening_hours = TextAreaField('Opening Hours', validators=[Optional()])
    submit = SubmitField('Submit')

    def process_amenities(self, amenities):
        if isinstance(amenities, list):
            self.amenities.data = '\n'.join(amenities)
        else:
            self.amenities.data = amenities

class MembershipPlanForm(FlaskForm):
    name = StringField('Plan Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    duration_months = IntegerField('Duration (months)', validators=[
        DataRequired(), NumberRange(min=1, max=60)
    ])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    features = TextAreaField('Features (one per line)', validators=[Optional()])
    is_active = BooleanField('Is Active')
    submit = SubmitField('Submit')

    def process_features(self, features):
        if isinstance(features, list):
            self.features.data = '\n'.join(features)
        else:
            self.features.data = features

class GymClassForm(FlaskForm):
    name = StringField('Class Name', validators=[DataRequired(), Length(max=64)])
    description = TextAreaField('Description', validators=[DataRequired()])
    instructor = StringField('Instructor Name', validators=[DataRequired(), Length(max=64)])
    start_time = DateTimeField('Start Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    end_time = DateTimeField('End Time', format='%Y-%m-%d %H:%M', validators=[DataRequired()])
    capacity = IntegerField('Capacity', validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField('Submit')

    def validate_end_time(self, field):
        if field.data <= self.start_time.data:
            raise ValidationError('End time must be after start time') 