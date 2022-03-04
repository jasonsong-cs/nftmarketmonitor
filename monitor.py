import requests
import json
import threading

import random
import time
from datetime import datetime

webhook = "" #Enter the discord webhook URL

headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'} #update header to your liking/latest version

#Sending webhook notification
def sendWebhookNotification(link, img, name, priceone, pricetwo):
    
    data = {
    "username": "Jason's NFT Monitor",
    "avatar_url": "http://4.bp.blogspot.com/_rkBUPPV7ZHU/SGUcA9Od2UI/AAAAAAAAAmM/TR0BwScB2FA/s1600/sad.bmp",
    "content": "@everyone",
    "embeds": [{
        "title": name,
        "url": link,
        "description": "Found for " + str(priceone) + " next lowest listing is " + str(pricetwo),
        "thumbnail": {"url": img},
    }]
    }
    
    try:
        result = requests.post(webhook, data=json.dumps(data), headers={"Content-Type": "application/json"})
    except:
        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "] " + " Failed to send webhook!")

            
def nft_monitor(project_name, linkcreated, proxy, seen, start, multi, count_str):
    multiplier = multi
    proxies = proxy
    iteration = 0
    while True:
        try:
            t = requests.get(linkcreated, headers = headers, proxies=proxies).json
            #Getting the lowest priced listing price and the second lowest priced listing price (while filtering what's at 0
            i = 0
            price_first = 0
            while (price_first == 0):
                price_first = t()['results'][i]['price']
                i = i + 1
            j = i - 1
            price_second = 0
            while (price_second == 0):
                price_second = t()['results'][i]['price']
                i = i + 1
            #True if the lowest price is lower than the second lowest price multiplied by the given multiplier, and the second lowest is greater than 0.04 SOL
            if price_first <= price_second * multiplier and price_second >= 0.04:
                mintAddress = t()['results'][j]['mintAddress']
                if mintAddress not in seen: #Checks if it's not seen
                    try:
                        name = t()['results'][j]['title']
                        link = "https://www.magiceden.io/item-details/" + mintAddress
                        img = t()['results'][j]['img']
                        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] " + name + " found, sending webhook!")
                        sendWebhookNotification(link, img, name, price_first, price_second) #Sends webhook
                        seen.append(mintAddress) #Adding the mintAddress to seen array
                    except:
                        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Error sending webhook!")
                        continue
            if iteration == 3600: #if the while loop occurs 3600 times
                new_multiplier = get_multipler_iter(project_name, count_str, proxies) #getting new multiplier for the project
                if multiplier == new_multiplier: #if multiplier stays the same
                    print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] " + project_name + " multiplier not changed")
                elif new_multiplier == 0: #if multiplier returns 0 (not monitoring)
                    print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] " + project_name + " stopping task now")
                    started.remove(project_name)
                    proxies_list.append(proxies['https'])
                    return 0 #end the thread
                else:  #if multiplier changed to a different number than 0
                    multiplier = new_multiplier
                    printingmulti = new_multiplier * 100
                    print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] " + project_name + " updated multiplier to " + str(printingmulti) + "%")
                iteration = 0 #reset iteration
                seen = [] #reset seen
            else:
                iteration = iteration + 1 #add 1 to iteration if it didn't reach 3600
            start = 0 #reset start
            continue
        except:
            print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] You have been rate limited! Rotating Proxy!")
            proxies_list.append(proxies['https'])
            proxies = { 'https' : random.choice(proxies_list) }
            proxies_list.remove(proxies['https'])
            start = start + 1
            if start == 10: #If 10 exception/error in a row, end the thread
                return 0
            continue

#Function to get the initial multiplier
def get_multipler(project, count_str, proxy):
    proxies = proxy
    while True:
        try:
            url = "https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/" + project
            t = requests.get(url, headers = headers, proxies = proxies).json
            volume = t()['results']['volume24hr']
            avgPrice = t()['results']['avgPrice24hr']
            count = t()['results']['listedCount']
            if (volume is None) or (avgPrice is None) or (count is None) or (count <= 35):
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Not monitoring " + project + "!")
                proxies_list.append(proxies['https'])
                return 0
            sales_24hours = volume / avgPrice
            if sales_24hours >= 100:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Retrieved multiplier for " + project + " 66%!")
                proxies_list.append(proxies['https'])
                return 0.66
            elif sales_24hours >= 80:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Retrieved multiplier for " + project + " 51%!")
                proxies_list.append(proxies['https'])
                return 0.51
            elif sales_24hours >= 60:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Retrieved multiplier for " + project + " 41%!")
                proxies_list.append(proxies['https'])
                return 0.41
            elif sales_24hours >= 40:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Retrieved multiplier for " + project + " 31%!")
                proxies_list.append(proxies['https'])
                return 0.31
            elif sales_24hours >= 20:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Retrieved multiplier for " + project + " 21%!")
                proxies_list.append(proxies['https'])
                return 0.21
            else:
                print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Not monitoring project " + project + "!")
                proxies_list.append(proxies['https'])
                return 0
        except:
            print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Error getting multiplier for " + project + " trying again! Rotating Proxies")
            proxies_list.append(proxies['https'])
            proxies = { 'https' : random.choice(proxies_list) }
            proxies_list.remove(proxies['https'])

