global proxy1
proxy1 = ''
from datetime import date, datetime
import requests
from bs4 import BeautifulSoup as BS
import csv
import json
import re
from lxml import html 
from proxy import Proxy

URL = "https://www.zakon.kz/news"
COMMENTS_URL = "https://zcomments.net/service/init/1"
proxy_change_counter = 4

def get_all_urls():  # Получаем все урлы новостей для дальнейшего парсинга                      
    r = requests.get(URL) 
    html = BS(r.content, 'html.parser') # получаем html главной страницы
    urls = []
    for item in html.select('.cat_news_item'): # пробгаемся циклом по блокам новостец
        data = item.contents
        if len(data) == 3: # если это блок с датой а не новостью
            continue 
        current_url = "https://www.zakon.kz/" + data[3].get("href") # получаем урл новости
        urls.append(current_url)            
    return urls

def parse_one_new(url): # функция парсит новость по урлу
    try:
        
        r = requests.get(url, proxies={'https': proxy1})
        r.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
        return {}
    except Exception as err:
        print(f'Other error occurred: {err}') 
        return {}

    html = BS(r.content, 'html.parser')

    new_id = re.split('/|-', url)[4] # id новости, нужно для пост запроса    
    main_block = ""
    try:
        main_block = html.select('.fullnews')[0].contents
    except IndexError:
        return {}
    
    title = main_block[1].text # получаем заголовок
    content = main_block[3].text # получаем текст новости
    pub_date = main_block[9].contents[1].text
    pub_time = pub_date.split(", ")[1]
    pub_date = datetime.today().strftime("%d-%m-%Y")
    pub_date += ", " + pub_time
    pub_date = datetime.strptime(pub_date, "%d-%m-%Y, %H:%M")    
    
    content += html.select('#initial_news_story')[0].text[:-59] # [:-59] нужно для удаления вот этого текста в конце статьи "Больше новостей в Telegram-канале «zakon.kz». Подписывайся!"
    post_data = {
        "page_title": title,
        "page_url": url,
        "block_code": "zakonnewsid" + new_id,
        "lang": "ru",
    }
    r = requests.post(COMMENTS_URL, data=post_data) # отправляем пост запрос на урл, который должен вернуть всю инфу о коментах
    json_data = str(r.content)
    count_of_comments = ''
    try:    
        count_of_comments = re.split('"total":|,"mode"', json_data)[1]
    except:
        count_of_comments = 0 # коменты отключены

    return {"title": title, "content": content, "pub_date": pub_date, "count_of_comments": count_of_comments} # возвращаем объект с данными новости
    
def save_all_news(data): # Сохраняем все данные в csv файл
    with open('news.csv', mode='w', encoding='utf-8') as news_file:
        employee_writer = csv.writer(news_file, delimiter='|')
        for new in data:            
            employee_writer.writerow([new["title"], new["content"], new["pub_date"], new["count_of_comments"]])
        

print("Получаем урлы...")

urls = get_all_urls()
data = []

print("Парсим новости...")
counter = proxy_change_counter # чтобы сразу сменить прокси
for url in urls: 
    if counter == proxy_change_counter: # будем менять прокси каждые N просмотренных новостей
        global proxy   
        proxy = Proxy()
        proxy = proxy.get_proxy() 
        print(proxy)
        proxy1 = proxy    
        counter = 1
    
    new = parse_one_new(url)
    if new:
        data.append(new)
    counter += 1

save_all_news(data)

print("Поздравляю!! Вы украли новости с сайта)")
