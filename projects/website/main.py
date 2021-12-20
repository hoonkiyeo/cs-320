# project: p4
# submitter: yeo9
# partner: none
# hours: 40


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
from flask import Flask, request, jsonify, Response
import re
from io import BytesIO

matplotlib.use('Agg')
plt.rcParams["font.size"] = 18

app = Flask(__name__)
df = pd.read_csv("main.csv") #Best Halloween candies

#https://www.kaggle.com/fivethirtyeight/the-ultimate-halloween-candy-power-ranking
#The Ultimate Halloween Candy Power Ranking

global counter #keeping track of how many times the home page has been visited
counter = 0
global cnt_A #version A - blue
cnt_A = 0
global cnt_B #version B - red
cnt_B = 0

@app.route('/')
def home():
    global counter
    counter += 1
    if counter <= 10:
        if counter %2 == 0:
            source = "A"
            color = "Blue"
        else:
            source = "B"
            color = "Red"
    else:
        if cnt_A >= cnt_B:
            color = "Blue"
            source = "A"
        else:
            color = "Red"
            source = "B"
    
    with open("index.html") as f:
        html = f.read()
        
    html = html.replace("<COLOR>", color)
    html = html.replace("<VERSION>", source)

    return html


# NOTE: app.run never returns (it runs for ever, unless you kill the process)
# Thus, don't define any functions after the app.run call, because it will
# never get that far.

#browse
@app.route('/browse.html')
def browse():
    html = """<html>
            <body>
            <h1>Browse</h1>
            {}
            </body>
            </html>""".format(df.to_html())
    
    return html

#email
@app.route('/email', methods=["POST"])
def email():
    email = str(request.data, "utf-8")
    if re.match(r"^\D{1}\w*@\w+\.com$", email): # 1
        with open("emails.txt", "a") as f: # open file in append mode
            f.write(email + "\n") # 2
        with open("emails.txt", "r") as f:
            n = len(f.read().strip().split("\n"))
        return jsonify(f"thanks, you're subscriber number {n}!")
    return jsonify("Invalid email address!") # 3


#donation
@app.route('/donate.html')
def donate():
    with open("donate.html") as f:
        html = f.read()
    if len(request.args) > 0: #query string
        global cnt_A
        global cnt_B
        source = request.args["from"]
        if source == "A":
            cnt_A += 1
        elif source == "B":
            cnt_B += 1
         
    return html

#robot.txt
@app.route('/robots.txt')
def robo():
    return Response("""
User-Agent: hungrycaterpillar
Disallow: /browse.html

User-Agent: busyspider
Disallow: /
""", headers = {"Content-Type": "text/plain"})

#figure1&2
@app.route("/candy.svg")
def candy():
    variable = request.args["variable"]
    fig, ax = plt.subplots()
    df[variable].plot.hist(ax=ax,bins=50,color = "red")
    ax.set_xlabel(variable)
    ax.set_ylabel("Frequency")
    plt.title(variable + " for Halloween candies")
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format = "svg", bbox_inches = "tight")
    plt.close(fig)
    return Response(fake_file.getvalue(), headers = {"Content-Type": "image/svg+xml"})
    
    

#figure3
@app.route("/candy2.svg")
def candy2():
    fig,ax = plt.subplots()
    df.plot.scatter("sugarpercent", "winpercent", ax = ax)
    
    ax.set_xlabel("sugarpercent")
    ax.set_ylabel("winpercent")
    plt.title("Sugarpercent vs Winpercent")
    fake_file = BytesIO()
    ax.get_figure().savefig(fake_file, format = "svg", bbox_inches = "tight")
    plt.close(fig)
    return Response(fake_file.getvalue(), headers = {"Content-Type": "image/svg+xml"})
    

    
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=False) # don't change this line!