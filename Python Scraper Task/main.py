import os
from urllib.request import Request, urlopen
# import datetime
from urllib.parse import urlparse
import re
import html
import json

# from dataclasses import dataclass

session_data = []

dirname = os.path.dirname(__file__)
website_list_path = os.path.join(dirname, 'websites.txt')

def userChoice(message, response_type, range):
    """
    Asks user for an input

    :param str message: Message to appear on terminal
    :param str response_type: If the expected response is an int
    :param list range: The range of numbers if the expected response is an int
    :return: User's input
    """
    inputting = True
    while inputting:
        choice = input(message)
        if(response_type == "int"):
            try:
                choice = int(choice)
            except ValueError:
                print("Please input a number")
            else:
                if(isinstance(range, list)):
                    if(choice < range[0] or choice > range[1]):
                        print(f"Selection is out of range! Please select from {range[0]} to {range[1]}")
                        continue
                inputting = False
                return choice

        else:
            inputting = False
            return choice

def closeApp():
    """
    Gracefully exit the program
    """
    print(exit)
    exit()

# @dataclass
# class ScrapeResult:
#     url: str
#     website: str
#     status_code: int
#     size: int


class Menu:
    def __init__(self, spider):
        self.spider = spider

    
    def main(self):
        """
        Displays the main menu of the program, prompts the user for next menu or exit
        """
        print("Web Scraper")
        print("Where to next?")
        print()
        print("1. Website Scraper")
        print("2. Options")
        print("3. Exit")
        print()
        choice = userChoice("Select Menu (number): ", "int", [1, 3])
        if(choice == 1):
            self.website_selection()


    def website_selection(self):
        """
        Prompts the user with website selection while showing options from websites.txt
        """
        with open(website_list_path) as f:
            lines = f.read().splitlines()

        print("-1 Back to Main Menu")
        print("0  Choose your own URL")
        n = 0
        for line in lines:
            spaces = ""
            if(len(lines)>9 and n<9):
                spaces = " "
            n += 1
            print(str(n) + spaces + " 🌐 " + line)

        website_choice = userChoice("Choose which website to scrape (number): ", "int", [-1,len(lines)])

        if(website_choice == -1):
            self.main()
        else:
            if(website_choice == 0):
                url = userChoice("URL: ", None, None)
            else:
                url = lines[website_choice-1]

            attemptingResponse = True
            while(attemptingResponse):
                response_content = self.spider.crawl(url=url)

                # Change this to status codes!
                if(response_content["status_code"] is not None and 200 <= response_content["status_code"] <= 299):
                    attemptingResponse = False
                    self.pageActions(url=url, website_content=response_content["body"])
                else:
                    retryChoice = self.retry_subMenu()
                    if(retryChoice == 1): # Retry
                        continue
                    elif(retryChoice == 2): # Continue
                        attemptingResponse = False
                        self.pageActions(url=url, website_content=response_content["body"])
                    else:
                        attemptingResponse = False
                        self.main()


    def retry_subMenu(self):
        print("Do you want to retry?")
        print("1. Retry")
        print("2. Continue with errors")
        print("3. Back to Main Menu")
        choice = userChoice("Select how to proceed (number): ", "int", [1,3])
        return choice


    def pageActions(self, url, website_content):
        print("Page content downloaded, how do you want to proceed")
        print("1. Scrape and display info")
        print("2. Save content")
        print("3. Scrape and save")
        print("4. Do nothing")
        choice = userChoice("Choose an action (number): ", "int", [1,4])
        parser = Parser(url=url, website_content=website_content)
        if choice == 4:
            self.main()
        elif choice == 1:
            parser
        elif choice == 2:
            print("Attempting to save to file in working directory...")
            parser.save_content()
            self.main()
        else: # Scrape and save
            parser.save_content()
            parser.extract_content()
            self.main()


class Spider:
    def __init__(self):
        self.headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

    def crawl(self, url):
        """
        Crawls a specific URL

        :param self self: Class parameter for headers
        :param str url: The URL to be sent a GET request
        :return: Dict with keys: "body" - the response content, "status-code" the http status code 
        """
        crawling = True
        while crawling:
            print("Connecting... to: " + url)
            status_code = None
            try:
                # Send a request to a specific url with the Spider class's
                request = Request(url, headers=self.headers)
                website_request = urlopen(request)
                print("Connected!")

                status_code = website_request.getcode()
                
                print("Status Code: ", status_code)
            except Exception as e:
                print("Error occured during GET request:")
                print(e)
                return {
                    "body": "",
                    "status_code": status_code
                }
            else:
                # Decode the html binary data to a str and get a status code
                # Also attempt to fix cyrillic encoding
                raw_content = website_request.read()
                encoding = website_request.headers.get_content_charset() or "utf-8"
                try:
                    website_content = raw_content.decode(encoding)
                except UnicodeDecodeError:
                    website_content = raw_content.decode("windows-1251", errors="replace")

                return {
                    "body": website_content,
                    "status_code": status_code
                }


class Parser:
    def __init__(self, url, website_content):
        self.url = url
        self.website_content = website_content

    def save_content(self):
        try:
            domain = urlparse(self.url).netloc
            i = 0
            while os.path.exists(f"{domain}-{i}.index"):
                i += 1

            with open(f"{domain}-{i}.index", "w", encoding="utf-8") as f:
                f.write(self.website_content)
                

        except Exception as e:
            print("Failed writing to file:")
            print(e)
            return False
        else:
            return True

    def extract_content(self):
        domain = urlparse(self.url).netloc

        if(domain == "www.mobile.bg"):
            item_pattern = re.compile(
                r'<div class="item">\s*<a href="([^"]+)".*?'
                r'<img[^>]+src="[^"]+"[^>]*>\s*'
                r'<img[^>]+src="([^"]+)"[^>]+alt="Снимка [^"]*".*?'
                r'<div class="ime">(.*?)</div>\s*'
                r'<div class="cena[^"]*">(.*?)</div>\s*'
                r'<div class="km">\((.*?)\)</div>\s*'
                r'<div class="grad">\s*<span>(.*?)</span>',
                re.DOTALL
            )

            cars = []
            for match in item_pattern.finditer(self.website_content):
                link, img_src, name, price, km, location = match.groups()
                cars.append({
                    "link": html.unescape(link.strip()),
                    "image": html.unescape(img_src.strip()),
                    "name": html.unescape(name.strip()),
                    "price": html.unescape(price.strip()),
                    "kilometers": html.unescape(km.strip()),
                    "location": html.unescape(location.strip())
                })

            i = 0
            while os.path.exists(f"{domain}-featured_cars-{i}.json"):
                i += 1

            with open(f"{domain}-featured_cars-{i}.json", "w", encoding="utf-8") as f:
                json.dump(cars, f, ensure_ascii=False, indent=4)

            print(f"Successfully saved {len(cars)} featured cars data to '{output_file}'.")


def init():
    spider = Spider()
    menu = Menu(spider)

    menu.main()

init()