#Function that's called to update the multiplier if needed once 3600 iteration occurs    
def get_multipler_iter(project, count_str, proxy):
    proxies = proxy
    while True:
        try:
            url = "https://api-mainnet.magiceden.io/rpc/getCollectionEscrowStats/" + project
            t = requests.get(url, headers = headers, proxies = proxies).json
            volume = t()['results']['volume24hr']
            avgPrice = t()['results']['avgPrice24hr']
            count = t()['results']['listedCount']
            if (volume is None) or (avgPrice is None) or (count is None) or (count <= 35):
                proxies_list.append(proxies['https'])
                return 0
            sales_24hours = volume / avgPrice
            if sales_24hours >= 100:
                return 0.66
            elif sales_24hours >= 80:
                return 0.51
            elif sales_24hours >= 60:
                return 0.41
            elif sales_24hours >= 40:
                return 0.31
            elif sales_24hours >= 20:
                return 0.21
            else:
                return 0
        except:
            print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Error getting multiplier for " + project + " trying again!")

def initiate(project_name,count_str):
    proxies = { 'https' : random.choice(proxies_list) }
    proxies_list.remove(proxies['https'])
    multiplier = get_multipler(project_name, count_str, proxies)
    if multiplier > 0: #Only starting projects with sales
        seen = []
        start = 0
        proxies = { 'https' : random.choice(proxies_list) }
        proxies_list.remove(proxies['https'])
        linkcreated = "https://api-mainnet.magiceden.io/rpc/getListedNFTsByQuery?q=%7B%22%24match%22%3A%7B%22collectionSymbol%22%3A%22" + project_name + "%22%7D%2C%22%24sort%22%3A%7B%22takerAmount%22%3A1%2C%22createdAt%22%3A-1%7D%2C%22%24skip%22%3A0%2C%22%24limit%22%3A20%7D"
        threading.Thread(target=nft_monitor, args=(project_name,linkcreated,proxies,seen,start,multiplier,count_str)).start()
        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "][Task " + count_str + "] Started task!")
        total.append("1")
        started.append(project_name)
    else:
        return 0 #To close thread

#Returns the entire collection names (strings) in an array
def get_collections():
    items = []
    url = "https://api-mainnet.magiceden.io/all_collections"
    #url = "https://api-mainnet.magiceden.io/rpc/getAggregatedCollectionMetrics" #Alternate URL
    t = requests.get(url, headers = headers).json
    for item in t()['collections']:
        project_name = item['symbol']
        try:
            if ((item['isFlagged'] == False) and (project_name not in started)):
                items.append(project_name)
        except: #When there is no isFlagged value
            if project_name not in started:
                items.append(project_name)
    return items

#Starting the whole function
def start_monitor():
    count = 1 #To give task numbers
    while True:
        temp = len(total)
        projects = get_collections() #Getting all project names
        for project_name in projects: #iterating over each project
            count_str = str(count)
            threading.Thread(target=initiate, args=(project_name,count_str)).start()
            count = count + 1
            time.sleep(0.015)
        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "] " + "initiated tasks!") #Printing when finishing launching all the threads
        time.sleep(30)
        started_num = len(total) - temp #Calculation on how many started (Total now - Total at before starting)
        str_started = str(started_num)
        print("[" + datetime.now().strftime("%H:%M:%S.%f")[:-3] + "] " + str_started + " tasks started!")
        time.sleep(5400) #Sleeping until next check (1.5 hour)

#Returns the proxies from the given textfile after formatting it into an array
def proxylist(textfile):
    opened_file = open(textfile, "r")
    proxyoutput = []

    #Supports user:pass proxy and just normal proxies
    for line in opened_file:
        line_splitted = line.split(":")
        try:
            proxyformatted = "https://" + line_splitted[2] + ":" + line_splitted[3].rstrip() + "@" + line_splitted[0] + ":" + line_splitted[1]
        except:
            proxyformatted = "https://" + line_splitted[0] + ":" + line_splitted[1].rstrip()
        proxyoutput.append(proxyformatted)
    
    return proxyoutput

if __name__ == "__main__":
    #Initiating empty array to store started projects, total number and formatting proxies into an array
    started = []
    total = []
    proxies_list = proxylist("proxies.txt")
    
    #Starting project
    start_monitor()
