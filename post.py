import requests
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
url="https://requestb.in/13935r61"

related = MIMEMultipart('related')

submission = MIMEText('image', 'jpeg', 'utf8')
submission.set_payload(open('signs/3.jpg', 'rb').read())
related.attach(submission)

# document = MIMEText('image', 'plain')
# document.set_payload(open('signs/3.jpg', 'rb').read())
# related.attach(document)

body = related.as_string().split('\n\n', 1)[1]
headers = dict(related.items())

r = requests.post(url, data=body, headers=headers)