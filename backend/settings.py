# Flask settings
# FLASK_SERVER_NAME = 'localhost:8888'
FLASK_DEBUG = True  # Do not use debug mode in production

# SQLAlchemy settings
#SQLALCHEMY_DATABASE_URI = 'postgresql://xtdkkbutqwhxvv:d3938c8668b8307b5e6be45177a60e482ddb79e6c23deaa34231a63570940e80@ec2-34-247-118-233.eu-west-1.compute.amazonaws.com:5432/d19t4vr4el5ht4'
SQLALCHEMY_DATABASE_URI = 'sqlite:///./app.db'
SQLALCHEMY_TRACK_MODIFICATIONS = True


info = {'iss': 'accounts.google.com', 'azp': '709342652468-q70g39ndsui4iuclht5eeatfhl9nqngn.apps.googleusercontent.com', 'aud': '709342652468-q70g39ndsui4iuclht5eeatfhl9nqngn.apps.googleusercontent.com', 'sub': '111043145295966398014', 'email': 'it.kevin.shitaye@gmail.com', 'email_verified': True, 'at_hash': 'fiZThb0ThOcwIVVm4kK5Eg', 'name': 'Kevin Shitaye', 'picture': 'https://lh3.googleusercontent.com/a/AATXAJzBSj_3i_zQ8hdpYJefk8vu6PhxYkQvTCynpcbZ=s96-c', 'given_name': 'Kevin', 'family_name': 'Shitaye', 'locale': 'en', 'iat': 1622414547, 'exp': 1622418147, 'jti': 'f238993bd73aa948abb3435800d8b437b060cb8d'}


