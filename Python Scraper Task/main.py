import os
from urllib.request import Request, urlopen
from urllib.parse import quote, urljoin, urlparse
import re
import html
import json

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
    while True:
        try:
            choice = input(message)
        except (EOFError, KeyboardInterrupt):
            print("\nInput stream closed. Exiting gracefully.")
            closeApp()

        if response_type == "int":
            try:
                choice = int(choice)
            except ValueError:
                print("Please input a number")
                continue

            if isinstance(range, list):
                if choice < range[0] or choice > range[1]:
                    print(f"Selection is out of range! Please select from {range[0]} to {range[1]}")
                    continue
            return choice

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
    for item_type in data_types:
        print(f"{item_type} x {data_types[item_type]}")
    raise SystemExit(0)

# @dataclass
# class ScrapeResult:
#     url: str
#     website: str
#     status_code: int
#     size: int


class Menu:
    def __init__(self, spider):
        self.spider = spider

    def print_scrape_summary(self, url, records, data_label, output_file=None):
        print("\nScraping completed successfully.")
        print(f"Website: {url}")
        print(f"Data scraped: {data_label}")
        print(f"Records collected: {len(records) if isinstance(records, list) else records}")
        if output_file:
            print(f"Data saved to: {output_file}")
        else:
            print("Data saved to: not available")

    def search_car(self):
        brand = userChoice("Enter car brand: ", None, None).strip()
        while not brand:
            print("Brand cannot be empty.")
            brand = userChoice("Enter car brand: ", None, None).strip()

        model = userChoice("Enter car model: ", None, None).strip()
        while not model:
            print("Model cannot be empty.")
            model = userChoice("Enter car model: ", None, None).strip()

        def make_slug(value):
            slug = re.sub(r"[\s_]+", "-", value.lower()).strip("-")
            slug = re.sub(r"-+", "-", slug)
            return quote(slug, safe="-")

        url = (
            "https://www.mobile.bg/obiavi/avtomobili-dzhipove/"
            f"{make_slug(brand)}/{make_slug(model)}"
        )
        return url

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
        if choice == 1:
            self.website_selection()
        elif choice == 2:
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
        try:
            with open(website_list_path, encoding="utf-8") as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            print("Website list not found. Please check the project directory.")
            self.main()
            return

        print("-1 Back to Main Menu")
        print("0  Choose your own URL")
        for index, line in enumerate(lines, start=1):
            print(f"{index}. {line}")

        website_choice = userChoice("Choose which website to scrape (number): ", "int", [-1, len(lines)])

        if(website_choice == -1):
            self.main()
            return

        if(website_choice == 0):
            url = userChoice("URL: ", None, None).strip()
        else:
            url = lines[website_choice - 1]

        if not url:
            print("URL cannot be empty.")
            self.main()
            return

        if urlparse(url).netloc.lower() in {"mobile.bg", "www.mobile.bg"}:
            print("Mobile.bg")
            print("1. Scrape this page (default featured cars)")
            print("2. Search by brand and model")
            mobile_choice = userChoice("Choose an option (number): ", "int", [1, 2])
            if mobile_choice == 2:
                url = self.search_car()

        attempting_response = True
        while attempting_response:
            response_content = self.spider.crawl(url=url)

            if response_content["status_code"] is not None and 200 <= response_content["status_code"] <= 299:
                attempting_response = False
                self.pageActions(url=url, website_content=response_content["body"])
            else:
                retry_choice = self.retry_subMenu()
                if retry_choice == 1:
                    continue
                elif retry_choice == 2:
                    attempting_response = False
                    self.pageActions(url=url, website_content=response_content["body"])
                else:
                    attempting_response = False
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
        choice = userChoice("Choose an action (number): ", "int", [1, 4])
        
        parser = Parser(url=url, website_content=website_content)

        if choice == 4:
            self.main()
            return

        try:
            if choice == 1:
                parser.save_content()
                extracted_data = parser.extract_content(isReturn=False)
                self.print_scrape_summary(url, extracted_data, "Parsed page data", parser.last_output_path)
            elif choice == 3:
                print("Attempting to save to file in working directory...")
                output_path = parser.save_content()
                self.print_scrape_summary(url, [], "HTML body", output_path)
            else: # Scrape and display
                extracted_data = parser.extract_content(isReturn=True)
                print("Here's the data collected from the website:")
                for item in extracted_data:
                    print(item)
                self.print_scrape_summary(url, extracted_data, "Parsed page data")
        except Exception as exc:
            print(f"Error while processing website data: {exc}")

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
                request = Request(url, headers=self.headers)
                website_request = urlopen(request, timeout=20)
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
        self.last_output_path = None

    def save_content(self):
        try:
            domain = urlparse(self.url).netloc
            i = 0
            file_name = f"{domain}-{i}.index"
            while os.path.exists(file_name):
                i += 1
                file_name = f"{domain}-{i}.index"

            saved_files_locations.append(file_name)
            self.last_output_path = os.path.join(dirname, file_name)
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(self.website_content)
        except Exception as e:
            print("Failed writing to file:")
            print(e)
            return None
        else:
            return self.last_output_path

    def save_json(self, filename, data):
        domain = urlparse(self.url).netloc
        i = 0
        output_file = f"{domain}-{filename}-{i}.json"
        while os.path.exists(output_file):
            i += 1
            output_file = f"{domain}-{filename}-{i}.json"

        saved_files_locations.append(output_file)
        self.last_output_path = os.path.join(dirname, output_file)
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        description = filename.replace("_", " ")
        print(f"Successfully saved {len(data)} {description} data to '{output_file}'.")
        return self.last_output_path

    def extract_content(self, isReturn):
        parsed_url = urlparse(self.url)
        domain = parsed_url.netloc.lower()

        if domain in {"www.mobile.bg", "mobile.bg"}:
            data_types["car"] = 0
            cars = []
            if not parsed_url.path.strip("/"):
                item_pattern = re.compile(
                    r'<div class="item">\s*<a href="([^"]+)".*?'
                    r'<img[^>]+src="[^"]+"[^>]*>\s*'
                    r'<img[^>]+src="([^"]+)"[^>]+alt="Снимка [^"]*".*?'
                    r'<div class="ime">(.*?)</div>\s*'
                    r'<div class="cena[^"]*">(.*?)</div>\s*'
                    r'<div class="km">\((.*?)\)</div>\s*'
                    r'<div class="grad">\s*<span>(.*?)</span>',
                    re.DOTALL | re.IGNORECASE,
                )
                for match in item_pattern.finditer(self.website_content):
                    link, image, name, price, kilometers, location = match.groups()
                    data_types["car"] += 1
                    cars.append({
                        "link": urljoin(self.url, html.unescape(link.strip())),
                        "image": urljoin(self.url, html.unescape(image.strip())),
                        "name": html.unescape(name.strip()),
                        "price": html.unescape(price.strip()),
                        "kilometers": html.unescape(kilometers.strip()),
                        "location": html.unescape(location.strip()),
                    })
            else:
                title_pattern = re.compile(
                    r'<a\s+href="([^"]+)"\s+class="title saveSlink"[^>]*>(.*?)</a>',
                    re.IGNORECASE | re.DOTALL,
                )
                title_matches = list(title_pattern.finditer(self.website_content))
                for index, title_match in enumerate(title_matches):
                    segment_end = (
                        title_matches[index + 1].start()
                        if index + 1 < len(title_matches)
                        else len(self.website_content)
                    )
                    listing_content = self.website_content[title_match.end():segment_end]
                    link, name = title_match.groups()
                    name = html.unescape(re.sub(r"<[^>]+>", " ", name))
                    name = re.sub(r"\s+", " ", name).strip()

                    price_match = re.search(
                        r'<div class="price[^"]*">\s*<div>(.*?)</div>',
                        listing_content,
                        re.IGNORECASE | re.DOTALL,
                    )
                    price = ""
                    if price_match:
                        price = html.unescape(
                            re.sub(r"<[^>]+>", " ", price_match.group(1))
                        )
                        price = re.sub(r"\s+", " ", price).strip()

                    params_match = re.search(
                        r'<div class="params">(.*?)</div>',
                        listing_content,
                        re.IGNORECASE | re.DOTALL,
                    )
                    parameters = ""
                    if params_match:
                        parameters = html.unescape(
                            re.sub(r"<[^>]+>", " ", params_match.group(1))
                        )
                        parameters = re.sub(r"\s+", " ", parameters).strip()

                    kilometers_match = re.search(
                        r"(\d[\d\s]*(?:[,.]\d+)?)\s*км\b",
                        parameters,
                        re.IGNORECASE,
                    )
                    kilometers = (
                        re.sub(r"\s+", " ", kilometers_match.group(1)).strip()
                        if kilometers_match
                        else ""
                    )

                    data_types["car"] += 1
                    cars.append({
                        "link": urljoin(self.url, html.unescape(link.strip())),
                        "name": name,
                        "price": price,
                        "kilometers": kilometers,
                        "parameters": parameters,
                    })

            if(isReturn):
                return cars

            self.save_json("featured_cars", cars)
            return cars

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
            return links

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
            return title

        if(domain == "soundmart.bg"):
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
            return store_info

        if(domain == "www.muziker.bg"):
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
            return muziker_info

        if(domain == "www.marica.bg"):
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
            return article_info

        if domain in ["www.plovdiv24.bg", "plovdiv24.bg"]:
            data_types["plovdiv24_info"] = 0
            plovdiv_info = []

            title_match = re.search(r'<title>(.*?)</title>', self.website_content, re.IGNORECASE | re.DOTALL)
            if title_match:
                page_title = html.unescape(re.sub(r'\s+', ' ', title_match.group(1)).strip())
                data_types["plovdiv24_info"] += 1
                plovdiv_info.append(f"Title: {page_title}")

            description_match = re.search(r'<meta[^>]+name="description"[^>]+content="([^"]+)"', self.website_content, re.IGNORECASE | re.DOTALL)
            if description_match:
                description = html.unescape(re.sub(r'\s+', ' ', description_match.group(1)).strip())
                if description:
                    data_types["plovdiv24_info"] += 1
                    plovdiv_info.append(f"Description: {description}")

            lead_match = re.search(
                r'<h2[^>]*class="[^"]*lead-title[^"]*"[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                self.website_content,
                re.IGNORECASE | re.DOTALL,
            )
            if lead_match:
                lead_url, lead_title = lead_match.groups()
                cleaned_title = html.unescape(re.sub(r'<[^>]+>', ' ', lead_title))
                cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
                if cleaned_title:
                    data_types["plovdiv24_info"] += 2
                    plovdiv_info.append(f"Top story: {cleaned_title}")
                    plovdiv_info.append(f"Top story link: {lead_url}")

            headline_matches = re.findall(
                r'<h2[^>]*>\s*<a[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
                self.website_content,
                re.IGNORECASE | re.DOTALL,
            )
            if headline_matches:
                headlines = []
                lead_title_text = None
                if lead_match:
                    lead_title_text = html.unescape(re.sub(r'<[^>]+>', ' ', lead_match.group(2)))
                    lead_title_text = re.sub(r'\s+', ' ', lead_title_text).strip()

                for url, title in headline_matches[:5]:
                    cleaned_title = html.unescape(re.sub(r'<[^>]+>', ' ', title))
                    cleaned_title = re.sub(r'\s+', ' ', cleaned_title).strip()
                    if cleaned_title and cleaned_title != lead_title_text and cleaned_title not in headlines:
                        headlines.append(cleaned_title)

                if headlines:
                    data_types["plovdiv24_info"] += len(headlines)
                    plovdiv_info.append("Latest headlines:")
                    for headline in headlines:
                        plovdiv_info.append(f"- {headline}")

            if not plovdiv_info:
                plovdiv_info.append("No structured information found on the Plovdiv24 homepage.")

            if isReturn:
                return plovdiv_info

            self.save_json("plovdiv24_info", plovdiv_info)
            return plovdiv_info

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

            if isReturn:
                return wikipedia_info

            self.save_json("interesting_info", wikipedia_info)
            return wikipedia_info

        return []



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