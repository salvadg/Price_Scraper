import requests
from bs4 import BeautifulSoup
import time
import smtplib
from email.message import EmailMessage

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15"}
URLS = {
    "amazon": "https://www.amazon.com/Sony-Full-Frame-Mirrorless-Interchangeable-Lens-ILCE7M3/dp/B07B43WPVK/ref=sr_1_2?dchild=1&keywords=sony+a7iii&qid=1594262959&sr=8-2",
    "bestbuy": "https://www.bestbuy.com/site/sony-alpha-a7-iii-mirrorless-4k-video-camera-body-only/6213101.p?skuId=6213101",
    "adorama": "https://www.adorama.com/isoa7m3.html",
    "bh": "https://www.bhphotovideo.com/c/product/1394217-REG/sony_ilce_7m3_alpha_a7_iii_mirrorless.html",
    "ebay": "https://www.ebay.com/sch/i.html?_nkw=SONY+A7iii&LH_BIN=1&_sop=15&_udlo=1000&_udhi=1700"
}

EMAIL = "your_email@mail.com"
PASSWORD = "your_password"


def _bestbuy_scraper(url):
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    html = soup.find(
        "div", class_="priceView-hero-price priceView-customer-price").find("span")

    price = float(html.get_text()[1:].replace(",", ""))
    return price


def _bh_scraper(url):
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    html = soup.find("div", class_="price_1DPoToKrLP8uWvruGqgtaY")
    price = float(html.get_text()[1:].replace(",", ""))
    return price


def _adorama_scraper(url):
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    html = soup.find("div", class_="price-final").find("strong")
    price = float(html.get_text()[1:].replace(",", ""))
    return price


def _amazon_scraper(url):
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    html = soup.find("td", class_="a-span12").find("span")
    price = float(html.get_text()[1:].replace(",", ""))
    return price


def _ebay_scraper(url, desired_price):
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    result_count = soup.find(
        "div", class_="srp-controls__control srp-controls__count").find("span")

    if int(result_count.get_text()) == 0:
        return None

    htmls = soup.find_all("div", class_="s-item__info clearfix")
    prices = {}

    for html in htmls:
        link = html.find("a")['href']
        price = html.find(
            "span", class_="s-item__price")

        price = float(price.get_text()[1:].replace(",", ""))
        if price <= desired_price:
            prices[price] = link

    return prices


def _bh_used():
    url = "https://www.bhphotovideo.com/c/products/used-mirrorless-cameras/ci/21264/N/4040479538?filters=fct_brand_name%3Asony"
    response = requests.get(url, headers=HEADERS)
    time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')

    product_soup = soup.find_all(
        "h3", attrs={"data-selenium": "miniProductPageName"})

    for data in product_soup:
        if "a77 ii" in data.find("span").get_text().lower():
            return data.find("a", _class="title_ip0F69brFR7q991bIVYh1")['href']

    return None


def _extract_prices(ebay_price):
    ebay_url = f"https://www.ebay.com/sch/i.html?_nkw=SONY+A7iii&LH_BIN=1&_sop=15&_udlo=1000&_udhi={ebay_price}"
    URLS["ebay"] = ebay_url
    prices = {"bestbuy": None, "amazon": None,
              "adorama": None, "bh": None, "ebay": None}
    prices["bestbuy"] = _bestbuy_scraper(URLS["bestbuy"])
    prices["adorama"] = _adorama_scraper(URLS["adorama"])
    prices["bh"] = _bh_scraper(URLS["bh"])
    if ebay_price:  # If no ebay_price give then assume ebay results unwanted
        prices["ebay"] = _ebay_scraper(URLS["ebay"], ebay_price)
    # prices["amazon"] = _amazon_scraper(URLS["amazon"])

    return prices


def send_message(TO, desired_price, ebay_price=None):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    ## Replace EMAIL and PASSWORD with login credentials of sender email
    server.login(EMAIL, PASSWORD)

    Send = False
    product = "Sony a7iii"
    prices = _extract_prices(ebay_price)
    msg = EmailMessage()
    msg['Subject'] = f"{product} price drop!"
    msg['From'] = "Spotter"
    msg['To'] = TO

    if _bh_used():
        bh_msg = EmailMessage()
        bh_msg['Subject'] = f"{product} restocked!!"
        bh_msg['From'] = "Spotter"
        bh_msg['To'] = TO
        bh_msg.set_content("BH! has Restocked on used sony a7iii")
        server.send_message(bh_msg)

    ebay_msg = ""
    s = f"Great News! The {product} has dropped below your desired price!"
    for store, price in prices.items():
        if store == "ebay" and price:
            Send = True
            ebay_msg = "\n\nThe {} can be found below ${} at ebay:\n{}".format(
                product, ebay_price, URLS["ebay"])
        elif price and price <= desired_price:
            Send = True
            s += f"\n{store.upper()}\n{URLS[store]}"
        s += ebay_msg

    if Send:
        msg.set_content(s)
        server.send_message(msg)
        print("SENT EMAIL!!")

    server.quit()


def main():
    ## REPLACE recipient with recepient email address.
    recipient = "your_email@mail.com"
    desired_price = 1700
    ebay_price = 1499  # optional
    send_message(recipient, desired_price, ebay_price)


if __name__ == "__main__":
    main()
