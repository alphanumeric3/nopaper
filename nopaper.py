import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import time
import requests

# each key here must be a message type that the HP MFPs use
symbols = {
    "information": "✅",
    "warning": "⚠️",
    "error": "❌"
}

env = Environment(
	loader = FileSystemLoader("."),
	autoescape = select_autoescape()
)

# load the list of printers
with open("printers.json", "r") as file:
    printers = json.load(file)

# variables for jinja2 to reference. each printer gets an entry for its name
msg_list = {} # messages per printer
status_list = {} # current status per printer

# prepare the data
for printer in printers:
    # here we make a request to the printer
    # TODO: implement this
    # response = requests.get(f"{}")
    # messages = response.json()
    # below is example data for this
    messages = [
        {
            "type": "warning",
            "priority": 10,
            "message": "ink is low, or something like that"
        },
        {
            "type": "error",
            "priority": 100,
            "message": "[some code you have to look up online]"
        },
        {
            "type": "information",
            "priority": 50,
            "message": "signing out"
        }
    ]

    # sort messages by priority in descending. order
    messages.sort(key=lambda m: m["priority"], reverse=True) 

    status = "info"
    for msg in messages:
        status = msg["type"]
        # error takes the highest priority
        if msg["type"] == "error":
            break

    # after getting the messages, add them to a dictionary
    # so that the jinja2 template can read them
    msg_list[printer] = messages
    # same for the status
    status_list[printer] = status

    print(printers,msg_list,status_list)

template = env.get_template("index.j2.html")

current_time = time.asctime(time.gmtime())

with open("index.html", "w") as page:
    page.write(template.render(
        symbols=symbols,
        printers=printers,
        msg_list=msg_list,
        status_list=status_list,
        ts=current_time
    ))
