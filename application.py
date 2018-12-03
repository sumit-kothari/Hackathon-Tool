from flask import Flask, render_template, session
from datetime import timedelta
from routes_dir import index_page, signin_page, signup_page, competition_page, discussion_page, terms_page, profile_page, quiz_page, teams_page
import constants

app = Flask(__name__)
app.secret_key = constants.APP_SECRET_KEY

app.register_blueprint(index_page)
app.register_blueprint(signin_page)
app.register_blueprint(signup_page)
app.register_blueprint(competition_page)
app.register_blueprint(discussion_page)
app.register_blueprint(terms_page)
app.register_blueprint(profile_page)
app.register_blueprint(quiz_page)
app.register_blueprint(teams_page)


@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=constants.SESSION_TIMEOUT_MINUTES)


@app.errorhandler(404)
def page_not_found(e):
   return redirect("/")


if __name__ == '__main__':
    app.run(port=5000, debug=True)
