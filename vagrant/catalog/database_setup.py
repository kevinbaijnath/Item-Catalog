from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Course(Base):
    __tablename__ = 'course'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
        }

class CourseItem(Base):
    __tablename__ = 'course_item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    steps = Column(String(1000), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship(Course)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'steps': self.steps,
        }

#### END OF FILE ###
engine = create_engine('sqlite:///courses.db')
Base.metadata.create_all(engine)
