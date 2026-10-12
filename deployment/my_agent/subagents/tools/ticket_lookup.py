import json

#kyra and jimson
def get_ticket_status(ticketNum:str) -> str:

    """Retrieves the information for a ticket.

    Args:
        ticketNum (str): The ticket number (e.g., "1234", "4572").

    Returns:
        ticket (str): A string containing the ticket information.
            If 'no ticket found': no ticket was found for this ticket number.
            Otherwise, ticket contains the following information:
                Subject: A short description of the issue.
                Ticket number: the ticket number.
                Description: a detailed description of the issue.
                Status: describes whether or not the issue has been resolved.
                    if 'Resolved': the issue has been resolved.
                    if 'Not resolved': the issue has not been resolved yet.

    """

    #load ticket objects 
    with open('tickets.json', "r") as f:
        tickets = json.load(f)

    f.close() 

    #try to find ticket with given ticket number. If ticket is found, return its chunk/ticket.

    for ticket in tickets['tickets']:
        if ticket['Ticket number'] == ticketNum:
            return ticket

 #if ticket with correct ticket number isn't found, return 'no ticket found'
    return 'no ticket found'