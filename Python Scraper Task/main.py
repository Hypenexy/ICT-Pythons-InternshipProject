import os
from urllib.request import Request, urlopen
# import datetime
from urllib.parse import urlparse
import re
import html
import json

# from dataclasses import dataclass

scraped_sites = []
saved_files_locations = []
data_types = {}

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

    print("---=*= Session summary =*=---")
    print("Site URLs that have been scraped:")
    for site in scraped_sites:
        print(site)


    print("Saved files' locations:")
    for location in saved_files_locations:
        print(os.path.join(dirname, location))


    print("Data Types collected and the number of records:")
    for type in data_types:
        print(f"{type} x {data_types[type]}")
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
        elif(choice == 2):
            self.options()
        else:
            closeApp()


    def options(self):
        """View and change the User-Agent used for requests."""
        while True:
            print("Options")
            print(f"Current User-Agent: {self.spider.headers['User-Agent']}")
            print("1. Change User-Agent")
            print("2. Restore default User-Agent")
            print("3. Back to Main Menu")
            choice = userChoice("Select an option (number): ", "int", [1, 3])

            if choice == 1:
                user_agent = userChoice("Enter User-Agent: ", None, None).strip()
                if user_agent:
                    self.spider.headers["User-Agent"] = user_agent
                else:
                    print("User-Agent cannot be empty.")
            elif choice == 2:
                self.spider.headers["User-Agent"] = self.spider.default_user_agent
            else:
                self.main()
                return


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
        scraped_sites.append(url)
        print("Page content downloaded, how do you want to proceed")
        print("1. Scrape and save parsed data and HTML")
        print("2. Scrape and display parsed info")
        print("3. Save HTML body")
        print("4. Do nothing")
        choice = userChoice("Choose an action (number): ", "int", [1,4])
        parser = Parser(url=url, website_content=website_content)
        if choice == 4:
            self.main()
        elif choice == 1:
            parser.save_content()
            parser.extract_content(isReturn=False)
            self.main()
        elif choice == 3:
            print("Attempting to save to file in working directory...")
            parser.save_content()
            self.main()
        else: # Scrape and display
            list = parser.extract_content(isReturn=True)
            print("Here's the data collected from the website:")
            for item in list:
                print(item)
            self.main()


