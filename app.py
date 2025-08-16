import os
from flask import Flask
from config import Config
from models import db, User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Dossier d’upload (chemin absolu)
    upload_path = os.path.join(app.root_path, 'uploads')
    os.makedirs(upload_path, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_path

    # Init DB
    db.init_app(app)

    # Enregistrer les routes (blueprint)
    from routes import main_bp
    app.register_blueprint(main_bp)

    # Créer tables + admin par défaut
    with app.app_context():
        db.create_all()
        if User.query.count() == 0:
            admin = User(username="admin", role="admin")
            admin.set_password("admin123")
            db.session.add(admin)
            db.session.commit()

    # Handlers d’erreurs
    from flask import render_template
    @app.errorhandler(404)
    def not_found(e):
        return render_template("error.html", code=404, message="Page introuvable."), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template("error.html", code=500, message="Erreur serveur."), 500

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)  # en production: debug=False
