import os
from functools import wraps
from flask import (
    Blueprint, render_template, request, redirect, url_for,
    session, flash, send_from_directory, current_app
)
from werkzeug.utils import secure_filename
from models import db, User, Document

main_bp = Blueprint('main', __name__)

# ---------- Auth guard : forcer login partout sauf /login et static ----------
@main_bp.before_app_request
def require_login():
    from flask import request
    public_endpoints = {'main.login', 'static'}
    if request.endpoint in public_endpoints or request.endpoint is None:
        return
    if not session.get('user_id'):
        flash("Veuillez vous connecter d'abord.")
        return redirect(url_for('main.login'))

# ---------- Décorateur ADMIN ----------
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if session.get('role') != 'admin':
            flash("Accès réservé à l'administrateur.")
            return redirect(url_for('main.home'))
        return f(*args, **kwargs)
    return wrapper

# ---------- Helpers ----------
def allowed_file(filename: str) -> bool:
    if not filename or "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in current_app.config.get("ALLOWED_EXTENSIONS", set())

# ---------- Routes ----------
@main_bp.route("/")
def home():
    return render_template("dashboard.html")

@main_bp.route("/login", methods=['GET', 'POST'])
def login():
    # Si déjà connecté -> dashboard
    if session.get('user_id'):
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash("Connexion réussie.")
            return redirect(url_for('main.home'))
        flash("Nom d'utilisateur ou mot de passe incorrect.")
    return render_template("login.html")

@main_bp.route("/logout")
def logout():
    session.clear()
    flash("Vous êtes déconnecté.")
    return redirect(url_for('main.login'))

# ---- Utilisateurs (ADMIN) ----
@main_bp.route("/users")
@admin_required
def users():
    all_users = User.query.order_by(User.id.asc()).all()
    return render_template("users.html", users=all_users)

@main_bp.route("/add_user", methods=['POST'])
@admin_required
def add_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '')
    role = request.form.get('role', 'user')
    if not username or not password:
        flash("Nom d'utilisateur et mot de passe requis.")
        return redirect(url_for('main.users'))
    if User.query.filter_by(username=username).first():
        flash("Cet utilisateur existe déjà.")
        return redirect(url_for('main.users'))
    user = User(username=username, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    flash("Utilisateur ajouté.")
    return redirect(url_for('main.users'))

@main_bp.route("/delete_user/<int:user_id>")
@admin_required
def delete_user(user_id):
    user = User.query.get(user_id)
    if user and user.username != 'admin':
        db.session.delete(user)
        db.session.commit()
        flash("Utilisateur supprimé.")
    else:
        flash("Impossible de supprimer cet utilisateur.")
    return redirect(url_for('main.users'))

# ---- Documents (liste pour tous; ajout/suppression ADMIN) ----
@main_bp.route("/documents")
def documents():
    category = request.args.get('category')
    q = Document.query
    if category:
        q = q.filter_by(category=category)
    docs = q.order_by(Document.id.desc()).all()
    return render_template("documents.html", documents=docs)

@main_bp.route("/add_document", methods=['POST'])
@admin_required
def add_document():
    title = request.form.get('title', '').strip()
    category = request.form.get('category', 'Résumé')
    file = request.files.get('file')

    if not title or not file or not file.filename:
        flash("Titre et fichier requis.")
        return redirect(url_for('main.documents'))

    if not allowed_file(file.filename):
        flash("Extension non autorisée.")
        return redirect(url_for('main.documents'))

    filename = secure_filename(file.filename)
    save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)

    # Éviter l'écrasement : suffixe si le fichier existe
    base, ext = os.path.splitext(filename)
    i = 1
    while os.path.exists(save_path):
        filename = f"{base}_{i}{ext}"
        save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        i += 1

    file.save(save_path)
    doc = Document(title=title, category=category, filename=filename)
    db.session.add(doc)
    db.session.commit()
    flash("Document ajouté.")
    return redirect(url_for('main.documents'))

@main_bp.route("/delete_document/<int:doc_id>")
@admin_required
def delete_document(doc_id):
    doc = Document.query.get(doc_id)
    if doc:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.filename)
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
        db.session.delete(doc)
        db.session.commit()
        flash("Document supprimé.")
    return redirect(url_for('main.documents'))

@main_bp.route("/download/<int:doc_id>")
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)
    return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.filename, as_attachment=True)