class Spider:
    def __init__(self):
        self.default_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        self.headers = {"User-Agent": self.default_user_agent}

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

            saved_files_locations.append(f"{domain}-{i}.index")
            with open(f"{domain}-{i}.index", "w", encoding="utf-8") as f:
                f.write(self.website_content)
                

        except Exception as e:
            print("Failed writing to file:")
            print(e)
            return False
        else:
            return True

    def save_json(self, filename, data):
        domain = urlparse(self.url).netloc
        i = 0
        output_file = f"{domain}-{filename}-{i}.json"
        while os.path.exists(output_file):
            i += 1
            output_file = f"{domain}-{filename}-{i}.json"

        saved_files_locations.append(output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        description = filename.replace("_", " ")
        print(f"Successfully saved {len(data)} {description} data to '{output_file}'.")

    def extract_content(self, isReturn):
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

            data_types["car"] = 0
            cars = []
            for match in item_pattern.finditer(self.website_content):
                data_types["car"] += 1
                link, img_src, name, price, km, location = match.groups()
                cars.append({
                    "link": html.unescape(link.strip()),
                    "image": html.unescape(img_src.strip()),
                    "name": html.unescape(name.strip()),
                    "price": html.unescape(price.strip()),
                    "kilometers": html.unescape(km.strip()),
                    "location": html.unescape(location.strip())
                })
            

            if(isReturn):
                return cars

            featured_cars = "featured_cars"
            self.save_json(featured_cars, cars)

        if(domain == "murlev.com"):
            data_types["link"] = 0
            links = []

            a_tags_pattern = re.compile(r'(<a\b[^>]*>.*?</a>)', re.DOTALL | re.IGNORECASE)
            extracted_links = a_tags_pattern.findall(self.website_content)
            for idx, tag in enumerate(extracted_links, 1):
                data_types["link"] += 1
                links.append(f"[{idx}] {tag}")
            
            if(isReturn):
                return links
            
            self.save_json("links", links)

        if(domain == "midelight.net"):
            data_types["title"] = 0
            title = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                data_types["title"] += 1
                page_title = html.unescape(title_match.group(1).strip())
                title.append(page_title)

            if(isReturn):
                return title
            
            self.save_json("title", title)

        if(domain in ["soundmart.bg"]):
            data_types["store_info"] = 0
            store_info = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = html.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip())
                data_types["store_info"] += 1
                store_info.append(f"Title: {page_title}")

            description_match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if description_match:
                description = html.unescape(re.sub(r'\s+', ' ', description_match.group(1)).strip())
                if description:
                    data_types["store_info"] += 1
                    store_info.append(f"Description: {description}")

            jsonld_match = re.search(r'<script[^>]+type="application/ld\+json"[^>]*>(.*?)</script>', self.website_content, re.IGNORECASE | re.DOTALL)
            if jsonld_match:
                jsonld_text = jsonld_match.group(1)
                org_name_match = re.search(r'"name":"([^"]+)"', jsonld_text)
                if org_name_match:
                    org_name = html.unescape(org_name_match.group(1))
                    data_types["store_info"] += 1
                    store_info.append(f"Organization: {org_name}")

            if not store_info:
                store_info.append("No structured information found on the Soundmart homepage.")

            if(isReturn):
                return store_info

            self.save_json("store_info", store_info)

        if(domain in ["www.muziker.bg"]):
            data_types["muziker_info"] = 0
            muziker_info = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = html.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip())
                data_types["muziker_info"] += 1
                muziker_info.append(f"Title: {page_title}")

            meta_description = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if meta_description:
                description = html.unescape(re.sub(r'\s+', ' ', meta_description.group(1)).strip())
                if description:
                    data_types["muziker_info"] += 1
                    muziker_info.append(f"Description: {description}")

            languages = re.findall(r'<link[^>]+hreflang="[^"]+"[^>]+href="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if languages:
                preview = languages[:5]
                data_types["muziker_info"] += 1
                muziker_info.append(f"Regional sites: {', '.join(preview)}")

            if not muziker_info:
                muziker_info.append("No structured information found on the Muziker homepage.")

            if(isReturn):
                return muziker_info

            self.save_json("muziker_info", muziker_info)

        if(domain in ["www.marica.bg"]):
            data_types["article_info"] = 0
            article_info = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = html.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip())
                data_types["article_info"] += 1
                article_info.append(f"Title: {page_title}")

            description_match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if description_match:
                description = html.unescape(re.sub(r'\s+', ' ', description_match.group(1)).strip())
                if description:
                    data_types["article_info"] += 1
                    article_info.append(f"Description: {description}")

            paragraphs = []
            for paragraph in re.findall(r'<p[^>]*>(.*?)</p>', self.website_content, re.IGNORECASE | re.DOTALL):
                cleaned = re.sub(r'<[^>]+>', ' ', paragraph)
                cleaned = html.unescape(re.sub(r'\s+', ' ', cleaned).strip())
                if cleaned:
                    paragraphs.append(cleaned)

            if paragraphs:
                lead = paragraphs[0]
                data_types["article_info"] += 1
                article_info.append(f"Lead paragraph: {lead[:400]}")

            image_matches = re.findall(r'<img[^>]+src="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if image_matches:
                data_types["article_info"] += 1
                article_info.append(f"Featured image: {image_matches[0]}")

            if not article_info:
                article_info.append("No structured information found on the Marica article page.")

            if(isReturn):
                return article_info

            self.save_json("article_info", article_info)

        if(domain == "wikipedia.org"):
            data_types["wikipedia_info"] = 0
            wikipedia_info = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = html.unescape(title_match.group(1).strip())
                data_types["wikipedia_info"] += 1
                wikipedia_info.append(f"Title: {page_title}")

            slogan_match = re.search(
                r'<strong[^>]*class="[^"]*localized-slogan[^"]*"[^>]*>(.*?)</strong>',
                self.website_content,
                re.IGNORECASE | re.DOTALL,
            )
            if slogan_match:
                slogan = re.sub(r'<[^>]+>', '', slogan_match.group(1))
                slogan = html.unescape(slogan.strip())
                if slogan:
                    data_types["wikipedia_info"] += 1
                    wikipedia_info.append(f"Slogan: {slogan}")

            featured_langs = re.findall(
                r'<div\s+class="central-featured-lang[^"]*"\s+lang="([^"]+)"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*title="([^"]+)"[^>]*data-slogan="([^"]+)"',
                self.website_content,
                re.IGNORECASE | re.DOTALL,
            )
            if featured_langs:
                wikipedia_info.append("Featured language links:")
                for language, href, title, slogan in featured_langs[:5]:
                    normalized_link = href
                    if normalized_link.startswith("//"):
                        normalized_link = "https:" + normalized_link
                    data_types["wikipedia_info"] += 1
                    wikipedia_info.append(f"- {language.upper()}: {html.unescape(title)} ({html.unescape(slogan)}) -> {normalized_link}")

            if not wikipedia_info:
                wikipedia_info.append("No structured information found on the Wikipedia homepage.")

            if(isReturn):
                return wikipedia_info

            self.save_json("interesting_info", wikipedia_info)



def init():
    spider = Spider()
    menu = Menu(spider)

    try:
        menu.main()
    except KeyboardInterrupt:
        print()
        closeApp()

if __name__ == "__main__":
    init()