from utils import send_email_report

# Replace with your own email for testing
test_email = "nirmayee.ninawe24@vit.edu"

send_email_report(
    to_email=test_email,
    subject="🧪 Test Email from TuneWithin",
    body="This is a test email to verify that the email-sending function is working!"
)
