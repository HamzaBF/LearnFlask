from flask import Blueprint,jsonify,abort
from app.modeles import Projet, Avis, db,Contact
from flask_jwt_extended import jwt_required, get_jwt

bp = Blueprint('api_0_1', __name__,url_prefix='/v0.1')





@bp.errorhandler(400)
@bp.errorhandler(401)
@bp.errorhandler(403)
@bp.errorhandler(404)
def erreur(e):
    return jsonify(error=str(e)), e.code



@bp.get('/contacts')
@jwt_required()
def contacts_get():
    claims = get_jwt()
    roles = claims.get('roles', [])
    if 'admin' not in roles:
        abort(403)
    # contacts = Contact.query.all()
    contacts = db.session.query(Contact)
    return [c.dto() for c in contacts]




@bp.get('/projets/<int:idprojet>/avis')
def projets_avis_get(idprojet):

    projet = db.get_or_404(Projet, idprojet)
    return [a.dto()
        for a in projet.avis if a.ok]
