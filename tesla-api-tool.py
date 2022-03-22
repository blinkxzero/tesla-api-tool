import requests
import threading
import json
import smtplib
import datetime
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

base_url = 'https://www.tesla.com/api?m=cpo_marketing_tool&a=search'
my_params = {
  'exteriors': '',
  'model': '',
  'battery': '',
  'priceRange': '',
  'city': '',
  'state': '',
  'country': 'US',
  'region': 'NA',
  'sort': '',
  'titleStatus': '',
  'zip': ''
}
new_items = {}
stored_items = {}
output_items = {}

def initalize():
  getData()

def getData():
  global new_items
  global stored_items
  global output_items
  threading.Timer(60.0, getData).start()
  response = requests.get(base_url, params = my_params)
  results = response.json()

  # Filter python objects with list comprehensions
  output_items = {}
  output_dict = [x for x in results if ((x['UsedVehiclePrice'] < 50000 and x['Model'] == 'MODEL_S' and x['TitleStatus'] == 'USED' and x['PreownedWarrantyEligibility'] == 'Pre-Owned') or (x['UsedVehiclePrice'] < 60000 and x['Model'] == 'MODEL_S' and x['TitleStatus'] == 'NEW' and x['PreownedWarrantyEligibility'] == ''))]
  
  for item in output_dict:
    output_items.update({item['Vin']: item}) 
    if item['Vin'] not in stored_items:
      stored_items.update({item['Vin']: item})
      new_items.update({item['Vin']: item})

  for item in stored_items:
    if item not in output_items:
      del stored_items[item]

  print("----------------------")
  print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
  print("----------------------")
  print("Stored Items")
  print(stored_items.keys())
  print("New Items")
  print(new_items.keys())
  print("")

  # send email
  if len(new_items) > 0:
    sendEmail(output_dict)

def sendEmail(data):
  global new_items
  global stored_items
  global output_items

  # me == my email address
  # you == recipient's email address
  email_from = "youremail@gmail.com"
  email_from_password = "password"
  email_to = "youremail@gmail.com"

  # Create message container - the correct MIME type is multipart/alternative.
  msg = MIMEMultipart('alternative')
  msg['Subject'] = "Tesla Updates ({count} New)".format(count=len(new_items))
  msg['From'] = email_from
  msg['To'] = email_to

  # Create the body of the message (a plain-text and an HTML version).
  html = """\
  <html>
    <head></head>
    <body>
  """
  for item in data:
    if item['Vin'] in new_items:
      battery = item['Badge']
      titlestatus = item['TitleStatus'].lower()
      year = item['Year']
      link = "https://www.tesla.com/{titlestatus}/{VIN}".format(VIN=item['Vin'], titlestatus=titlestatus)
      price = '${:,.2f}'.format(item['UsedVehiclePrice'])

      html += """
        <p>{titlestatus} - {battery} - <b>{price}</b> - {year} - {link}</p>
      """.format(link=link, price=price, titlestatus=titlestatus, battery=battery, year=year)

  html += """
    <p>
    -------------------------------------------------------<br>
    - ALL LISTINGS<br>
    -------------------------------------------------------<br>
    </p>
  """

  for item in data:
    if item['Vin'] in stored_items:
      battery = item['Badge']
      titlestatus = item['TitleStatus'].lower()
      year = item['Year']
      link = "https://www.tesla.com/{titlestatus}/{VIN}".format(VIN=item['Vin'], titlestatus=titlestatus)
      price = '${:,.2f}'.format(item['UsedVehiclePrice'])

      html += """
        <p>{titlestatus} - {battery} - <b>{price}</b> - {year} - {link}</p>
      """.format(link=link, price=price, titlestatus=titlestatus, battery=battery, year=year)

  html += """    
    </body>
  </html>
  """

  # Record the MIME types of both parts - text/plain and text/html.
  html_text = MIMEText(html, 'html')
  msg.attach(html_text)

  # Send the message via SMTP server.
  s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  s.ehlo()
  s.login(email_from, email_from_password)
  # sendmail function takes 3 arguments: sender's address, recipient's address
  # and message to send - here it is sent as one string.
  s.sendmail(email_from, email_to, msg.as_string())
  s.close()
  new_items = {}

  #print(data)

initalize()