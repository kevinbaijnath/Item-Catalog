from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Course

engine = create_engine('postgresql://catalog@localhost/itemcatalog')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Appetizers Category
course_category1 = Course(name="Appetizers")
session.add(course_category1)
session.commit()

# Beverages Category
course_category2 = Course(name="Beverages")
session.add(course_category2)
session.commit()

# Deserts Category
course_category3 = Course(name="Deserts")
session.add(course_category3)
session.commit()

# Main Dishes Category
course_category4 = Course(name="Main Dishes")
session.add(course_category4)
session.commit()

# Salads Category
course_category5 = Course(name="Salads")
session.add(course_category5)
session.commit()

# Side Dishes Category
course_category6 = Course(name="Side Dishes")
session.add(course_category6)
session.commit()

# Snacks Category
course_category7 = Course(name="Snacks")
session.add(course_category7)
session.commit()

# Soups Category
course_category8 = Course(name="Soups")
session.add(course_category8)
session.commit()

print "Added Course Categories"
