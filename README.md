# Price Scraper Purpose
Periodically scrapes the price of the given Camera (Sony a7iii) from several retail sites using BeautifulSoup to parse HTML. 
When the retail price drops below a given desired price then an email is sent. 

#### Additional Info 
I utilize a cron job to schedule run the the script periodically

### Future Plans
As it currently stands the code is limited to a specific camera and a few retail sites and it is barebones. But I hope to implement a feature to simply input any camera model/name and desired price and begin tracking.

### LIBRARIES USED
- smtplib
- Beautiful Soup (BS4)
- time



