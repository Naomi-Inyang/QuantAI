from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate

database = SQLAlchemy()
db_migration = Migrate()

session = database.session