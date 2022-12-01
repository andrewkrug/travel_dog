from email import message
import json
import logging
import os
import requests
import subprocess
import sys
from ddtrace import tracer
from ddtrace.contrib.trace_utils import set_user
from decimal import Decimal
from flask import Flask
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flaskext.markdown import Markdown
from flask.logging import default_handler
from flask_dynamo import Dynamo
from functools import wraps
from pythonjsonlogger import jsonlogger


import ldclient
import config
import helpers
import models
import dynamo_helpers
from ldclient import Config
import time
import random


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)

logger = logging.getLogger(__name__)
logHandler = logging.StreamHandler(sys.stdout)
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)

session = dynamo_helpers.get_session()
dynamo = Dynamo()
ldclient.set_config(Config(config.get_ld_api_key()))
not_enabled_message = "Sorry that feature is not currently available."

LD_USER = {"key": "username", "name": None}

try:
    tracer.configure(hostname="172.17.0.1")
except Exception:
    pass

# Define our models for the users in the application
def create_app():
    app = Flask(__name__)
    app.config["DYNAMO_TABLES"] = [
        dict(
            TableName="traveldog-users",
            KeySchema=[dict(AttributeName="username", KeyType="HASH")],
            AttributeDefinitions=[dict(AttributeName="username", AttributeType="S")],
            ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5),
        )
    ]
    dynamo.init_app(app)
    app.logger.info(
        "The application is initialized and the dynamodb tables are created."
    )
    tables = dynamo_helpers.list_tables(session)
    app.logger.info(f"The tables present in the db are: {tables}.")
    if config.CREATE_TABLES == "True":
        if len(tables.get("TableNames", [])) == 0:
            with app.app_context():
                dynamo.create_all()
        else:
            app.logger.info("Skipping the creation of new tables.")
            tables = dynamo_helpers.list_tables(session)
            app.logger.info(f"The tables present in the db are: {tables}.")
    else:
        app.logger.info("Skipping the creation of tables.")
    return app


app = create_app()
Markdown(app)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.logger.setLevel(logging.DEBUG)
logger.debug("Test test debug.")


def login_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        username = request.cookies.get("username")
        if username != None:
            LD_USER["name"] == username
            return f(*args, **kwargs)
        else:
            return (
                jsonify(msg="You must be authenticated to use this endpoint."),
                403,
            )

    return decorator


def is_authenticated():
    username = request.cookies.get("username")
    if username != None:
        app.logger.info(f"User is authenticated successfully as user={username}")
        return True
    else:
        app.logger.info(f"There is no user logged in for this request.")
        return False


@app.before_request
def before_request():
    username = request.cookies.get("username")
    if username != None:
        LD_USER["name"] = username
    else:
        LD_USER["name"] = None

    flag_value = ldclient.get().variation("tarpitting", LD_USER, False)

    if flag_value == True:
        app.logger.info(f"Tarpitting activated for user={username}")
        sleep_value = random.randint(5, 10)
        time.sleep(sleep_value)


@app.route("/changelog")
def changelog():
    CHANGELOG_FILE = "CHANGELOG.md"
    fh = open(CHANGELOG_FILE)
    mkd_text = fh.read()
    fh.close()
    return render_template("changelog.html", mkd_text=mkd_text)


@app.route("/auth", methods=["GET", "POST"])
def auth():
    app.logger.info("Auth code triggered.")
    error = None
    resp = make_response(
        render_template(
            "auth.html", authed=is_authenticated(), user=request.cookies.get("username")
        )
    )

    username = request.args.get("username")
    if username != None:
        app.logger.info("Attempting login.")
        form_value = username

        if form_value == None:
            resp = make_response(
                render_template("auth.html", authed=is_authenticated(), user=None)
            )
            resp.delete_cookie("username")
            app.logger.info("Successfully logged user out.")
        else:
            try:
                app.logger.info(f"Attepting a sign in for user={form_value}")
                session = dynamo_helpers.get_session()
                table = dynamo_helpers.get_table(session)
                users = models.User(table)
                u = users.find(form_value)
                app.logger.info(
                    f"The result of attempting to log in the user is result={u}"
                )
                if u["username"] == form_value:
                    resp = make_response(
                        render_template(
                            "auth.html",
                            authenticated=True,
                            user=form_value,
                        )
                    )
                    resp.set_cookie("username", form_value)
                    LD_USER["name"] = form_value
                    set_user(tracer, user_id=form_value)
                    app.logger.info(f"Session cookie set for user={form_value}")
                    return resp
            except Exception as e:
                error = (
                    "There was an issue logging in. Do you need to create an account?"
                )
                resp = make_response(
                    render_template(
                        "auth.html",
                        authenticated=is_authenticated(),
                        user=None,
                        error=error,
                    )
                )
                app.logger.error(f"Session could not be created due to error={e}")
    return resp


