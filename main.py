import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox
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

    else:
        raise ValueError("Unsupported browser")
    return driver


# Perform Google search using Dorks
def google_search(query, driver):
    search_url = f"https://www.google.com/search?q={query}"
    driver.get(search_url)
    time.sleep(3)  # Wait for the page to load

    # Scroll to the bottom to load all results
    body = driver.find_element(By.TAG_NAME, 'body')
    for _ in range(5):  # Adjust the range for more scrolling
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(1)

    return driver.page_source


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


# Function to run the search and display results
def run_search_and_display_results(queries, browsers):
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


# GUI for entering queries and displaying results
def main():
    def add_query():
        query = query_entry.get()
        if query:
            queries.append(query)
            query_list.insert(tk.END, query)
            query_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Input Error", "Please enter a query.")

    def delete_query():
        selected = query_list.curselection()
        if selected:
            for i in selected[::-1]:
                query_list.delete(i)
                del queries[i]
        else:
            messagebox.showwarning("Selection Error", "Please select a query to delete.")

    def add_selected_example():
        selected = example_listbox.curselection()
        if selected:
            for i in selected:
                query = example_listbox.get(i)
                queries.append(query)
                query_list.insert(tk.END, query)

    def start_search():
        if queries:
            final_queries = []
            for query in queries:
                advanced_query = query
                if date_range.get():
                    advanced_query += f" daterange:{date_range.get()}"
                if file_type.get():
                    advanced_query += f" filetype:{file_type.get()}"
                if site.get():
                    advanced_query += f" site:{site.get()}"
                final_queries.append(advanced_query)
            run_search_and_display_results(final_queries, browsers)
        else:
            messagebox.showwarning("Input Error", "Please enter at least one query.")

    def search_selected_examples():
        selected = example_listbox.curselection()
        if selected:
            selected_queries = [example_listbox.get(i) for i in selected]
            run_search_and_display_results(selected_queries, browsers)
        else:
            messagebox.showwarning("Selection Error", "Please select at least one example query to search.")

    queries = []
    browsers = ["chrome", "firefox"]

    example_queries = [
        'inurl:admin "login"',
        'inurl:wp-content "index of"',
        'intitle:"index of" "backup"',
        'intext:"password" "login"',
        'filetype:log "error"',
        'site:example.com "login"',
        'inurl:php?id=',
        'inurl:login.asp',
        'intitle:"index of" "private"',
        'intext:"username" "password"',
        'intitle:"index of" "config"',
        'inurl:"/proc/self/cwd"',
        'filetype:xls "password"',
        'inurl:"sitemap.xml" filetype:xml',
        'intitle:"index of" "database"',
        'inurl:"wp-admin/admin-ajax.php"',
        'inurl:"wp-login.php"',
        'intext:"confidential" "report"',
        'inurl:"/admin/config.php"',
        'intitle:"index of" "customer data"',
        'inurl:"/phpmyadmin"',
        'inurl:"/cgi-bin/" "404"',
        'intext:"backup" "filetype:sql"',
        'intext:"sensitive" "data"',
        'intitle:"index of" "user"',
        'intext:"restricted" "access"',
        'intitle:"index of" "credentials"',
        'inurl:"/passwords.txt"',
        'intext:"account" "login"',
        'intitle:"index of" "admin"',
        'intext:"admin" "login"',
        'inurl:"signup.php"',
        'inurl:"register.php"',
        'inurl:"/register"',
        'inurl:"/signup"',
        'intitle:"index of" "mail"',
        'intitle:"index of" "documents"',
        'inurl:"/upload"',
        'intext:"upload" "file"',
        'inurl:"/ftp"',
        'intitle:"index of" "ftp"',
        'inurl:"/private"',
        'intitle:"index of" "private"',
        'intext:"confidential" "filetype:pdf"',
        'intitle:"index of" "secrets"',
        'inurl:"/config"',
        'intitle:"index of" "confidential"',
        'inurl:"/files"',
        'intitle:"index of" "files"',
        'site:*.gov filetype:xls',
        'site:*.edu filetype:doc',
        'intext:"CV" filetype:pdf',
        'inurl:"/billing"',
        'intext:"tax" "document"',
        'intitle:"index of" "bank"',
        'intitle:"index of" "transactions"',
        'inurl:"/credit_card"',
        'intext:"password" "reset"',
        'inurl:"/customer_list"',
        'filetype:sql "dump"',
        'intitle:"index of" "confidential"',
        'inurl:"/admin/config.php"',
        'filetype:xls inurl:"/backup"',
        'filetype:pdf intext:"sensitive information"',
        'intext:"database" "username" "password"',
        'intitle:"index of" "user data"',
        'inurl:"/private" filetype:xls',
        'inurl:"/private" filetype:pdf',
        'inurl:"/private" filetype:doc',
        'inurl:"/secret" filetype:xls',
        'inurl:"/secret" filetype:pdf',
        'inurl:"/secret" filetype:doc',
        'inurl:"/confidential" filetype:xls',
        'inurl:"/confidential" filetype:pdf',
        'inurl:"/confidential" filetype:doc',
        'filetype:sql intext:"dump"',
        'filetype:sql intext:"backup"',
        'filetype:sql intext:"password"',
        'filetype:xls intext:"database"',
        'filetype:xls intext:"customer"',
        'filetype:xls intext:"email"',
        'filetype:xls intext:"phone"',
        'filetype:doc intext:"confidential"',
        'filetype:doc intext:"secret"',
        'filetype:doc intext:"sensitive"',
        'filetype:pdf intext:"financial"',
        'filetype:pdf intext:"report"',
        'filetype:pdf intext:"tax"',
        'filetype:pdf intext:"private"',
        'filetype:xls intext:"password"',
        'filetype:xls intext:"login"',
        'filetype:doc intext:"username"',
        'filetype:doc intext:"password"',
        'filetype:sql inurl:"/dump"',
        'filetype:sql inurl:"/backup"',
        'filetype:sql inurl:"/password"',
        'filetype:doc inurl:"/confidential"',
        'filetype:doc inurl:"/private"',
        'filetype:doc inurl:"/secret"',
        'filetype:pdf inurl:"/confidential"',
        'filetype:pdf inurl:"/private"',
        'filetype:pdf inurl:"/secret"',
        'filetype:xls inurl:"/confidential"',
        'filetype:xls inurl:"/private"',
        'filetype:xls inurl:"/secret"'
    ]

    root = tk.Tk()
    root.title("Google Dork Query Input")

    frame = tk.Frame(root)
    frame.pack(pady=10)

    query_label = tk.Label(frame, text="Enter Google Dork Query:")
    query_label.pack(side=tk.LEFT)

    query_entry = tk.Entry(frame, width=50)
    query_entry.pack(side=tk.LEFT, padx=10)

    add_button = tk.Button(frame, text="Add Query", command=add_query)
    add_button.pack(side=tk.LEFT)

    delete_button = tk.Button(frame, text="Delete Query", command=delete_query)
    delete_button.pack(side=tk.LEFT)

    query_list_label = tk.Label(root, text="Queries:")
    query_list_label.pack(pady=5)

    query_list = tk.Listbox(root, width=100, height=10)
    query_list.pack(pady=5)

    example_frame = tk.Frame(root)
    example_frame.pack(pady=10)

    example_label = tk.Label(example_frame, text="Example Google Dork Queries:")
    example_label.pack()

    example_listbox = tk.Listbox(example_frame, selectmode=tk.MULTIPLE, width=100, height=10)
    for example_query in example_queries:
        example_listbox.insert(tk.END, example_query)
    example_listbox.pack()

    add_example_button = tk.Button(root, text="Add Selected Examples", command=add_selected_example)
    add_example_button.pack(pady=5)

    search_example_button = tk.Button(root, text="Search Selected Examples", command=search_selected_examples)
    search_example_button.pack(pady=5)

    # Advanced search options
    advanced_frame = tk.LabelFrame(root, text="Advanced Search Options", padx=10, pady=10)
    advanced_frame.pack(pady=10, fill="x")

    date_range_label = tk.Label(advanced_frame, text="Date Range (e.g., 2457388-2457389):")
    date_range_label.grid(row=0, column=0, sticky='w')
    date_range = tk.Entry(advanced_frame, width=30)
    date_range.grid(row=0, column=1)

    file_type_label = tk.Label(advanced_frame, text="File Type (e.g., pdf):")
    file_type_label.grid(row=1, column=0, sticky='w')
    file_type = tk.Entry(advanced_frame, width=30)
    file_type.grid(row=1, column=1)

    site_label = tk.Label(advanced_frame, text="Site (e.g., example.com):")
    site_label.grid(row=2, column=0, sticky='w')
    site = tk.Entry(advanced_frame, width=30)
    site.grid(row=2, column=1)

    start_button = tk.Button(root, text="Start Search", command=start_search)
    start_button.pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
