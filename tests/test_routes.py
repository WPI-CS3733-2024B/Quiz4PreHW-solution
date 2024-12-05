import os
import pytest
from app import create_app, db
from app.models import Course, TeachingAssistant, Room
from config import Config
import sqlalchemy as sqla

class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SECRET_KEY = 'bad-bad-key'
    WTF_CSRF_ENABLED = False
    DEBUG = True
    TESTING = True


@pytest.fixture(scope='module')
def test_client():
    # create the flask application ; configure the app for tests
    flask_app = create_app(config_class=TestConfig)

    # db.init_app(flask_app)
    # Flask provides a way to test your application by exposing the Werkzeug test Client
    # and handling the context locals for you.
    testing_client = flask_app.test_client()
 
    # Establish an application context before running the tests.
    ctx = flask_app.app_context()
    ctx.push()
 
    yield  testing_client 
    # this is where the testing happens!
 
    ctx.pop()

@pytest.fixture
def init_database(request,test_client):
    # Create the database and the database table
    db.create_all()
    # initialize the majors
        # create the rooms 
    allrooms = [{'building' : 'Fuller', 'roomNumber' : 'B46', 'capacity' : 60}, 
                {'building' : 'UnityHall', 'roomNumber' : '175', 'capacity' : 100},
                {'building' : 'UnityHall', 'roomNumber' : '150', 'capacity' : 80},
                {'building' : 'Goddard', 'roomNumber' : '227', 'capacity' : 56}]
    if len(db.session.scalars(sqla.select(Room)).all()) == 0:
        for room in allrooms:
            theroom = Room (building = room['building'],roomNumber=room['roomNumber'], capacity = room['capacity'] ) 
            db.session.add(theroom)
            db.session.commit()
    
    yield  # this is where the testing happens!

    db.drop_all()

def test_index_get(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/index' page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing
    response = test_client.get('/index')

    # TO DO : write assert statements:
    #   verifying the status code and 
    #   verifying the response content. 

    assert response.status_code == 200
    assert b"Current Courses:" in response.data

def test_index_post(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the CourseForm in '/index' is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """

    # Test setup
    # TO DO: get the roomid for Goddard 227; currently hardcoded to 1. 
    room_id = db.session.scalars(sqla.select(Room).where(Room.building == 'Goddard').where(Room.roomNumber == '227')).first().id

    # Create a test client using the Flask application configured for testing
    response = test_client.post('/index', 
                          data=dict(major = 'CS', coursenum='3733',title = 'Soft Eng', classroom = room_id),
                          follow_redirects = True)
    
    # TO DO : write assert statements:
    #   verifying the status code and 
    #   verifying the updates to the database (provide at least 2 assert statements)
    #   verifying the response content.

    assert response.status_code == 200

    courses = db.session.scalars(sqla.select(Course).where(Course.major == 'CS' and Course.coursenum == '3733')).all()

    assert courses[0].major== 'CS'
    assert courses[0].roomid ==  room_id
    assert len(courses) == 1
    assert b"CS 3733" in response.data 
    assert b"Soft Eng" in response.data  
    assert b"TAs:" in response.data   

def test_assigta_get(request,test_client, init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the '/course/<courseid>/assignta'  page is requested (GET)
    THEN check that the response is valid
    """
    # Create a test client using the Flask application configured for testing

    # Test setup
    # TO DO: get the roomid for Goddard 227; currently hardcoded to 1. 
    room_id = db.session.scalars(sqla.select(Room).where(Room.building == 'Goddard').where(Room.roomNumber == '227')).first().id


    # TO DO : Add a new course (CS 3733 Software Engineering) to the DB, assign the "roomid" of the course to room_id. 
    newcourse = Course(major = 'CS', coursenum = '3733', title = 'Software Engineering', roomid = room_id)
    db.session.add(newcourse)
    db.session.commit()

    # TO DO : write assert statements:
    #   verifying the status code and 
    #   verifying the response content. 

    response = test_client.get('/course/'+ str(newcourse.id) + '/assignta')
    assert response.status_code == 200
    assert b"CS 3733 - Software Engineering" in response.data
    assert b"Add New TA:" in response.data


def test_assignta_post(request,test_client,init_database):
    """
    GIVEN a Flask application configured for testing
    WHEN the TAForm in '/course/<courseid>/assignta' is submitted (POST)
    THEN check that the response is valid and the database is updated correctly
    """

    # Test setup
    # TO DO: get the roomid for Goddard 227; currently hardcoded to 1. 
    room_id = db.session.scalars(sqla.select(Room).where(Room.building == 'Goddard').where(Room.roomNumber == '227')).first().id


    # TO DO : Add a new course (CS 3733 Software Engineering) to the DB, assign the "roomid" of the course to room_id. 
    newcourse = Course(major = 'CS', coursenum = '3733', title = 'Software Engineering', roomid = room_id)
    db.session.add(newcourse)
    db.session.commit()

    response = test_client.post('/course/'+ str(newcourse.id) + '/assignta', 
                          data=dict(ta_name = 'Quentin', ta_email='quentin@wpi.edu'),
                          follow_redirects = True)
    
    # TO DO : write assert statements:
    #   verifying the status code and 
    #   verifying the updates to the database ; check if the TeachingAssistant (having name 'Quentin' and email 'quentin@wpi.edu' exists. 
    #   verifying the updates to the database ; check if the TeachingAssistant 'Quentin' is added to the "tas" of course 'CS 3733'  
    #   verifying the response content. 

    assert response.status_code == 200

    # get the CS 3733 course object   
    thecourse = db.session.scalars(sqla.select(Course).where(Course.major == 'CS' and Course.coursenum == '3733')).first()
    all_tas = db.session.scalars(thecourse.tas.select()).all()
    assert len(all_tas) == 1
    assert all_tas[0].ta_name ==  'Quentin'

    # get the TA having email 'quentin@wpi.edu'
    tas = db.session.scalars(sqla.select(TeachingAssistant).where(TeachingAssistant.ta_email == 'quentin@wpi.edu')).all()
    assert len(tas) == 1
    assert tas[0].ta_name== 'Quentin'

    assert b"CS 3733" in response.data 
    assert b"Software Engineering" in response.data  
    assert b"Quentin" in response.data
    assert b"quentin@wpi.edu" in response.data   
   
