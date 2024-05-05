from flask import Blueprint,render_template
from flask_login import login_required, current_user

views = Blueprint('views',__name__)

@views.route('/')
def user():
    return render_template("user.html")

