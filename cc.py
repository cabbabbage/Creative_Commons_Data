import csv
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import WebDriverException
from time import sleep
from tqdm import tqdm
import csv
from random import uniform
import os
from threading import Lock
class SearchResultsScraper:
    def __init__(self, file_path, cc_types,cat):
        self.file_path = file_path
        self.cc_types = cc_types
        self.cat = cat
        self.start_url = "https://www.google.com/search?as_q="
        self.modified_lines = self.replace_spaces_with_plus()
        self.total_results = 0
        self.cc_results = {cc: 0 for cc in cc_types}
        self.out_file = "./data_by_cat/" + str(cat) + "_data.csv"
        os.makedirs(os.path.dirname(self.out_file), exist_ok=True)
        self.path = ChromeDriverManager().install()
        self.scrape_search_results()

  

    def get_html_with_selenium(self, url, retry_count=0):
        options = Options()
        options.headless = True
        driver = webdriver.Chrome(service=Service(self.path), options=options)
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-gpu") 
        try:
            driver.get(url)
            return driver.page_source
        except WebDriverException as e:
            print(f"An error occurred while fetching {url}: {e}")
            if retry_count < 2: 
                print(f"Retrying... Attempt {retry_count + 1}")
                return self.get_html_with_selenium(url, retry_count + 1)
            else:
                print("Max retries reached. Moving on.")
        finally:
            driver.quit()
        return None

    def calculate_results(self, results_string):
        results_string = results_string.replace("(", "")
        parts = results_string.split()
        num_results = int(parts[1].replace(',', ''))
        print(parts[3])
        return num_results

    def get_results(self, html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        results = soup.find(id="result-stats")
        if results:
            return self.calculate_results(results.text)
        else:
            print('No results found')
            return 0

    def replace_spaces_with_plus(self):
        with open(self.file_path, 'r') as file:
            return [line.replace(" ", "+").strip() for line in file]

    def write(self, line, norm_url, cc_url, results, total_results):
        if total_results > 0:
            perc = (results / total_results) * 100
        else:
            perc = 0

        csv_data = [self.cat, norm_url, cc_url, line, results, total_results, perc]
        with open(self.out_file, 'a', newline='') as file:  # Open file in append mode
            writer = csv.writer(file)
            writer.writerow(csv_data)

    def do(self, url):
        got = False
        while not got:
            try:
                html_content = self.get_html_with_selenium(url)
                res = self.get_results(html_content)
                got = True
            except:
                print("fail")
        return res
    
    def search(self,line):
        full_url_norm = self.start_url + line
        full_url_cc = self.start_url + line + "&tbs=sur:fm"
        total  = self.do(self.start_url + line)
        total_cc = self.do(self.start_url + line + "&tbs=sur:fm")
        self.write(line, full_url_norm, full_url_cc, total_cc, total)



    def scrape_search_results(self):
        for line in tqdm(self.modified_lines, desc=f"Scraping {self.cat}"):
            success = False
            while not success:
                try:
                    self.search(line)
                    success = True
                except Exception as e:
                    print(f"An error occurred for line '{line}': {e}")



    def result(self):
        return "cat " + str(self.cat) + " has" + str(self.total_results) + " total, " + str(self.cc_results) + " cc results."
