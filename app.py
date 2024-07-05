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
    
@app.route("/analysis/articulated_truck", methods=["GET"])
def articulated_truck():
    if (request.method == "GET"):
        return render_template("articulated_truck.html")
    
@app.route("/analysis/asphalt_paver", methods=["GET"])
def asphalt_paver():
    if (request.method == "GET"):
        return render_template("asphalt_paver.html")

@app.route("/analysis/backhoe_loader", methods=["GET"])
def backhoe_loader():
    if (request.method == "GET"):
        return render_template("backhoe_loader.html")
    
@app.route("/analysis/dozer", methods=["GET"])
def dozer():
    if (request.method == "GET"):
        return render_template("dozer.html")
    
@app.route("/analysis/excavator", methods=["GET"])
def excavator():
    if (request.method == "GET"):
        return render_template("excavator.html")
