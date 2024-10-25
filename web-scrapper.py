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

def web_scrape_author():
    urls = [
        'https://medium.com/@dipanshu10',
        #'https://medium.com/@tim-lou', 
            ]

    for url in urls:
        
        driver = webdriver.Chrome()
        driver.get(url)
        print(driver.title)
        anchors = driver.find_elements(By.TAG_NAME, 'a')
        medium_links = set()
        username = url.split('@')[-1]
        try:
            for anchor in anchors:
                href = anchor.get_attribute('href')
                check_url = 'https://'+username+'.medium.com/'
                not_check_url = check_url+'?'
                if href and check_url in href:
                        if(not_check_url not in href and 'followers?' not in href and 'about?' not in href and '@' not in href):
                            medium_links.add(href)

            for link in medium_links:
                print(link)
            driver.quit()
        except:
            pass

    with open('medium_links.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Links'])
        for link in medium_links:
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
        # for content in all_content:
        #     print(content)
        i=1
        with open('medium_content.csv', mode='a', newline='') as file:
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
    return text

def delete_row_by_number(row_number):
    df = pd.read_csv('medium_content.csv')
    df = df.drop(index=row_number)
    df.to_csv('medium_content.csv', index=False)

web_scrape_links('https://arxiv.org/html/2410.15165v1')
add_topic(28, 'biomolecules')

''' remove HTML conversions sometimes display errors due to content that did not convert correctly from the source. This paper uses the following packages that are not yet supported by the HTML conversion tool. Feedback on these issues are not necessary; they are known and are being worked on.

failed: centernot
Authors: achieve the best HTML results from your LaTeX submissions by following these best practices.'''
#remove words begining with /
