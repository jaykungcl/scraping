# ref: https://python.plainenglish.io/scraping-the-subpages-on-a-website-ea2d4e3db113

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import json

def getdata(url):
    r = None
    try:
        r = requests.get(url)
    except:
        return ''
    return r.text

dict_href_links = {}

def get_links(website_link):
    html_data = getdata(website_link)
    if not html_data:
        return ({}, '')
    soup = None
    try:
        soup = BeautifulSoup(html_data, "html.parser")
    except:
        return ({}, '')
    list_links = []
    title = ''

    for link in soup.find_all("a", href=True):

        # base_link = website
        # if(soup.find('title')):
        #     title = soup.find('title').get_text()
        # if title.startswith('404 Error'):
        #     base_link = website
        base_link = "https://www.ocsc.go.th/"
        
        # Append to list if new link contains original link
        if str(link["href"]).startswith((str(website_link))):
            list_links.append(link["href"])
            
        # Include all href that do not start with website link but with "/"
        if str(link["href"]).startswith("/"):
            if link["href"] not in dict_href_links:
                print(link["href"])
                dict_href_links[link["href"]] = None
                link_with_www = base_link + link["href"][1:]
                print("adjusted link =", link_with_www)
                list_links.append(link_with_www)
                
    # Convert list of links to dictionary and define keys as the links and the values as "Not-checked"
    dict_links = dict.fromkeys(list_links, {"checked": "Not-checked", "parent": website_link})

    if(soup.find('title')):
        title = soup.find('title').get_text()

    # return {"links": dict_links, "title": title}
    return (dict_links, title)

def get_subpage_links(l):
    for link in tqdm(l):
        # print(">>>>>>>>>", l[link]['checked'])
        # If not crawled through this page start crawling and get links
        if l[link]['checked'] == "Not-checked":
            # print('>>>>>>>>>>>>>>>>>')
            # print(l)
            # temp = get_links(link) 
            # dict_links_subpages = temp['links']
            tup = get_links(link)
            dict_links_subpages = tup[0]
            title = tup[1]


            children_list = list(dict_links_subpages.keys())

            index = link.find('?')
            if (index == -1):
                if 'parent' in l[link]:
                    l[link] = {"checked":"Checked", "title": title, "url": link, "children": children_list, "parent": l[link]['parent']}
                else:
                    l[link] = {"checked":"Checked", "title": title, "url": link, "children": children_list}
            else:
                base_url = link[0:index]
                query = link[index+1:]
                query_string_list = query.split('&')

                query_string = {}

                for q in query_string_list:
                    couple = q.split('=')
                    query_string = {**{couple[0]:couple[1]}, **query_string}

                l[link] = {"checked":"Checked", "title": title, "url": link, "base_url": base_url, "query_string": query_string, "children": children_list}
            # dict_links_subpages = get_links(link)
            # print(dict_links_subpages)
            # Change the dictionary value of the link to "Checked"
            # l[link] = {"checked":"Checked", "title": temp['title']}
        else:
            # Create an empty dictionary in case every link is checked
            dict_links_subpages = {}
        # Add new dictionary to old dictionary
        l = {**dict_links_subpages, **l}
    return l

# add websuite WITH slash on end
website = "https://www.ocsc.go.th/"
# create dictionary of website
dict_links = {website:{"checked":"Not-checked"}}

counter, counter2 = None, 0
while counter != 0: 
    counter2 += 1
    dict_links2 = get_subpage_links(dict_links)
    # Count number of non-values and set counter to 0 if there are no values within the dictionary equal to the string "Not-checked"
    # https://stackoverflow.com/questions/48371856/count-the-number-of-occurrences-of-a-certain-value-in-a-dictionary-in-python

    # for value in dict_links2.values():
    #     checked = value['checked']
    #     sum = 0
    #     if (checked == 'Not-checked'):
    #         sum += 1
    #         counter = sum
        

    counter = sum(value['checked'] == "Not-checked" for value in dict_links2.values())

    # Print some statements
    print("")
    print("THIS IS LOOP ITERATION NUMBER", counter2)
    print("LENGTH OF DICTIONARY WITH LINKS =", len(dict_links2))
    print("NUMBER OF 'Not-checked' LINKS = ", counter)
    print("")
    dict_links = dict_links2
    # Save list in json file
    a_file = open("data_with_title.json", "w")
    json.dump(dict_links, a_file)
    a_file.close()

