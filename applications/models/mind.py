from applications.extensions import db


#
class Mind(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60))
    create_on = db.Column(db.String(60))
    note = db.Column(db.Text)
    is_deleted = db.Column(db.Integer)