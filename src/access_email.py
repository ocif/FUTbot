import imaplib
from email import policy
from email.parser import BytesParser

def get_login_code(email_address, email_password):
    # Connect to the email server and login
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(email_address, email_password)
    mail.select('inbox')

    # Search for the email containing the code (adjust the search criteria as needed)
    status, email_ids = mail.search(None, '(FROM "EA@e.ea.com" SUBJECT "Your EA Security Code is:")')
    email_id_list = email_ids[0].split()

    # If no emails match the criteria, return None
    if not email_id_list:
        return None

    # Sort email IDs in descending order (most recent first)
    sorted_email_ids = sorted(email_id_list, key=int, reverse=True)

    # Loop through the sorted email IDs and fetch the code
    for email_id in sorted_email_ids:
        status, email_data = mail.fetch(email_id, '(BODY[HEADER.FIELDS (SUBJECT)])')
        raw_subject = email_data[0][1].decode('utf-8')
        
        # Extract the code from the subject
        code = extract_code_from_subject(raw_subject)
        if code:
            mail.logout()
            return code

    mail.logout()
    return None

def extract_code_from_subject(subject):
    # Logic to extract the code from the subject
    # For example, if the code is a 6-digit number:
    import re
    match = re.search(r'(\d{6})', subject)
    if match:
        return match.group(1)
    return None
