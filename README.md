# Ebay Watcher
Sends a gmail notification whenever the price changes for an item or when auction ends

##  Use
Import web_crawler and create an EbayWatcher. Here the "from" and "to" email are the same which send an email to itself, password is entered for the "from" email. Then add a link to the watcher by calling the addLinkToWatch method, with a valid ebay link, price change difference, and how often in seconds to check the link. Then simply start the watcher by calling the start() method, and a email will be sent when the price changes by .5 cents or it ends. 

*Important that you set the gmail account that is being accessed to let access for less secure apps to be turned on

[Turn access on](https://myaccount.google.com/lesssecureapps)

## Example 
```
import web_crawler

ebayWatcher = web_crawler.EbayWatcher("someemail@gmail.com", "someemail@gmail.com", "password")
ebayWatcher.addLinkToWatch("ebay_link", .5, 10)

ebayWatcher.start()
```

