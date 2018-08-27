import urllib.request
import urllib.parse
import re
from threading import Timer
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import copy

""" Creates a EbayWatcher that can check multiple different Ebay pages, it will email the recipient when a price 
change difference has been exceeded via gmail. As of August 2018 this works for the current website of Ebay. 
 By Brandon Blaschke 
 """


class EbayWatcher:

    def __init__(self, fromEmail, toEmail, emailPassword):
        self._links = {}
        self._loop = True
        self.emailFrom = fromEmail
        self.emailTo = toEmail
        self.emailPassword = emailPassword

    """ Get the price from the ebay page and return
     @return: float of price
     """
    @staticmethod
    def _getPrice(htmlString):
        match = re.search('US\s\$\d{1,10}.\d{0,2}', htmlString)
        priceString = match.group(0)
        return float(priceString[4:])

    """ Check if the auction has ended or not 
         @return: True if auction done or not 
         """
    @staticmethod
    def _ifEnded(htmlString):
        match = re.search('The listing you\'re looking for has ended', htmlString)
        if match is None:
            return False
        else:
            return True

    """ Sets the link's attribute to checked """
    def _setLinkToBeChecked(self, args):
        key = args
        val = self._links[key]
        val[0] = False
        self._links[key] = val

    """ Get a list of all the links in the watcher. @return: List of links being used"""
    def getLinks(self):
        return self._links.items()

    """ Get a copy of the dictionary being used. 
    The format of the values is like so [checkedInLoop, price, priceChangeDif, updateTimeSecs, auctionOver]
    @return: Copy of dictionary"""
    def getDictionary(self):
        return copy.deepcopy(self._links)

    """ Add a link to watch
    
    @param: htmlString The link to the ebay page 
    @param: priceChangeDif Difference in price for when to notify email recipient
    @param: updateTimeSecs How often to check the price of the item 
    """
    def addLinkToWatch(self, htmlString, priceChangeDif, updateTimeSecs):
        # [checked, price, priceChangeDif, updateTimeSecs, auctionOver]
        self._links[htmlString] = [False, -1, priceChangeDif, updateTimeSecs, False]

    """ Start the EbayWatcher """
    def start(self):
        threading.Thread(target=self._startHelper).start()

    """ Used for the multi threading to start another watcher """
    def _startHelper(self):
        # Loop for program
        self._loop = True
        while self._loop:

            # loop through all links to check price
            for key, val in self._links.items():
                # if not checked and auction not over
                if not val[0] and not val[4]:
                    link = key
                    with urllib.request.urlopen(link) as response:
                        html = response.read().decode('utf-8')
                    price = self._getPrice(html)
                    ended = self._ifEnded(html)
                    # print("Checking " + key + "\nprice: " + str(price) + " Ended: " + str(ended))

                    # Send email saying price dropped by set amount or it ended
                    if abs(self._links[key][1] - price) >= self._links[key][2] and self._links[key][1] != -1 or ended:
                        # Create Server
                        server = smtplib.SMTP('smtp.gmail.com', 587)
                        server.starttls()
                        server.login(self.emailFrom, self.emailPassword)

                        # Construct Message
                        message = MIMEMultipart()
                        message['From'] = self.emailFrom
                        message['To'] = self.emailTo
                        message['Subject'] = "Ebay Notification"

                        if ended:
                            body = key + "\nAuction for this item has ended"
                        else:
                            body = key + "\nItem went from $" + str(self._links[key][1]) + " to $" + str(price)

                        message.attach(MIMEText(body, "plain"))

                        text = message.as_string()
                        server.sendmail(self.emailFrom, self.emailTo, text)
                        # print("Sent email")
                        server.quit()

                        # print(key, "went from " + str(self._links[key][1]) + " to " + str(price))

                    if ended:
                        self._links[key] = [True, price, self._links[key][2], self._links[key][3], True]
                    else:
                        self._links[key] = [True, price, self._links[key][2], self._links[key][3], False]
                        t = Timer(self._links[key][3], self._setLinkToBeChecked, [key])
                        t.start()

    """ Ends the EbayWatcher """
    def end(self):
        print("end")
        self._loop = False

