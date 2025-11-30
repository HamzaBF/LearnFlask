from wtforms import Form , StringField , TextAreaField, validators, ValidationError
from wtforms.csrf.session import SessionCSRF
from datetime import timedelta


def info_perso(form, field):
    if any(tabou in field.data for tabou in ['@', 'http', 'adresse', 'téléphone', 'tel', 'tél']):
        raise ValidationError(f"Pas d'information personnelle dans '{ field.label.text }', s'il vous plait.")


class FormAvis(Form):
    class Meta:
        csrf = True
        csrf_class = SessionCSRF
        csrf_secret = b'6QE_LBwhg4JxTi61QmsvpdvgF8'
        csrf_time_limit= timedelta(seconds=10)
        
    auteur =  StringField('Nom ( entreprise)',[
        validators.InputRequired(),
        validators.Length(min=2,max=50),
        info_perso
    ])
    contenu = TextAreaField('Votre avis',[
        validators.InputRequired(),
        info_perso
    ])