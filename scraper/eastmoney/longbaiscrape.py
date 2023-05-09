from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import csv

good_pe = 10.0

base_url = "http://emweb.securities.eastmoney.com/PC_HSF10/NewFinanceAnalysis/Index?type=web&code="
good_stocks = []

urls_need_webscrape = []
with open('stock_basic_00.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        stock = row[0].replace('.', '').upper()
        urls_need_webscrape.append(base_url + stock)

# Set up the WebDriver
driver = webdriver.Chrome()

for url in urls_need_webscrape:
    try:
        # Navigate to the URL
        print (url)
        driver.get(url)

        # Wait for the "按年度" button to become clickable and click it
        wait = WebDriverWait(driver, 20)
        button = wait.until(EC.element_to_be_clickable((By.XPATH, "//*[@id=\"zyzbTab\"]/li[2]")))
        button.click()

        # Wait for the table to load
        table = wait.until(EC.presence_of_element_located((By.ID, "F10MainTargetDiv")))

        time.sleep(2)

        # Extract the page source using Beautiful Soup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        stock_price = float(soup.find('span', {'id': 'hq_2'}).text)

        profit_per_stock = 0
        # Find the table element
        table = soup.find('div', {'id': 'F10MainTargetDiv'}).find('table')
        # Extract the table data
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 0 and "基本每股收益" in cells[0].text: 
                profit_per_stock = float(cells[1].text)
        
        if (profit_per_stock > 0):
            pe = stock_price / profit_per_stock
            if pe < good_pe:
                good_stocks.append(url)
    except:
        print ("error: " + url)

# Close the WebDriver
driver.quit()

with open('output.txt', 'w') as f:
    for item in good_stocks:
        f.write(item + '\n')