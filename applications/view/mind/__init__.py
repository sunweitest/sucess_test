from applications.view.mind.mind_case import mind_bp



def register_mind_view(app):
    app.register_blueprint(mind_bp)