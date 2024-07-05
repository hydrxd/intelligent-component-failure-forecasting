from flask import *
from datetime import datetime, timedelta

app = Flask(__name__)

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.permanent_session_lifetime = timedelta(minutes=30)


@app.route("/", methods=["GET"])
def home():
    if (request.method == "GET"):
        return render_template("home.html")
    
@app.route("/analysis", methods=["GET"])
def analysis():
    if (request.method == "GET"):
        return render_template("analysis.html")
