from flask import Flask, render_template, request, session
from waitress import serve
from webtraining import get_training_example
import os
import json

username = "No_Name_Provided"
train_example = {}

app = Flask(__name__)
app.secret_key = 'pleasepleasepleasebesecure'.encode('utf8')

@app.route("/")
@app.route("/index")
def index():
    i=0
    return render_template("index.html")

@app.route("/training")
def training():

    session["username"] = request.args.get("username").replace(" ", "").strip()
    
    
    current_team, new_1, new_0, train = get_training_example()
    session["train_example"] = train

    return render_template(
        "training.html",
        cosmog_train_string= current_team,
        train_new_0 = new_1,
        train_new_1 = new_0,
        uname= session.get("username")
    )

@app.route("/training_disregard")
def training_disregard():

    train_example = session.get("train_example")

    train_example["Better"] = 0
    
    u = session.get("username")

    train_data = {}
    if os.path.exists("/data/" + u + "_training_data.json"):
        with open("/data/" + u + "_training_data.json", "r") as file:
                train_data = json.load(file)

        curr_index = int(max(list(map(int, train_data.keys()))))
        train_data[curr_index + 1] = train_example

        with open("/data/" + u + "_training_data.json", "w") as file:
                json.dump(train_data,file,indent=4)
    else:
        train_data[0] = train_example

        with open("/data/" + u + "_training_data.json", "w") as file:
                json.dump(train_data,file,indent=4)
         

    current_team, new_1, new_0, train = get_training_example()
    session["train_example"] = train

    return render_template(
        "training.html",
        cosmog_train_string= current_team,
        train_new_0 = new_1,
        train_new_1 = new_0,
        uname= session.get("username")
    )

@app.route("/training_disregard_2")
def training_disregard_2():

    train_example = session.get("train_example")

    train_example["Better"] = 1
    
    u = session.get("username")

    train_data = {}
    if os.path.exists("/data/" + u + "_training_data.json"):
        with open("/data/" + u + "_training_data.json", "r") as file:
                train_data = json.load(file)

        curr_index = int(max(list(map(int, train_data.keys()))))
        train_data[curr_index + 1] = train_example

        with open("/data/" + u + "_training_data.json", "w") as file:
                json.dump(train_data,file,indent=4)
    else:
        train_data[0] = train_example

        with open("/data/" + u + "_training_data.json", "w") as file:
                json.dump(train_data,file,indent=4)
         

    current_team, new_1, new_0, train = get_training_example()
    session["train_example"] = train

    return render_template(
        "training.html",
        cosmog_train_string= current_team,
        train_new_0 = new_1,
        train_new_1 = new_0,
        uname= session.get("username")
    )


@app.route("/training_disregard_3")
def training_disregard_3():
    
    current_team, new_1, new_0, train = get_training_example()
    session["train_example"] = train

    return render_template(
        "training.html",
        cosmog_train_string= current_team,
        train_new_0 = new_1,
        train_new_1 = new_0,
        uname= session.get("username")
    )

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port= 8000)