@app.route("/")
def index():
    session = dynamo_helpers.get_session()
    table = dynamo_helpers.get_table(session)
    user_obj = models.User(table)
    flash = None
    adversary = False
    if ldclient.get().variation("adversary-data", LD_USER, False):
        adversary = True
        user_obj.adversary = True
        app.logger.info(
            f"The user user={LD_USER['name']} has been identified as an adversary."
        )

    if ldclient.get().variation("adversary-engage-hire", LD_USER, False):
        adversary = True
        flash = "Do you like breaking things for a living?  Maybe consider checking out our careers page!"
        app.logger.info(
            f"The user user={LD_USER['name']} is sophisticated enough to try to hire."
        )

    users = user_obj.all()
    users_lol = [[users[0]]]

    idx = 0

    for user in users[1:-1]:
        if len(users_lol[idx]) == 3:
            users_lol.append([user])
            idx = idx + 1
        else:
            app.logger.info(idx)
            users_lol[idx].append(user)

    app.logger.debug("The application is initialized and someone visited the index.")
    return render_template(
        "home.html", users=users_lol, flash=flash, adversary=adversary
    )


@app.route("/v1/seed")
def seed():
    flag_value = ldclient.get().variation("seed-route", LD_USER, False)
    adversary_data = ldclient.get().variation("adversary-data", LD_USER, False)
    if flag_value == True:
        app.logger.info("Seed route is active.  Generating users for the database.")
        session = dynamo_helpers.get_session()
        table = dynamo_helpers.get_table(session)
        models.seed(table)
        data = table.scan(Limit=100, Select="ALL_ATTRIBUTES")
        if adversary_data == True:
            user_obj = models.User(table)
            user_obj.adversary = True
            data = dict(Count=100, Items=[])
            for x in range(0, 100):
                data["Items"].append(user_obj.fake)
        app.logger.debug("Returning users from the seed route.")
        return jsonify(dict(data))
    else:
        return jsonify(status=500, message=not_enabled_message), 500


@app.route("/profile", methods=["POST", "GET"])
@login_required
def profile():
    flag_value = ldclient.get().variation("profile-editing", LD_USER, False)

    if flag_value == True:
        app.logger.info("Profile route is active.  Generating users for the database.")
        session = dynamo_helpers.get_session()
        table = dynamo_helpers.get_table(session)
        u = models.User(table)
        profile = u.find(request.cookies.get("username"))

        app.logger.info(request.method)

        if len(list(request.args.keys())) > 1:
            app.logger.info(
                f"Attempting an update using submitted form data for user={LD_USER['name']}"
            )
            username = request.args.get("username")
            surname = request.args.get("surname")
            given_name = request.args.get("given_name")
            favorite_location_url = request.args.get("favorite_location_url")

            profile["favorite_location_url"] = favorite_location_url
            h = {"Content-type": "application/json"}
            try:
                cookie = request.headers["Cookie"]
                body = json.dumps(profile, cls=DecimalEncoder)
                headers = {
                    "Content-type": "application/json",
                    "Accept": "text/plain",
                    "Cookie": cookie,
                }
                r = requests.get(
                    f"{config.BASE_URL}/v1/user", headers=headers, params=request.args
                )
                app.logger.info(f"The status of the update was status={r.status_code}")
                set_user(tracer, user_id=LD_USER["name"])
            except Exception as e:
                app.logger.error(
                    f"The user user={LD_USER['name']} could not be updated due to error={e}"
                )

        return render_template("profile.html", profile=profile)
    else:
        user_id = LD_USER["name"]
        app.logger.debug(
            f"Feature flag is disabled for profile editing.  Redirecting user_id={user_id}"
        )
        return redirect(url_for("profile_view", flash="Temporarily disabled"), code=302)


