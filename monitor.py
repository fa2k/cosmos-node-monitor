import argparse
import time
import http.client
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def get_block_height(node_host, node_port):
    conn = http.client.HTTPConnection(node_host, node_port)
    conn.request("GET", "/status")
    response = conn.getresponse()
    if response.status != 200:
        raise Exception(f"Request failed with status {response.status}")
    data = response.read()
    return json.loads(data)["result"]["sync_info"]["latest_block_height"]

def send_email(smtp_server, smtp_port, smtp_username, smtp_password, to_email, from_email, subject, message):
    """Attempt to send an email with the specified parameters.

    The return value indicates whether the email was accepted by the SMTP server.
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Secure the connection
        if smtp_username:
            server.login(smtp_username, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
        return False

def monitor_node(node_host, node_port, smtp_server, smtp_port, smtp_username, smtp_password, to_email, from_email, send_test_email, check_interval):
    if send_test_email:
        if not send_email(smtp_server, smtp_port, smtp_username, smtp_password, to_email, from_email,
                   "Test Email",
                   "This is a test email from the Cosmos node monitor script. "
                   f"It is configured to monitor {node_host}:{node_port}."):
            raise RuntimeError("Unable to send test message - quitting!")

    last_height = None
    spam = False
    while True:
        try:
            height = get_block_height(node_host, node_port)
            if last_height is not None and height <= last_height:
                if not spam:
                    spam = send_email(smtp_server, smtp_port, smtp_username, smtp_password, to_email, from_email,
                            "Node is not processing new blocks",
                            f"The node at {node_host} is not processing new blocks. "
                            f"Last block height: {last_height}, current block height: {height}")
            else:
                spam = False
            last_height = height
        except Exception as e:
            if not spam:
                spam = send_email(smtp_server, smtp_port, smtp_username, smtp_password, to_email, from_email,
                        "Node is down",
                        f"The node at http://{node_host}:{node_port} is down. Error: {str(e)}")
        time.sleep(check_interval)  # Wait for a minute before checking again

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Monitor a Cosmos node.')
    parser.add_argument('--node_host', required=True, help='The hostname or IP address of the node.')
    parser.add_argument('--node_port', default=26657, help='Port to use to query the node.')
    parser.add_argument('--smtp_server', required=True, help='The SMTP server to use to send emails.')
    parser.add_argument('--smtp_port', type=int, default=587, help='The SMTP server port to use to send emails.')
    parser.add_argument('--smtp_username', default=None, help='The SMTP username to use to send emails.')
    parser.add_argument('--smtp_password', default=None, help='The SMTP password to use to send emails.')
    parser.add_argument('--to_email', required=True, help='The email address to send notifications to.')
    parser.add_argument('--from_email', help='The sender email (defaults to to_email if not given).')
    parser.add_argument('--send_test_email', action='store_true', help='Send a test email on startup.')
    parser.add_argument('--check_interval', default=300, help='Number of seconds between each check.')
    args = parser.parse_args()

    from_email = args.from_email
    if not from_email:
        from_email = args.to_email

    monitor_node(
        args.node_host,
        args.node_port,
        args.smtp_server,
        args.smtp_port,
        args.smtp_username,
        args.smtp_password,
        args.to_email,
        from_email,
        args.send_test_email,
        args.check_interval
        )
