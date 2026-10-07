import os
from urllib.request import Request, urlopen
dirname = os.path.dirname(__file__)
website_list_path = os.path.join(dirname, 'websites.txt')

def userChoice(message, response_type, range):
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
    print(exit)
    exit()

class Menu:
    def __init__(self, spider):
        self.spider = spider
        
    def main(self):
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
        with open(website_list_path) as f:
            lines = f.read().splitlines()

        print("0 🌐 Choose your own URL")
        n = 0
        for line in lines:
            spaces = ""
            if(len(lines)>9 and n<9):
                spaces = " "
            n += 1
            print(str(n) + spaces + " 🌐 " + line)

        website_choice = userChoice("Choose which website to scrape (number): ", "int", [0,len(lines)])

        url = lines[website_choice-1]

        website_content = self.spider.crawl(url=url)

        if(website_content == "unsuccessfull"):
            self.retryMenu()

        print(website_content)

    def retryMenu():
        print("Do you want to retry?")
        print("1. Retry")
        print("2. Continue")
        print("3. Back to Main Menu")
        choice = userChoice("Select how to proceed (number): ", "int", [1,3])

class Spider:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36 Edg/154.0.0.0'}
        pass

    def crawl(self, url):
        req = Request(
            url, 
            headers=self.headers
        )

        crawling = True
        while crawling:
            print("Connecting to: " + url)
            try:
                website_request = urlopen(req)
                print("Connected!")
                website_content = website_request.read().decode("utf-8")
            except Exception as e:
                print("Error occured during GET request:")
                print(e)
                return "unsuccessfull"
            else:
                print("five black dudes")
                return website_content



def init():
    spider = Spider()
    menu = Menu(spider)

    menu.main()

    # website_content = spider.crawl(url=url)


    # with open("index.html", "w") as f:
    #     f.write(website_content)


    # print(website_content)

init()