import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk
import os


# Initialize WebDriver for the specified browser
def init_driver(browser):
    if browser == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        driver = webdriver.Chrome(service=ChromeService(), options=options)
    elif browser == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(service=FirefoxService(), options=options)
    elif browser == "edge":
        options = webdriver.EdgeOptions()
        options.add_argument('--headless')
        driver = webdriver.Edge(service=EdgeService(), options=options)
    else:
        raise ValueError("Unsupported browser")
    return driver


# Perform Google search using Dorks
def google_search(query, driver):
    driver.get('https://www.google.com')
    search_box = driver.find_element(By.NAME, 'q')
    search_box.send_keys(query)
    search_box.submit()
    body = driver.find_element(By.TAG_NAME, 'body')
    return body.get_attribute('innerHTML')


# Parse search results
def parse_results(page_source):
    soup = BeautifulSoup(page_source, 'html.parser')
    results = []
    for g in soup.find_all('div', class_='g'):
        anchors = g.find_all('a')
        if anchors:
            link = anchors[0]['href']
            title = g.find('h3').text if g.find('h3') else 'No title'
            snippet = g.find('span', class_='aCOpRe').text if g.find('span', class_='aCOpRe') else 'No snippet'
            results.append({'title': title, 'link': link, 'snippet': snippet})
    return results


# Save results to a CSV file
def save_results(results, filename):
    df = pd.DataFrame(results)
    df.to_csv(filename, index=False)


# Display CSV results in GUI
def display_csv_in_gui(filename):
    root = tk.Tk()
    root.title("CSV File Results")

    tree = ttk.Treeview(root, columns=('Title', 'Link', 'Snippet'), show='headings')
    tree.heading('Title', text='Title')
    tree.heading('Link', text='Link')
    tree.heading('Snippet', text='Snippet')

    df = pd.read_csv(filename)

    for index, row in df.iterrows():
        tree.insert('', tk.END, values=(row['title'], row['link'], row['snippet']))

    tree.pack(expand=True, fill='both')
    root.mainloop()


def main():
    queries = []
    print("Enter Google Dork queries (type 'done' when finished):")
    while True:
        query = input("Query: ")
        if query.lower() == 'done':
            break
        queries.append(query)

    if not queries:
        print("No queries provided. Exiting.")
        return

    browsers = ["chrome", "firefox", "edge"]
    all_results = []

    for browser in browsers:
        print(f"Using browser: {browser}")
        driver = init_driver(browser)
        for query in queries:
            print(f"Searching for: {query}")
            page_source = google_search(query, driver)
            results = parse_results(page_source)
            all_results.extend(results)
        driver.quit()

    if all_results:
        save_results(all_results, 'vulnerable_websites.csv')
        print(f"Results saved to vulnerable_websites.csv")
        display_csv_in_gui('vulnerable_websites.csv')
    else:
        print("No results found")


if __name__ == "__main__":
    main()
