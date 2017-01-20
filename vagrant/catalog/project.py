from flask import Flask, render_template, request
from flask import redirect, jsonify, url_for, abort, flash, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from oauth2client.client import flow_from_clientsecrets, FlowExchangeError
import httplib2
import json
import requests
from database_setup import Base, Course, CourseItem
from helpers.user import createUser, getUserId

app = Flask(__name__)

engine = create_engine('sqlite:///courses.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()
client_secrets = json.loads(open('client_secrets.json', 'r').read())
CLIENT_ID = client_secrets['web']['client_id']


def valid_course(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        Checks to see if the course exists and pass it through or return a 404
        """
        course = (
            session.query(Course)
            .filter_by(name=kwargs["course_name"])
            .first()
            )

        if not course:
            abort(404)

        return func(course=course)

    return decorated_function


def valid_course_item(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        Checks to see if the course item exists
        and pass it through or return a 404
        """
        course = (
            session.query(Course)
            .filter_by(name=kwargs["course_name"])
            .first()
            )

        if not course:
            flash("The course you have tried to reach does not exist")
            abort(404)

        course_item = (
            session.query(CourseItem)
            .filter_by(name=kwargs["course_item_name"], course_id=course.id)
            .first()
            )

        if not course_item:
            flash("The course item you have tried to reach does not exist")
            abort(404)

        return func(course=course, course_item=course_item)

    return decorated_function


def valid_permission(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        Checks to make sure the current user id matches the course item user id
        or return 401
        """
        if login_session['user_id'] != kwargs['course_item'].user_id:
            abort(401)

        return func(*args, **kwargs)

    return decorated_function


def valid_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return:
        Checks to make sure that a user id has been set for the login session
        """
        if not (login_session and login_session.get('user_id')):
            flash("User is not logged in")
            abort(401)
        return func(*args, **kwargs)
    return decorated_function


@app.context_processor
def inject_login_session():
    return dict(login_session=login_session)


@app.route('/')
@app.route('/courses/', methods=('GET', 'POST'))
def courses():
    """
    :returns flask.response:
    Renders the courses html template with all courses from the db
    """
    courses = session.query(Course).all()
    return render_template('courses.html', courses=courses)


@app.route('/courses/json')
def coursesJson():
    """
    :returns flask.response:
    Makes json representation of all courses from the db
    """
    courses = session.query(Course).all()
    values = []
    for course in courses:
        course_items = (
            session.query(CourseItem)
            .filter_by(course_id=course.id)
            .all()
            )
        serialized_val = (course_items and [i.serialize for i in course_items])
        serialized_course_items = serialized_val or {}
        course_json = course.serialize
        course_json["items"] = serialized_course_items
        values.append(course_json)

    return jsonify(Courses=values)


def makeJsonResponse(response_string, response_code):
    """
    :param string response_string:
    :param int response_code:
    :return flask.response:
    Returns a json response based on a given string and response code
    """
    response = make_response(json.dumps(response_string), response_code)
    response.headers['Content-Type'] = 'application/json'
    return response


@app.route('/gconnect', methods=['POST'])
def gconnect():

    """
    :return flask.response:
    Oauth2 exchange one time code from client for access token
    """
    code = request.data

    if code is None:
        return makeJsonResponse('Data parameter was not supplied', 400)

    try:
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        return makeJsonResponse('Failed to obtain authorization code', 401)

    access_token = credentials.access_token
    url = (
           "https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={0}"
           .format(access_token))
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    if result.get('error') is not None:
        return makeJsonResponse(result.get('error'), 500)

    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        return makeJsonResponse('User id does not match current user id', 401)

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        return makeJsonResponse('User is already connected', 200)

    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['name'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # check if user exists, if they do retrieve them.  If not, make a new user
    login_session['user_id'] = (getUserId(session, login_session['email']) or
                                createUser(session, login_session))

    return render_template('courses.html')


@app.route('/logout')
@valid_user
def logout():
    """
    :return flask.response:
    Logs out the user
    """
    login_session.clear()
    return redirect(url_for('courses'))


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        return makeJsonResponse('No user is connected', 401)

    url = ('https://accounts.google.com/o/oauth2/revoke?token={0}'
           .format(access_token))
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        return makeJsonResponse('Successfully disconnected', 200)
    else:
        return makeJsonResponse(result, 400)


@app.route('/course/<string:course_name>/', methods=['GET'])
@valid_course
def course(course):
    """
    :param Course course:
    :returns flask.response:
    Renders course item page for a given course
    """
    items = session.query(CourseItem).filter_by(course_id=course.id).all()
    return render_template('courseitems.html',
                           course_name=course.name,
                           course_items=items)


@app.route('/course/<string:course_name>/json', methods=['GET'])
@valid_course
def courseJson(course):
    """
    :param Course course:
    :returns flask.response:
    Return a json representation of all course items for a given course
    """
    items = session.query(CourseItem).filter_by(course_id=course.id).all()
    serialized_course_items = (items and [i.serialize for i in items]) or {}
    return jsonify(CourseItems=serialized_course_items)


@app.route('/course/<string:course_name>/<string:course_item_name>/')
@valid_course_item
def courseItem(course, course_item):
    """
    :param Course course:
    :param CourseItemcourse_item:
    :returns flask.response:
    Renders course item page for a course and course item
    """
    return render_template('courseitem.html',
                           course=course,
                           course_item=course_item)


@app.route('/course/<string:course_name>/<string:course_item_name>/json')
@valid_course_item
def courseItemJson(course, course_item):
    """
    :param Course course:
    :param CourseItem course_item:
    :returns flask.response:
    Returns json representation of course item
    """
    serialized_course_item = (course_item and course_item.serialize) or {}
    return jsonify(CourseItem=serialized_course_item)


@app.route('/course/<string:course_name>/new/', methods=['GET', 'POST'])
@valid_course
@valid_user
def newCourseItem(course):
    """
    :param Course course:
    :returns flask.response:
    Creates new course item or renders new course item template
    """
    if request.method == "POST":
        form = request.form
        new_course_item = CourseItem(name=form['name'],
                                     description=form['description'],
                                     steps=form['steps'],
                                     course_id=course.id,
                                     user_id=login_session['user_id'])
        session.add(new_course_item)
        session.commit()
        return redirect(url_for('courseItem',
                                course_name=course.name,
                                course_item_name=new_course_item.name))

    return render_template('newcourseitem.html', course_name=course.name)


@app.route('/course/<string:course_name>/<string:course_item_name>/delete/',
           methods=['GET', 'POST'])
@valid_course_item
@valid_user
@valid_permission
def deleteCourseItem(course, course_item):
    """
    :param Course course:
    :param CourseItem course_item:
    :returns flask.response:
    Deletes course item and redirect or returns deletecourse item template
    """
    if request.method == "POST":
        session.delete(course_item)
        session.commit()
        return redirect(url_for('course', course_name=course.name))

    return render_template('deletecourseitem.html',
                           course_name=course.name,
                           course_item_name=course_item.name)


@app.route('/course/<string:course_name>/<string:course_item_name>/edit/',
           methods=['GET', 'POST'])
@valid_course_item
@valid_user
@valid_permission
def editCourseItem(course, course_item):
    """
    :param Course course:
    :param CourseItem course_item:
    :returns flask.response:
    Updates existing course item and redirects or renders edit template
    """
    if request.method == "POST":
        form = request.form
        if not (form['name'] and form['description'] and form['steps']):
            flash("Please ensure that all fields have values.")
            return render_template('editcourseitem.html',
                                   course_name=course.name,
                                   course_item=course_item)

        course_item.name = request.form['name']
        course_item.description = request.form['description']
        course_item.steps = request.form['steps']
        course_item.course_id = course.id
        session.add(course_item)
        session.commit()
        return redirect(url_for('courseItem',
                                course_name=course.name,
                                course_item_name=course_item.name))

    return render_template('editcourseitem.html',
                           course_name=course.name,
                           course_item=course_item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
