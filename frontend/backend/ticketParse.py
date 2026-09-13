import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
JSON_PATH = SCRIPT_DIR.parent.parent / "tickets.json"

#open the tickets.json file and read the data
with open(JSON_PATH, 'r') as f:
    data =  json.load(f)

    # get count of each type of ticket status

countRes = 0
countUnres = 0
countMal = 0

for tickets in data['tickets']:
    if tickets['Status'] == 'Resolved':
        countRes += 1
    elif tickets['Status'] == 'Not resolved':
        countUnres += 1
    elif tickets['Status'] == 'MALFORMED':
        countMal += 1

totalCounts = {
    "ticket_counts": [
        {
            "status": "Resolved",
            "count": countRes
        },
        {
            "status": "Not resolved",
            "count": countUnres
        },
        {
            "status": "MALFORMED",
            "count": countMal
        }
    ]
}
# Save the totalCounts to a JSON file to use for graph through npm json-server

with open('ticket_counts.json', 'w') as f:
    json.dump(totalCounts, f, indent=4)

    #NEED A WAY TO AUTOMATE THIS SCRIPT TO RUN EVERY TIME THE TICKETS.JSON FILE IS UPDATED.