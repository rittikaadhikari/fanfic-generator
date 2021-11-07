import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlencode, parse_qsl

class Scraper:
    """
    A class which scrapes fanfiction of a particular fandom into a 
    folder of .txt files.
    """
    def __init__(self, fandom_type, fandom, num_fanfics, out_dir):
        self.fandom_type = fandom_type
        self.fandom = fandom
        self.num_fanfics = num_fanfics
        self.out_dir = out_dir
        self.parser = "html.parser"

        self.base_url = "https://archiveofourown.org/"
        fandom_type_url = self.get_fandom_type_url()
        self.fandom_url = self.get_fandom_url(fandom_type_url)

    def get_fandom_type_url(self):
        """
        Returns url with a particular type of work (i.e., Books or Movies, etc.)
        """
        base_page = requests.get(self.base_url)
        soup = BeautifulSoup(base_page.content, self.parser)
        elements = soup.find("div", class_="browse module").find_all("a", href=True)
        
        for elem in elements:
            if self.fandom_type.lower() in elem.text.lower():
                return urljoin(self.base_url, elem.get("href"))
        
        raise Exception(f"Fandom type {self.fandom_type} not found.")

    def get_fandom_url(self, fandom_type_url):
        """
        Returns url with works in a particular fandom (i.e., Harry Potter, PJO, etc.)
        """
        fandom_type_page = requests.get(fandom_type_url)
        soup = BeautifulSoup(fandom_type_page.content, self.parser)
        elements = soup.find("ol", class_="alphabet fandom index group").find_all("a", href=True)
        
        for elem in elements:
            if self.fandom.lower() in elem.text.lower():
                return urljoin(fandom_type_url, elem["href"])
        
        raise Exception(f"Fandom name {self.fandom} not found.")

    def add_content_filters(self, page=1):
        """
        Adds filters to filter out any inappropriate content.

        Parameters:
        page (int): webpage number (DEFAULT = 1) 

        Returns: 
        str: webpage url with content filters
        """
        query = [('commit', 'Sort and Filter'), 
                 ('exclude_work_search[rating_ids][]', '11'), 
                 ('exclude_work_search[rating_ids][]', '12'), 
                 ('exclude_work_search[rating_ids][]', '13'), 
                 ('exclude_work_search[rating_ids][]', '9'),
                 ('exclude_work_search[archive_warning_ids][]', '14'),
                 ('exclude_work_search[archive_warning_ids][]', '17'),
                 ('exclude_work_search[archive_warning_ids][]', '20'),
                 ('exclude_work_search[archive_warning_ids][]', '19'),
                 ('work_search[sort_column]', 'hits'),
                 ('work_search[language_id]', 'en')]
        query.append(('page', str(page)))
        fandom_page_url = self.fandom_url + "?" + urlencode(query)
        return fandom_page_url

    def get_fanfic_urls(self):
        """
        Returns all valid fanfiction work urls.
        """
        fanfic_urls = []
        page_num = 1
        while len(fanfic_urls) < self.num_fanfics:
            fanfics_page_url = self.add_content_filters(page_num)
            fanfics_page = requests.get(fanfics_page_url)
            soup = BeautifulSoup(fanfics_page.content, "html.parser")
            elems = soup.find("ol", class_="work index group").find_all("li", id=lambda x: x and x.startswith("work_"))
            for elem in elems:
                href = elem.find("a", href=True).get("href")
                fanfic_url = urljoin(self.base_url, href)
                fanfic_urls.append(fanfic_url)
            page_num += 1 

        return fanfic_urls

    def get_fanfic(self, url):
        """
        Returns one fanfiction work's text, given a url.
        """
        fanfic_page = requests.get(url)
        soup = BeautifulSoup(fanfic_page.content, "html.parser")
        title = soup.find("h2", class_="title heading").text.strip()
        elems = soup.find("div", class_="userstuff module")
        if elems == None:
            elems = soup.find("div", class_="userstuff")
        return title, elems.text
    
    def save_scraped_fanfics(self):
        """
        Save all fanfictions in .txt files.
        """
        if not os.path.exists(self.out_dir):
            os.makedirs(self.out_dir)

        fanfic_urls = self.get_fanfic_urls()
        for fanfic_url in fanfic_urls:
            title, text = self.get_fanfic(fanfic_url)
            with open(os.path.join(self.out_dir, f"{title}.txt"), "w") as file:
                file.write(text)

####################### EXAMPLE RUN ######################    
# scraper = Scraper("books", "harry potter", 1, "fanfics")
# scraper.save_scraped_fanfics()
######################### END RUN ########################