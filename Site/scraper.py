from serpapi import GoogleSearch
import json 
from random import choice as random_choice
from urllib.request import urlopen
from urllib.parse import urlparse, parse_qs
import requests
from flask import request
import sqlite3
from bs4 import BeautifulSoup

ALL_KEYS = [
    "51885409429729e8eafae701b085d38c8610ad3a43dbd09902c90e9a94b5f7c4",
    "a671165f2a3ea4f0fe16de05a522f510fa5a95654b9ee8bde967315d7d31df1e",
    "5498076ef848bfe647f829789f64a92c3ccfb5378aabfe3179489ef0996a4e2b",
    "899169763c67e294e3eff95b050263b60277b9d55888d69f4ee29571a37c0d92",
    "f2124b06d99425903dbcad15caaa356c46cb41b718c7d948fecbe29f2d4fe266",
    "06556192c512245973c3c8c053be4d8be7b569a088a2ad175905d09ba4ef2fac",
    "753d55265a5944e48010c07836430d182dd641ba775f6d994af26f33cdcd5c97",
    "f0873fc767ece14260796530cb1e595476a5f2b2e5c1f055a7a44ecd2a487cc6",
    "4d8ba227ea969746410370b862076a4f77766886d6ea8cff5da9cc745e9d9ea6",
    "e0907c398fb8e29ad3166baf36f36bc4d122acdcdf96e1c0e16eb38357c16108",
    "3b67157423152bd12b175a79c68acb7ca21263e4e689198043ea9f1970ea1f5c",
    "c78f89cd3967cfef5f3de3cb1a184a22404e095f3adcc9683d0cfdf9f1f1fff4",
    "c70b6b5dfd250e37b7144b5000f74c3eb97a2efbef4c653a161c50f15e8a20fc"
]

def trigger_bulk(query, ads):
    params = {
      "engine": "google_shopping",
      "q": query,
      "hl": "en",
      "gl": "uk",
      "google_domain": "google.co.uk",
      "location": "Greater London",
      "api_key": random_choice(ALL_KEYS)
    }

    search = GoogleSearch(params)
    results = search.get_dict()
    shopping_results = results["shopping_results"]
    item_list_dic = []

    if not shopping_results:
        print("No results found")
        return []

    for shopping_result in shopping_results:
        temp_dic = {}
        temp_dic["title"] = shopping_result["title"]
        temp_dic["source"] = shopping_result["source"]
        temp_dic["extracted_price"] = shopping_result["extracted_price"]
        temp_dic["link"] = shopping_result["link"]
        temp_dic["product_id"] = shopping_result.get("product_id", "")
        item_list_dic.append(temp_dic)
    
    
    if ads:
        try:
            inline_shopping_results = results["inline_shopping_results"]

            for inline_shopping_result in inline_shopping_results:
                temp_dic = {}
                temp_dic["title"] = inline_shopping_result["title"]
                temp_dic["extracted_price"] = inline_shopping_result["extracted_price"]
                temp_dic["source"] = inline_shopping_result["source"]
                r = requests.get(inline_shopping_result["link"], allow_redirects=False)
                googlead_location_url = parse_qs(urlparse(r.headers["Location"]).query)["adurl"][0]
                temp_dic["link"] = googlead_location_url
                item_list_dic.append(temp_dic)
        except:
            pass

    return item_list_dic


def full_trigger_update(user_id):
    connect = sqlite3.connect('shop_scanner.db')
    command = connect.cursor()
    command.execute('SELECT product_id, old_price, new_price FROM shop_items WHERE ID =?', [user_id],)
    products = command.fetchall()
    for product_id, old_price, new_price in products:
        single_trigger_update(product_id, new_price, old_price)


def single_trigger_update(product_id, new_price, old_price):
    if product_id != "":    
        connect = sqlite3.connect('shop_scanner.db')
        command = connect.cursor()
    
        params = {
        "engine": "google_product",
        "product_id": product_id,
        "hl": "en",
        "gl": "uk",
        "google_domain": "google.co.uk",
        "location": "Greater London",
        "api_key": random_choice(ALL_KEYS)
        }
        search = GoogleSearch(params)
        results = search.get_dict()
        product_results = results["sellers_results"]["online_sellers"]
        price = new_price if new_price else old_price    
        best_price = price
        product_link = ""
        for online_sellers in product_results:
            if "total_price" not in online_sellers:
                continue
            new_price = online_sellers["total_price"]
            parsed_price = float(new_price[1:].replace(",", "")) # Price from API starts with £ sign, so we need to remove tha  
            if best_price < parsed_price:
                continue
            
            best_price = parsed_price
            product_link = online_sellers["link"]
            favicon = product_link.replace("https://www.google.co.uk/url?q=", "")
            favicon_url = f"https://www.google.com/s2/favicons?domain=https://{urlparse(favicon).netloc}&sz=256"
            shop_name = online_sellers["name"]
        if best_price == price:
            return
        command.execute("UPDATE OR IGNORE shop_items SET favicon_link= ?, shop_name= ?, new_price = ?, old_price = ?, item_url = ? WHERE product_id = ?", (favicon_url, shop_name, best_price, price, product_link, product_id))
        connect.commit()
    else:
        pass