import json


def validate_ticket(ticket_number: int) -> bool:
    """Verifies if a ticket exists within tickets.json.

    Args:
        ticket_number (int): the number id of the ticket

    Returns:
        bool: True/False and ticket number.

    """

    ticket_found = False

    input_file = open("tickets.json", "r")
    tickets_json = json.load(input_file)
    for ticket in tickets_json['tickets']:

        #Convert each to ints to avoid string and int comparisons
        converted_input_ticket_num = int(ticket_number)
        converted_database_ticket_num = int(ticket['Ticket number'])

        if converted_input_ticket_num == converted_database_ticket_num:
            ticket_found = True

    if ticket_found:
        return True
    else: 
        return False