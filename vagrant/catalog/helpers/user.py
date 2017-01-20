from database_setup import User


def createUser(session, login_session):
    """
    :param sqlalchemy.orm.sessionmaker session:
    :param dictionary login_session:
    :returns int:
    Creates a user in the db and returns the id of the newly created user
    """
    user = User(name=login_session["name"],
                email=login_session["email"],
                picture=login_session["picture"])
    session.add(user)
    session.commit()
    user = session.query(User).filter_by(email=login_session["email"]).first()
    return user.id


def getUserId(session, email):
    """
    :param sqlalchemy.orm.sessionmaker session:
    :param string email:
    :returns int:
    Obtains a user id from the db given an email
    """
    user = session.query(User).filter_by(email=email).first()
    return user and user.id or None
