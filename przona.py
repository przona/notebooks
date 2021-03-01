from bs4 import BeautifulSoup
from colorama import Fore, Back, Style
import csv
import pandas as pd
import re
import requests
import time
from IPython.display import clear_output


def squeal(text=None):
    clear_output(wait=True)
    if not text is None: print(text)


def get_web_page(url, debug=True):
    time.sleep(1)
    web_page = requests.get(url)
    if web_page.status_code == 200:
        if debug:
            print(f"retrieved web page {url} (200/{len(web_page.content)})")
    else:
        print(Fore.RED, f"web page {url} returned status code {web_page.status_code}", Style.RESET_ALL)
    return(web_page.content)



def get_page_links(web_page, patterns=[]):
    page_links = []
    for a in BeautifulSoup(web_page, "html.parser").select('a'):
        try:
            href = a.get("href")
            for pattern in patterns:
                if re.search(pattern, href):
                    page_links.append(href)
        except TypeError:
            pass
    return(page_links)


def split_url(url):
    if re.search("^https?://", url, flags=re.IGNORECASE):
        return("/".join(url.split("/")[:3]), "/"+"/".join(url.split("/")[3:]))
    else:
        return("", url)

                            
def get_web_pages(url, patterns=[], processed_urls=[], debug=True):
    web_page_contents = get_web_page(url, debug)
    target_urls = get_page_links(web_page_contents, patterns)
    base_url, remote_file = split_url(url)
    web_pages = {remote_file: web_page_contents}
    retrieved_urls = [remote_file]
    while len(set(target_urls)) > len(web_pages):
        target_url = list(set(target_urls).difference(set(web_pages.keys())))[0]
        if target_url in processed_urls:
            web_pages[target_url] = "PROCESSED"
            if debug:
                print(f"already processed {target_url}")
        elif not re.search("\.html*$",target_url) and not re.search("/[^.]*$",target_url):
            web_pages[target_url] = "SKIPPED"
            if debug:
                print(f"skipped {target_url}")
        elif re.search("/gerelateerde_documenten/", target_url) and \
             "/".join(target_url.split("/")[6:]) in retrieved_urls:
            web_pages[target_url] = "DUPLICATE"
            if debug:
                print(f"duplicate {target_url}")
        else:
            web_pages[target_url] = get_web_page(base_url+target_url, debug)
            target_urls.extend(get_page_links(web_pages[target_url], patterns))
            if re.search("/gerelateerde_documenten/", target_url):
                retrieved_urls.append("/".join(target_url.split("/")[6:]))
    return(web_pages)


def get_recommendation_list(web_pages):
    recommendation_list = []
    for key in web_pages:
        for a in BeautifulSoup(web_pages[key], "html.parser").select('a'):
            try:
                href = a.get("href")
                if re.search("^/richtlijn/", href):
                    recommendation = href.split("/")[2]
                    if recommendation not in recommendation_list:
                        recommendation_list.append(recommendation)
            except TypeError:
                pass
    return(recommendation_list)


def save_dict(dictionary, out_file_name, mode="w"):
    out_file = open(out_file_name, mode)
    csvwriter = csv.writer(out_file)
    for key in dictionary:
        if type(dictionary[key]) == dict:
            row = [key]
            row.extend(list(dictionary[key].values()))
            csvwriter.writerow(row)
        elif type(dictionary[key]) == list:
            row = [key]
            row.extend(dictionary[key])
            csvwriter.writerow(row)
        else:
            row = [key, dictionary[key]]
            csvwriter.writerow(row)
    out_file.close()

    
def read_dict(file_name, spy=False):
    counter = 0
    dict_out = {}
    infile = open(file_name,"r")
    csvreader = csv.reader(infile)
    for row in csvreader:
        counter += 1
        if len(row) == 0:
            print(Fore.RED,"cannot happen")
        else:
            index = row.pop(0)
            if len(row) == 0:
                dict_out[index] = []
            elif type(row) == str:
                dict_out[index] = [row]
            else:
                dict_out[index] = row
        if counter % 1000 == 0:
            if spy: 
                squeal(counter)
    if spy:
        squeal(counter)
    infile.close()
    return(dict_out)


