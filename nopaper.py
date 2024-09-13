import json
from jinja2 import Environment, FileSystemLoader, select_autoescape
import time
import requests

# each key here must be a message type that the HP MFPs use
# from frontend code: ["error", "warning", "popup", "job-status", "notification", "message"]
symbols = {
    "": "⚙", # why does this exist!?
    "popup": "💬",
    "message": "💬",
    "notification": "✅",
    "job-status": "📰",
    "warning": "⚠️",
    "error": "❌"
}

env = Environment(
	loader = FileSystemLoader("."),
	autoescape = select_autoescape()
)

# load the list of printers
with open("printers.json", "r") as file:
    settings = json.load(file)
    printers = settings["printers"]
    tls_verify = settings["verify"]

# variables for jinja2 to reference. each printer gets an entry for its name
successful_printers = [] # printers that responded properly
msg_list = {} # messages per printer
status_list = {} # current status per printer

# prepare the data
for printer in printers:
    # here we make a request to the printer
    ip = printers[printer]["ip"]
    try:
        # TODO: find a more secure way to talk to devices. they all
        # have self-signed certificates!
        response = requests.get(
            f"https://{ip}/hp/device/MessageCenter/Summary",
            verify=tls_verify,
            timeout=2
        )
        # add it to the successful list
        successful_printers.append(printer)
    except Exception as e:
        # if the request fails, skip to the next printer
        print(f"failed to fetch info for {printer} @ {ip}")
        print(f"{type(e)}: {e}")
        continue

    messages = response.json()['messages']

    # sort messages by priority in descending order
    messages.sort(key=lambda m: m["priority"], reverse=True) 

    status = "notification"
    for msg in messages:
        status = msg["type"]
        # error messages take the highest priority
        if msg["type"] == "error":
            break

    # after getting the messages, add them to a dictionary
    # so that the jinja2 template can read them
    msg_list[printer] = messages
    # same for the status
    status_list[printer] = status

template = env.get_template("index.j2.html")

current_time = time.asctime(time.gmtime())

with open("index.html", "w", encoding="utf-8") as page:
    page.write(template.render(
        symbols=symbols,
        printers=successful_printers, # only show working printers on the page
        msg_list=msg_list,
        status_list=status_list,
        ts=current_time
    ))
