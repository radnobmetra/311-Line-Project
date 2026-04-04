from pathlib import Path

TICKETS_PATH = Path("tickets.txt")

with open(TICKETS_PATH, "r") as file:
    DOCUMENT = file.read()

#looks up ticket number
def search_tickets(ticketNumber: str) -> str:

    ticketNumber = ticketNumber.lower()

    #chunking by blank line seperation
    chunks = DOCUMENT.split("\n\n")

    #possible as each ticket number is unique
    for chunk in chunks:
        if ticketNumber in chunk.lower():
            return chunk
        
    return "Ticket Number Does Not Exist."

"""
    #scoring chunks ticket number
    scored = []
    for chunk in chunks:
        if ticketNumber in chunk.lower():
            scored.append((ticketNumber, chunk))

    if not scored: return "Ticket Number Does Not Exist."


    topChunk = scored[0][1]
    return topChunk
"""
        #only serach for ticket number and return? or append bottom two lines to ticket number search? by join to return? no need for score maybe as each ticket numebr is unique?