@app.route("/profile/view", methods=["POST", "GET"])
@login_required
def profile_view():
    set_user(tracer, user_id=LD_USER["name"])
    session = dynamo_helpers.get_session()
    table = dynamo_helpers.get_table(session)
    u = models.User(table)
    profile = u.find(LD_USER["name"])
    favorite_location_url = profile["favorite_location_url"]
    safe_img_name = helpers.url_to_filename(favorite_location_url)
    return render_template(
        "profileview.html", profile=profile, safe_img_name=safe_img_name
    )


@app.route("/v1/preview", methods=["POST", "GET"])
@login_required
def site_preview():
    set_user(tracer, user_id=LD_USER["name"])
    if request.method == "POST":
        data = request.json
        favorite_location_url = data.get(
            "favorite_location_url", "http://placekitten.com/1024/768"
        )
        safe_name = helpers.url_to_filename(favorite_location_url)
    else:
        favorite_location_url = "http://placekitten.com/1024/768"
        if request.args.get("favurl") != None:
            favorite_location_url = request.args.get("favurl")
        safe_name = helpers.url_to_filename(favorite_location_url)

    cmd = f"cd static/custom-locations/ && wkhtmltoimage -f png -n {favorite_location_url} {safe_name}.png"
    app.logger.info(f"The command executed was command={cmd}")
    p = subprocess.Popen(f"{cmd}", shell=True, stdout=subprocess.PIPE)
    return jsonify(status=200, filename=f"/static/custom-locations/{safe_name}.png")


@app.route("/v1/up")
@login_required
def ping():
    set_user(tracer, user_id=LD_USER["name"])
    flag_value = ldclient.get().variation("site-up", LD_USER, False)

    if flag_value == True:
        destination = request.args.get("favurl", "http://google.com")
        try:
            destination = destination.split("http://")[1]
        except Exception:
            pass

        try:
            destination = destination.split("https://")[1]

        except Exception:
            pass

        command = f"/bin/ping -c 2 {destination}"
        app.logger.info(f"The command executed was {command}")
        with subprocess.Popen(["/bin/sh", "-c", command]) as p:
            try:
                p.wait(timeout=3)
                result = True
            except subprocess.TimeoutExpired:
                result = False
    else:
        result = "Feature not available."
    return jsonify(result)


@app.route("/v1/user", methods=["GET", "POST"])
@login_required
def user_api():
    set_user(tracer, user_id=LD_USER["name"])
    ld_user = LD_USER
    session = dynamo_helpers.get_session()
    table = dynamo_helpers.get_table(session)
    user_obj = models.User(table)

    if len(list(request.args.keys())) > 1:
        data = request.args
        app.logger.info(f"Attempting an update on the payload={data}")
        username = data["username"]
        # ensure user can only update itself
        valid_profile_keys = [
            "id",
            "username",
            "surname",
            "given_name",
            "age",
            "location",
            "address",
            "favorite_location_img",
            "favorite_location_url",
        ]
        if username == ld_user["name"]:
            app.logger.info(f"Valid update.  Updating user for user={username}.")
            u = user_obj.find(data["username"])
            for k in data.keys():
                if k in valid_profile_keys:
                    # attempt an update
                    data_to_update = data.get(k)
                    if data_to_update != None and data_to_update != u[k]:
                        u[k] = data_to_update
                        app.logger.info(
                            f"Attempting to update key={k}, with value={data_to_update}"
                        )
            app.logger.info(user_obj.surname)
            user_obj.update(u)

            return jsonify(status=200, message=f"Updated the profile for {username}")
        else:
            app.logger.error(
                f"The username {username} did not match the LD_USER ld_user={ld_user['name']}.  This could be an attempt at hacking."
            )
            return jsonify(status=500, message="Could not update user.")
    if len(list(request.args.keys())) == 1 and request.method == "GET":
        result = user_obj.find(request.args["username"])
        return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
