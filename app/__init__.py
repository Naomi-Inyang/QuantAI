from .error_handler import register_error_handlers
from .controllers import routes_blueprint
from dotenv import load_dotenv
from flask_cors import CORS
from .config import Config
from .extensions import *
from .constants import *
from flask import Flask 

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger


load_dotenv()

def create_app(config_class=Config):
    app = Flask(__name__)

    app.config.from_object(config_class)

    CORS(app)

    register_error_handlers(app) 
    register_blueprints(app)
    initialize_extensions(app)
    run_scheduler(app)

    if app.config.get("DEBUG"):  
        app.run(debug=True)

    return app


def initialize_extensions(app):
    database.init_app(app)

    db_migration.init_app(app, database)


def register_blueprints(app):
    app.register_blueprint(routes_blueprint)

def run_scheduler(app):
    from .jobs.store_forecasts import store_forecasts
        
    scheduler = BackgroundScheduler()
    scheduler.add_job(store_forecasts, IntervalTrigger(hours=12), args=[app])
    scheduler.start()

