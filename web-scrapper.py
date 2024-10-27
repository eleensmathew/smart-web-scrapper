from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import time
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer  
stop_words = stopwords.words('english')
sw = stopwords.words('english')
lemmatizer = WordNetLemmatizer()
import re 
import requests
import os

def web_scrape_author():
    urls = [
        'https://arxiv.org/list/econ.GN/recent',
        #'https://medium.com/@tim-lou', 
            ]

    for url in urls:
        
        driver = webdriver.Chrome()
        driver.get(url)
        print(driver.title)
        anchors = driver.find_elements(By.TAG_NAME, 'a')
        username = url.split('@')[-1]
        all_links= []
        try:
            for anchor in anchors:
                href = anchor.get_attribute('href')
                check_url = "https://arxiv.org/html/2"
                if href and check_url in href:
                    print(href)
                    all_links.append(href)
            
            driver.quit()
        except:
            pass

    with open('medium_links.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Links'])
        for link in all_links:
            writer.writerow([link])

def web_scrape_links(url):
    driver = webdriver.Chrome()
    driver.get(url)
    time.sleep(3)    
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        headings = driver.find_elements(By.TAG_NAME, 'h1') + driver.find_elements(By.TAG_NAME, 'h2') + driver.find_elements(By.TAG_NAME, 'h3')  # Extract all <h1>, <h2>, and <h3> tags
        paragraphs = driver.find_elements(By.TAG_NAME, 'p') 
        all_content = []
        for heading in headings:
            all_content.append(heading.text)
        for paragraph in paragraphs:
            all_content.append(paragraph.text)

        with open('medium_content_new.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            final_content = ""
            for content in all_content:
                if('Written' in content or 'Sign' in content or len(content.split()) == 1):
                    #print(content)
                    continue
                final_content+=content+" "
            cleaned_text = clean_text(final_content)
            writer.writerow([cleaned_text])
            print('completed')
        driver.quit()
    except Exception as e:
        print(f"An error occurred: {e}")


    driver.quit()

def add_topic(row, topic):
    df = pd.read_csv('medium_content.csv')
    if 'newcol' not in df.columns:
        df['newcol'] = ""
    df.at[row, 'newcol'] = topic
    df.to_csv('medium_content.csv', index=False)

def clean_text(text):
    from nltk import pos_tag
    text = text.lower()
    text = re.sub(r"remove html conversions sometimes display errors due to content that did not convert correctly from the source\. this paper uses the following packages that are not yet supported by the html conversion tool\. feedback on these issues are not necessary; they are known and are being worked on\.\s*failed: centernot\s*authors: achieve the best html results from your latex submissions by following these best practices\.", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[^a-zA-Z?.!,¿]+", " ", text)
    text = re.sub(r"http\S+", "",text) 
    html=re.compile(r'<.*?>') 
    text = html.sub(r'',text)
    punctuations = '@#!?+&*[]-%.:/();$=><|{}^' + "'`" + '_'
    for p in punctuations:
        text = text.replace(p,'') 
    text = [word.lower() for word in text.split() if word.lower() not in sw and len(word) > 1 and not word.startswith('/')]
    text = [lemmatizer.lemmatize(word) for word in text]
    text = " ".join(text)
    text = re.sub(r"reporting error experimental html improve accessibility invite report rendering error learn project help improve conversion", "", text, flags=re.IGNORECASE)
    text = re.sub(r"experimental html improve accessibility invite report rendering error learn project help improve conversion html conversion sometimes display error due content convert correctly source paper us following package yet supported html conversion tool feedback issue necessary known worked author achieve best html result latex submission following best practice", "", text, flags=re.IGNORECASE)
    text = re.sub(r"continuing improve html version papers, feedback help enhance accessibility mobile support report error html help improve conversion rendering, choose method listed team already identified following issue appreciate time reviewing reporting rendering error may found yet effort help improve html version readers, disability barrier accessing research thank continued support championing open access free development cycle help support accessibility arxiv collaborator latexml maintain list package need conversion, welcome developer contribution", "", text, flags=re.IGNORECASE)
    text = re.sub(r"experimental html improve accessibility invite report rendering error learn project help improve conversion", "", text, flags=re.IGNORECASE)
    text = re.sub(r"improve html version papers, feedback help enhance accessibility mobile support report error html help u improve conversion rendering, choose method listed team already identified following issue appreciate time reviewing reporting rendering error may found yet effort help u improve html version readers, disability barrier accessing research thank continued support championing open access free development cycle help support accessibility arxiv collaborator latexml maintain list package need conversion, welcome developer contribution", "", text, flags=re.IGNORECASE)
    return text

def delete_row_by_number(row_number):
    df = pd.read_csv('medium_content.csv')
    df = df.drop(index=row_number)
    df.to_csv('medium_content.csv', index=False)


def clean_csv_row(row_index):
    
    filename = 'medium_content.csv'
    df = pd.read_csv(filename)
    if row_index >= len(df):
        raise IndexError("out of range")
    df.at[row_index, 'content'] = clean_text(df.at[row_index, 'content'])
    df.to_csv(filename, index=False)
    print("cleaned")

def scrape_all_links_from_csv(csv_filename):
    with open(csv_filename, mode='r') as file:
        reader = csv.reader(file)
        next(reader)
        urls = [row[0] for row in reader]
    with open('medium_content_new.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['content'])
            print('wrote')
    for url in urls:
        web_scrape_links(url)

#web_scrape_links('https://arxiv.org/html/2410.15439v1')
#add_topic(50, 'general economics')
web_scrape_author()
scrape_all_links_from_csv('medium_links.csv')

#url rotation api
# payload = { 'api_key': '25f0173438a83f6ec7ec454632f8c5c0', 'url': 'https://arxiv.org/' }
# r = requests.get('https://arxiv.org/html/2410.18145v1', params=payload)
#print(r.text)