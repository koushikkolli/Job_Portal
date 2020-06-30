import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
import time

__URL__ = "https://www.indeed.com/jobs?"

def get_jobs_new(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    jobs = soup.find_all(name="div", attrs={"class": "jobsearch-SerpJobCard unifiedRow row result"})
    dataframe_dict = {}
    companies = []
    for job in jobs:
        company = job.find_all(name="span", attrs={"class": "company"})
        if len(company) > 0:
            for b in company:
                companies.append(b.text.strip())
        else:
            sec_try = job.find_all(name="span", attrs={"class": "result-link-source"})
            for span in sec_try:
                companies.append(span.text)
    dataframe_dict["Company"] = companies
    job_titles = []
    apply_sites = []
    for job in jobs:
        for a in job.find_all(name="a", attrs={"data-tn-element": "jobTitle"}):
            job_titles.append(a["title"])
            apply_sites.append("https://www.indeed.com" + a["href"])
    dataframe_dict["Job_title"] = job_titles
    dataframe_dict["Apply site"] = apply_sites
    locations = []
    for job in jobs:
        c = job.findAll("span", attrs={"class": "location"})
        for span in c:
            locations.append(span.text)
    dataframe_dict["Location"] = locations
    summaries = []
    for job in jobs:
        d = job.findAll("div", attrs={"class": "summary"})
        for span in d:
            summaries.append(span.text.strip())
    dataframe_dict["Summary"] = summaries
    dates = []
    for job in jobs:
        date = job.findAll("span", attrs={"class": "date"})
        for span in date:
            dates.append(span.text.strip())
    dataframe_dict["Date"] = dates
    return pd.DataFrame(dataframe_dict)


def get_apply_url(url):
    page1 = requests.get(url)
    soup1 = BeautifulSoup(page1.text, "html.parser")
    company_url = ""
    for a in soup1.find_all(name="a", text="Apply On Company Site"):
        company_url = a["href"]
    if company_url == "":
        company_url = url
    return company_url


def prepare_url(key_word="", where="", remote=0, formage=0, salary="", location="", job_type="",company="",experience=""):
    if salary != "":
        if "$" in key_word:
            print("yes")
            keyword = key_word[:key_word.find("$")] + " " + salary
        else:
            keyword = key_word + "+" + salary
    keyword = keyword.replace(" ", "+")
    keyword = keyword.replace(",", "%2C")
    keyword = keyword.replace("/", "%2F")
    if where == "":
        if location != "":
            where = location
            location = ""
    where = where.replace(" ", "+")
    where = where.replace(",", "%2C")
    where = where.replace("/", "%2F")
    url = __URL__ + "&q=" + keyword + "&l=" + where
    if remote == 1:
        url += "&remotejob=1"
    if (formage > 0):
       url += "&fromage=" + str(formage)

    if (job_type != ""):
       url += "&jt=" + job_type

    if (experience != ""):
        url += "&explvl=" + experience

    df = get_apply_url(url)
    return df



