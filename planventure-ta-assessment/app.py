import os
from flask import Flask
from flask_cors import CORS
from models.database import db
from routes.assessments_fixed import assessments
from routes.questions import questions

def create_app(config=None):
    app = Flask(__name__)
    CORS(app)

    if config:
        app.config.update(config)
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'assessment.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    if not os.path.exists(app.instance_path):
        os.makedirs(app.instance_path)

    db.init_app(app)
    
    app.register_blueprint(assessments, url_prefix='/api')
    app.register_blueprint(questions, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        db.create_all()
    app.run(debug=True)
