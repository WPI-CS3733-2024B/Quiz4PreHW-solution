from __future__ import print_function
import sys
from flask import Blueprint,render_template, flash, redirect, url_for, request

from app import db
from app.forms import CourseForm, TAForm
from app.models import Course, Room, TeachingAssistant
import sqlalchemy as sqla

app_blueprint = Blueprint('app', __name__)


@app_blueprint.route('/', methods=['GET', 'POST'])
@app_blueprint.route('/index', methods=['GET', 'POST'])
def index():  
    form = CourseForm()
    if form.validate_on_submit():
        if (form.major.data is not None) and (form.coursenum.data is not None):
            #check if course already exists
            course_count = db.session.scalar(sqla.select(db.func.count()).where(Course.major == form.major.data).where(Course.coursenum == form.coursenum.data))
            if course_count < 1:
                newcourse = Course(major = form.major.data,coursenum = form.coursenum.data,title = form.title.data, roomid = form.classroom.data.id)
                db.session.add(newcourse)
                db.session.commit()
                return redirect(url_for('app.course', course_id = newcourse.id) )
    # display existing courses
    all_courses = db.session.scalars(sqla.select(Course).order_by(Course.major)).all()
    return render_template('index.html', form=form, courses = all_courses)

@app_blueprint.route('/course/<course_id>/assignta', methods = ['GET', 'POST'])
def course(course_id):
    form = TAForm()
    thecourse = db.session.get(Course, course_id)
    if form.validate_on_submit():
        if (form.ta_name.data is not None) :
                new_ta = TeachingAssistant(ta_name = form.ta_name.data, ta_email = form.ta_email.data)
                db.session.add(new_ta)
                thecourse.add_ta(new_ta)
                db.session.commit()
                return redirect(url_for('app.course', course_id = thecourse.id) )
        
    return render_template('course.html', form = form, current_course = thecourse)
