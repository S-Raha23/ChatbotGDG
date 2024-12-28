from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup
import requests
import sys
import cloudscraper
import os
sys.stdout.reconfigure(encoding='utf-8')
import json
import re
def sanitize_name(name):
    name = re.sub(r'[<>$:"/\\|?*]', '_', name)
    name = re.sub(r'\.{2,}', '.', name)
    return name.strip('.')

PATH = r"C:\Program Files (x86)\chromedriver-win64\chromedriver.exe"

# Set up ChromeDriver service
service = Service(PATH)

# Initialize the WebDriver
driver = webdriver.Chrome(service=service)
scraper = cloudscraper.create_scraper()  # Automatically bypass Cloudflare
url = "https://codeforces.com/contests?complete=true"
response = scraper.get(url)

html_text = response.text
soup = BeautifulSoup(html_text, 'lxml')

contestTables = soup.find_all('div', class_='datatable')

prev = contestTables[1]

tr_tag = prev.find_all('tr', {'data-contestid': True})

CP_folder = os.path.join(os.getcwd(), "CP Resources")
os.makedirs(CP_folder, exist_ok=True)

for i in tr_tag[1:]:

    if i:
        # Extract the value of the 'data-contestid' attribute
        contest_id = i.get('data-contestid')
        first = i.find('td')
        title_text = first.contents[0].strip()
        clean_title_text=sanitize_name(title_text)
        print(title_text)

        # Create a folder named after the contest title
        contest_folder = os.path.join(CP_folder, clean_title_text)
        os.makedirs(contest_folder, exist_ok=True)

        contest_url = "https://codeforces.com/contest/" + contest_id
        r = scraper.get(contest_url)

        # Get the page source of the contest page
        contest_html_text = r.text
        soup1 = BeautifulSoup(contest_html_text, 'lxml')

        # Find the problems table
        problem_table = soup1.find('table', class_='problems')
        problems = problem_table.find_all('tr')
        problem_No=0
        for problem in problems[1:]:
            parts = problem.find_all('td')
            problem_letter = parts[0].a.text.strip()
            print(problem_letter)
            problem_name = parts[1].a.get_text()
            problem_url = contest_url + "/problem/" + problem_letter
            #print(problem_url)
            print(problem_name)
            clean_problem_name=sanitize_name(problem_name)
            # Create a folder for the problem
            problem_folder = os.path.join(contest_folder, clean_problem_name)
            os.makedirs(problem_folder, exist_ok=True)

            # Fetch the problem page
            r2 = scraper.get(problem_url)
            problem_html_text = r2.text
            soup2 = BeautifulSoup(problem_html_text, 'lxml')
            
            whole = soup2.find('div', 'problem-statement')
            if whole:
                header=whole.find('div',class_='header')
                title=header.find('div',class_='title').get_text()
                timee_limit=header.find('div',class_='time-limit').get_text()
                memory_limit=header.find('div',class_='memory-limit').get_text()
                data={
                    "title":title,
                    "time-limit": timee_limit,
                    "memory-limit":memory_limit
                }
                 
                statement = whole.find_all('div')
                info = statement[10].text
                InputStatement=statement[11].get_text()
                OutputStatement=statement[13].get_text()
                # Write the problem info to a text file
                problem_file_path = os.path.join(problem_folder, 'info.txt')
                if problem_file_path:
                    with open(problem_file_path, 'w', encoding='utf-8') as f:
                        f.write(sanitize_name(info))
                        f.write("\n \n")
                        f.write(sanitize_name(InputStatement))
                        f.write("\n \n")
                        f.write(sanitize_name(OutputStatement))
            sidebar=soup2.find('div',id='sidebar')
            editorial=sidebar.find_all('li')[-1]
            editorial_URL="https://codeforces.com"+editorial.a.get('href')
            r3 = scraper.get(editorial_URL)
            editorial_html_text = r3.text
            soup3 = BeautifulSoup(editorial_html_text, 'lxml')
            spoiler_divs_all = soup3.find_all("div", class_="spoiler-content")
            length=len(spoiler_divs_all)
            if (spoiler_divs_all!=None):
                if(problem_No*2+1>length-1):
                    continue
                spoiler_divs=spoiler_divs_all[problem_No*2+1].code.get_text(strip=True)
                solution_file_path = os.path.join(problem_folder, 'solution.txt')
                if solution_file_path:
                    with open(solution_file_path, 'w', encoding='utf-8') as f:
                        f.write(spoiler_divs)
                problem_No=problem_No+1
            tag_name=sidebar.find_all('span',class_='tag-box')
            tags=[]
            for tag in tag_name:
                t=tag.get_text().strip()
                tags.append(t)

            all_data={
                "problem_info":data,
                "tags":tags
            }
            fileName= os.path.join(problem_folder, "problem_data.json")
            with open(fileName, "w") as json_file:
                json.dump(all_data, json_file, indent=4)
            
    
            
   
            
    
            
    

