import smtplib
import os
from email.message import EmailMessage

def send_digest(new_files, modified_files, deleted_files):
    """Sends an email digest of changes."""
    
    smtp_host = os.environ.get('SMTP_HOST')
    smtp_port = os.environ.get('SMTP_PORT', 587)
    smtp_user = os.environ.get('SMTP_USER')
    smtp_password = os.environ.get('SMTP_PASSWORD')
    recipient = os.environ.get('DIGEST_RECIPIENT') # e.g. "user@example.com"
    
    if not all([smtp_host, smtp_user, smtp_password, recipient]):
        print("Missing SMTP configuration. Skipping email.")
        return

    msg = EmailMessage()
    msg['Subject'] = 'Florida Contracts: Weekly Update Digest'
    msg['From'] = smtp_user
    msg['To'] = recipient
    
    # Build HTML body
    body = """
    <html>
    <head>
        <style>
            body { font-family: sans-serif; }
            h2 { color: #333; }
            ul { margin-bottom: 20px; }
            li { margin-bottom: 5px; }
            .badge { padding: 2px 6px; border-radius: 4px; color: white; ffont-size: 0.8em;}
            .new { background-color: #28a745; }
            .mod { background-color: #ffc107; color: black; }
            .del { background-color: #dc3545; }
        </style>
    </head>
    <body>
        <h1>Florida Contracts Digest</h1>
        <p>Here are the updates found in the latest scan:</p>
    """
    
    if new_files:
        body += "<h2><span class='badge new'>NEW</span> Contracts Found</h2><ul>"
        for f in new_files:
            body += f"<li>{f}</li>"
        body += "</ul>"
        
    if modified_files:
        body += "<h2><span class='badge mod'>MODIFIED</span> Contracts Updated</h2><ul>"
        for f in modified_files:
            body += f"<li>{f}</li>"
        body += "</ul>"
        
    if deleted_files:
        body += "<h2><span class='badge del'>DELETED</span> Contracts Removed</h2><ul>"
        for f in deleted_files:
            body += f"<li>{f}</li>"
        body += "</ul>"
        
    if not (new_files or modified_files or deleted_files):
        body += "<p><em>No changes detected this week.</em></p>"
        
    body += """
        <hr>
        <p><small>This is an automated message from your Florida Contracts Explorer.</small></p>
    </body>
    </html>
    """
    
    msg.add_alternative(body, subtype='html')

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as s:
            s.starttls()
            s.login(smtp_user, smtp_password)
            s.send_message(msg)
        print("Digest email sent successfully.")
    except Exception as e:
        print(f"Error sending email: {e}")