def get_duplicate_web_pages(web_pages, out_file_name):
    counter = 0
    for url in web_pages:
        counter += 1
        if type(web_pages[url]) == str and (web_pages[url] == "DUPLICATE" or web_pages[url] == "PROCESSED"):
            squeal(counter)
            content = get_web_page(BASE_URL+url)
            save_dict({url: content}, out_file_name, mode="a")
            

def update_recommendations(recommendation_list, processed_urls, out_file_name, BASE_URL=""):
    counter = 0
    for recommendation in recommendation_list:
        counter += 1
        print(counter, recommendation)
        if "/richtlijn/"+recommendation not in processed_urls:
            recommendation_web_pages = get_web_pages(BASE_URL+"/richtlijn/"+recommendation,
                                                     patterns=["^/richtlijn/", "^/gerelateerde_documenten"],
                                                     processed_urls = processed_urls,
                                                     debug=False)
            save_dict(recommendation_web_pages, out_file_name, mode="a")
            processed_urls += list(recommendation_web_pages.keys())


def get_categories(content):
    soup = BeautifulSoup(content)
    categories = {}
    for option in soup.select("option"):
        key = option.get("value")
        value = option.text
        categories[key] = value
    del(categories[""])
    return(categories)


def get_recommendations_per_category(categories):
    recommendations_per_category = {}
    for key in categories:
        query = BASE_QUERY+str(key)
        web_pages = get_web_pages(BASE_URL+query,
                                  patterns=["^/\?query=\&page=\d+"],
                                  processed_urls=[BASE_URL+query])
        print(f"category {key}; number of pages: {len(web_pages)}")
        recommendation_list = get_recommendation_list(web_pages)
        print(f"found {len(recommendation_list)} recommendations for category {key} {categories[key]}\n")
        recommendations_per_category[key] = recommendation_list
    return(recommendations_per_category)

def get_categories_per_recommendation(recommendations_per_category):
    categories_per_recommendation = {}
    for category in recommendations_per_category:
        for recommendation in recommendations_per_category[category]:
            if recommendation not in categories_per_recommendation:
                categories_per_recommendation[recommendation] = {}
                for c in recommendations_per_category:
                    categories_per_recommendation[recommendation][c] = " "
            categories_per_recommendation[recommendation][category] = "+"
    categories_per_recommendation = {r:categories_per_recommendation[r] for r in sorted(categories_per_recommendation.keys(),\
        key=lambda r:len([c for c in categories_per_recommendation[r] if categories_per_recommendation[r][c] == "+"]),reverse=True)}
    return(categories_per_recommendation)


def pretty_print(recommendations_per_category, outfile_name):
    categories_per_recommendation = get_categories_per_recommendation(recommendations_per_category)
    r_per_c = {c:{r:categories_per_recommendation[r][c] for r in categories_per_recommendation} for c in categories_per_recommendation[list(categories_per_recommendation.keys())[0]]}
    r_per_c = {c:r_per_c[c] for c in sorted(r_per_c.keys(), key=lambda c:len([r for r in r_per_c[c] if r_per_c[c][r] == "+"]), reverse=True)}
    pd.DataFrame(r_per_c).to_csv(outfile_name, index_label="richtlijn")
    return(pd.DataFrame(r_per_c))


def get_recommendations(web_pages):
    recommendations = []
    for url in web_pages:
        if re.search("^/richtlijn/", url):
            recommendation = url.split("/")[2]
            if not recommendation in recommendations and not re.search("[.?]", recommendation) and \
               not re.search("Oeps", str(web_pages[url])) and recommendation != "item":
                recommendations.append(recommendation)
    return(recommendations)


def count_suffixes(web_pages):
    suffixes = {}
    for key in web_pages.keys():
        suffix = key.split("/")[-1]
        if re.search("\.", suffix):
            suffix = suffix.split(".")[-1]
        else:
            suffix = ""
        if re.search("\?", suffix):
            suffix = suffix.split("?")[0]
        if not suffix in suffixes:
            suffixes[suffix] = 1
        else:
            suffixes[suffix] += 1
    return(suffixes)


def get_links(web_pages, recommendation, url_part):
    hrefs = []
    for url in web_pages.keys():
        if re.search(recommendation, url):
            soup = BeautifulSoup(web_pages[url][0])
            for tag in soup.select("a"):
                try:
                    href = tag.get("href")
                    if re.search(url_part, href) and href not in hrefs:
                        hrefs.append(href)
                except:
                    pass
    return(hrefs)
