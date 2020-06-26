import requests
from lxml import html 

class Proxy:      
    proxy_url = 'http://www.ip-adress.com/proxy_list/' #переменной присваиваем ссылку сайта, выставляющего прокси-сервера
    proxy_list = [] #пустой массив для заполнения 

    def __init__(self):       
        r = requests.get(self.proxy_url)      
        page = html.fromstring(r.content)      
        result = page.xpath("//tr[@class='odd']/td[1]/text()") #берем содержимое тега вместе с внутренними тегами для получение списка прокси
        for i in result:#перебираем все найденные прокси
            if i in massiv:      
                yy = result.index(i)       
                del result[yy]      
        self.list = result #конструктору класса приравниваем прокси
        print(self.list)
        
    def get_proxy(self):
        for proxy in self.list: #в цикле перебираем все найденные прокси
            if 'https://'+proxy == proxy1: #проверяем, совпдает ли до этого взятый прокси с новым, если да:
                    global massiv
                    massiv = massiv + [proxy] #добавляем прокси к массиву
            url = 'https://'+proxy
            return url