import requests # This is to access a website
import time # This is to loop code over a specified time
from bs4 import BeautifulSoup # This is to scrape, parse and view html code
from win10toast import ToastNotifier # This is for windows notifications
from email.message import EmailMessage # Used for creating emails
import ssl # Secure connection
import smtplib # Email Connection

# Website to scrape
# TODO - insert real data
URL = "fakewebsite.com"

# Intializing variables
global current
current = [0,0] # current[0]= # of thumbsUp, current[1]= # of thumbsDown
global previous
previous = [0,0] # previous[0]= # of thumbsUp, previous[1]= # of thumbsDown

# Loop timer (number of seconds you wish to wait before the website is scraped and checked for changes)
# --- REFERENCE ---
# seconds | Minutes
# -----------------
#     60  |  1 
#    900  |  15
#   1800  |  30 
#   3600  |  60 
sleepTime = 5

# Windows 10 notification
toast = ToastNotifier()

# Up-to-date (2023) guide to setup GMAIL access in python (gmail recently changed accessing emails in 2022):
# https://www.youtube.com/watch?v=g_j6ILT-X0k
email = EmailMessage()
title = "New rating recieved!"

# TODO - insert real data
emailSender = "fakemailsender@gmail.com"
emailPassword = "fakepassword" # The link explains how to get this
emailReceiver = "fakemailreceiver@gmail.com"

email["From"] = emailSender
email["To"] = emailReceiver
email["Subject"] = title

###########################
###     DEFINITIONS     ###
###########################
def RunWebScraper():
    # Send a GET request to the website to receive the response
    response = Scrape(URL)
    
    # Exctract the raw html from the response
    rawHTML = ExtractRawHTML(response)

    # Example: Getting the number of "thumbs-up" and "thumbs-down" on my website
    ''' Note:
        This may be the trickiest part. 
        Summary of what to do here:
            1. Use the "view page source" on the website you're scraping (right click the webpage).
            2. Try to identify html tags,ids,classes,etc  <p>,<h1>,<div>,<nav>,<li> || class="something" || id="something" for the stuff you are trying to scrape off the website.
                Example: the html tag: <li> contains all the lecture documents
                        <body>
                            <div class="lectures">
                                <li>Lecture 1.pdf</li>
                                <li>Lecture 2.pdf</li>
                                <li>Lecture 3.pdf</li>
                            </div>
                        </body>
            
            There's lots of variety and different ways to do this (depends on the website, and webscraper) and sometimes it can be very difficult.
            I've found these may help when trying to scrape certain things from the website:
            
            |Sample html search for certain criteria|
            # specificIDs = rawHTML.find(id="form-group")
            # specificClasses = rawHTML.find(class_="dropdown-menu")
            # specificTags = rawHTML.find_all("p")
            # specificTagsWithSpecificClass = rawHTML.find_all("li", class_="nav-item")
            # specificTagWithSpecificString = rawHTML.find_all("p", string="Welcome.")

            For my website, the id="numberOfUps" (you can see in the page source) is where I store the thumbs-up and thumbs-down value.
            Once you have the proper stuff aquired, you can use .get_text() to get the text (in my case the # of thumbs-up and thumbs-down)
    '''
    ratings = rawHTML.find_all(id="numberOfUps")
    current[0] = ratings[0].get_text()
    current[1] = ratings[1].get_text()

    # Storing the number of thumbs-up/down in a message to send by email or notification
    message = "You now have " + str(current[0]) + " thumbs up and " + str(current[1]) + " thumbs down."

    # Check for change in the thumbs-up/down
    if(ThumbsChanged()):
        # Change Found
        print("Change found: True")

        # Email
        SendEmail(message)

        # Windows 10 notification (works - but only in Windows 10 machines!)
        # SendNotification(message)
    else:
        # No change
        print("Change found: False")
    
def Scrape(websiteAddress):
    try:
        result = requests.get(websiteAddress) 
    except:
        print(websiteAddress + " is not be a valid website to scrape.")
    return result   

def ExtractRawHTML(data):
    # return data.text # This might also work
    return BeautifulSoup(data.content, 'html5lib')

def MakeItLookNice(rawHTML):
     # prettify() is a built in function that can help make the raw html look more readable, although I didn't use it
    return rawHTML.prettify()

def ThumbsChanged():
    if(current[0] != previous[0] or current[1] != previous[1]):
        SynchronizeValues()
        return True
    else:
        return False

def SynchronizeValues():
    previous[0] = current[0]
    previous[1] = current[1]

def SendNotification(message):
    toast.show_toast(
        title,
        message,
        duration = 5,
        icon_path = None,
        threaded = True,
    )

def SendEmail(message):
    # Set the content of the email
    email.set_content(message)

    # Create a secure connection
    context = ssl.create_default_context()

    # Use smtp to send the email
    with smtplib.SMTP_SSL("smtp.gmail.com",465,context=context) as smtp:
        smtp.login(emailSender,emailPassword)
        smtp.sendmail(emailSender,emailReceiver,email.as_string())
        smtp.quit()

# Runs the script, then sleeps, then runs. Repeat infinite
while(True):
    RunWebScraper()
    time.sleep(sleepTime)