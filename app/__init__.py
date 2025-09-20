from flask import Flask
from flasgger import Swagger


def create_app():
    app = Flask(__name__)

    swagger = Swagger(app)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    # Redirect / → /apidocs
    @app.route('/')
    def index():
        return redirect('/apidocs')

    return app
