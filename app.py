from applications import create_app
from flask_migrate import Migrate
from applications.extensions import db

app = create_app()

migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
