from flask import Flask, render_template, request, redirect, jsonify, url_for, abort
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Course, CourseItem

app = Flask(__name__)

engine = create_engine('sqlite:///courses.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Fake Restaurants
# restaurant = {'name': 'The CRUDdy Crab', 'id': '1'}

# restaurants = [{'name': 'The CRUDdy Crab', 'id': '1'}, {'name':'Blue Burgers', 'id':'2'},{'name':'Taco Hut', 'id':'3'}]

# Fake Menu Items
# items = [ {'name':'Cheese Pizza', 'description':'made with fresh cheese', 'price':'$5.99','course' :'Entree', 'id':'1'}, {'name':'Chocolate Cake','description':'made with Dutch Chocolate', 'price':'$3.99', 'course':'Dessert','id':'2'},{'name':'Caesar Salad', 'description':'with fresh organic vegetables','price':'$5.99', 'course':'Entree','id':'3'},{'name':'Iced Tea', 'description':'with lemon','price':'$.99', 'course':'Beverage','id':'4'},{'name':'Spinach Dip', 'description':'creamy dip with fresh spinach','price':'$1.99', 'course':'Appetizer','id':'5'} ]
# item =  {'name':'Cheese Pizza','description':'made with fresh cheese','price':'$5.99','course' :'Entree'}
# items = []

#get all courses
#get a json representation of all courses
@app.route('/')
@app.route('/course/', methods=('GET', 'POST'))
def courses():
    courses = session.query(Course).all()

    if request.headers['Content-Type'] == 'application/json':
        return jsonify(Courses=[c.serialize for c in courses])

    return render_template('courses.html',courses=courses)

#get a specific course
#get a json representation of a course
#post a new course
@app.route('/course/<string:course_name>/', methods=['GET'])
def course(course_name):
    #if request.method == 'POST':
    #    newCourse = Course(name=request.form['name'])
    #    session.add(newCourse)
    #    session.commit()
    #    return redirect(url_for('courses'))

    course = session.query(Course).filter_by(name=course_name).first()
    course_items = session.query(CourseItem).filter_by(course_id=course.id).all()
    if request.headers['Content-Type'] == 'application/json':
        serialized_course = (course and course.serialize) or {}
        serialized_course_items = (course_items and [i.serialize for i in course_items]) or {}
        return jsonify(Course=serialized_course,CourseItems=serialized_course_items)

    return render_template('courseitems.html',course_name=course.name, course_items=course_items)

#get a specific course item
#get a json representation of a specific course item
#post a new specific course item
@app.route('/course/<string:course>/<string:course_item>/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def courseItem(course, course_item):
    course = session.query(Course).filter_by(name=course).first()

    if not course:
        abort(404)

    course_item = session.query(CourseItem).filter_by(course_id=course.id, name=course_item).first()
    exists = course_item != None
    form = request.form

    if request.method == "POST":
        if exists:
            return render_template('error.html',error_string="Resource already exists"), 409
        newCourseItem = CourseItem(name=form['name'],description=form['description'],steps=form['steps'],course_id=course.id)
        session.add(newCourseItem)
        session.commit()
        return redirect(url_for('categoryItem', course=course.name))
    elif request.method == "PUT":
        if not exists:
            abort(404)
        course_item.name = form['name']
        course_item.description=form['description']
        course_item.steps=form['steps']
        course_item.course_id=course.id
        session.add(course_item)
        session.commit()

    elif request.method == "DELETE":
        if not exists:
            abort(404)
        session.delete(course_item)
        session.commit()
        return redirect(url_for('showMenu', restaurant_id=restaurant_id))


    if request.headers['Content-Type'] == 'application/json':
        serialized_value = (course_item and course_item.serialize) or {}
        return jsonify(CourseItem=serialized_value)

@app.route('/course/<string:course>/new/', methods=['GET', 'POST'])
def newCourseItem(course):
    course_value = session.query(Course).filter_by(name=course).first()

    if not course:
        return redirect(url_for('categories'))

    if request.method == "POST":
        form = request.form
        new_course_item = CourseItem(name=form['name'], description=form['description'], steps=form['steps'],
                                   course_id=course_value.id)
        session.add(new_course_item)
        session.commit()
        return redirect(url_for('courseItem', course=course_value.name, course_item=new_course_item.name))

    return render_template('newcourseitem.html',course_id=course_value.id, course_name=course_value.name)

@app.route('/course/<int:course_id>/delete/', methods=['GET', 'POST'])
def deleteCourse(course_id):
    course = session.query(Course).filter_by(id=course_id).first()

    if not course:
        return redirect(url_for('categories'))

    print(course)
#
#
# @app.route('/restaurant/<int:restaurant_id>/menu/JSON')
# def restaurantMenuJSON(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return jsonify(MenuItems=[i.serialize for i in items])
#
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
# def menuItemJSON(restaurant_id, menu_id):
#     Menu_Item = session.query(MenuItem).filter_by(id=menu_id).one()
#     return jsonify(Menu_Item=Menu_Item.serialize)
#
#
# @app.route('/restaurant/JSON')
# def restaurantsJSON():
#     restaurants = session.query(Restaurant).all()
#     return jsonify(restaurants=[r.serialize for r in restaurants])
#
#
# # Show all restaurants
# @app.route('/')
# @app.route('/restaurant/')
# def showRestaurants():
#     restaurants = session.query(Restaurant).all()
#     # return "This page will show all my restaurants"
#     return render_template('restaurants.html', restaurants=restaurants)
#
#
# # Create a new restaurant
# @app.route('/restaurant/new/', methods=['GET', 'POST'])
# def newRestaurant():
#     if request.method == 'POST':
#         newRestaurant = Restaurant(name=request.form['name'])
#         session.add(newRestaurant)
#         session.commit()
#         return redirect(url_for('showRestaurants'))
#     else:
#         return render_template('newRestaurant.html')
#     # return "This page will be for making a new restaurant"
#
# # Edit a restaurant
#
#
# @app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
# def editRestaurant(restaurant_id):
#     editedRestaurant = session.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedRestaurant.name = request.form['name']
#             return redirect(url_for('showRestaurants'))
#     else:
#         return render_template(
#             'editRestaurant.html', restaurant=editedRestaurant)
#
#     # return 'This page will be for editing restaurant %s' % restaurant_id
#
# # Delete a restaurant
#
#
# @app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
# def deleteRestaurant(restaurant_id):
#     restaurantToDelete = session.query(
#         Restaurant).filter_by(id=restaurant_id).one()
#     if request.method == 'POST':
#         session.delete(restaurantToDelete)
#         session.commit()
#         return redirect(
#             url_for('showRestaurants', restaurant_id=restaurant_id))
#     else:
#         return render_template(
#             'deleteRestaurant.html', restaurant=restaurantToDelete)
#     # return 'This page will be for deleting restaurant %s' % restaurant_id
#
#
# # Show a restaurant menu
# @app.route('/restaurant/<int:restaurant_id>/')
# @app.route('/restaurant/<int:restaurant_id>/menu/')
# def showMenu(restaurant_id):
#     restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
#     items = session.query(MenuItem).filter_by(
#         restaurant_id=restaurant_id).all()
#     return render_template('menu.html', items=items, restaurant=restaurant)
#     # return 'This page is the menu for restaurant %s' % restaurant_id
#
# # Create a new menu item
#
#
# @app.route(
#     '/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
# def newMenuItem(restaurant_id):
#     if request.method == 'POST':
#         newItem = MenuItem(name=request.form['name'], description=request.form[
#                            'description'], price=request.form['price'], course=request.form['course'], restaurant_id=restaurant_id)
#         session.add(newItem)
#         session.commit()
#
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('newmenuitem.html', restaurant_id=restaurant_id)
#
#     return render_template('newMenuItem.html', restaurant=restaurant)
#     # return 'This page is for making a new menu item for restaurant %s'
#     # %restaurant_id
#
# # Edit a menu item
#
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit',
#            methods=['GET', 'POST'])
# def editMenuItem(restaurant_id, menu_id):
#     editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
#     if request.method == 'POST':
#         if request.form['name']:
#             editedItem.name = request.form['name']
#         if request.form['description']:
#             editedItem.description = request.form['name']
#         if request.form['price']:
#             editedItem.price = request.form['price']
#         if request.form['course']:
#             editedItem.course = request.form['course']
#         session.add(editedItem)
#         session.commit()
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#
#         return render_template(
#             'editmenuitem.html', restaurant_id=restaurant_id, menu_id=menu_id, item=editedItem)
#
#     # return 'This page is for editing menu item %s' % menu_id
#
# # Delete a menu item
#
#
# @app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete',
#            methods=['GET', 'POST'])
# def deleteMenuItem(restaurant_id, menu_id):
#     itemToDelete = session.query(MenuItem).filter_by(id=menu_id).one()
#     if request.method == 'POST':
#         session.delete(itemToDelete)
#         session.commit()
#         return redirect(url_for('showMenu', restaurant_id=restaurant_id))
#     else:
#         return render_template('deleteMenuItem.html', item=itemToDelete)
#     # return "This page is for deleting menu item %s" % menu_id


if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5050)
