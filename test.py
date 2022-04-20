import requests
import json
import re
from bs4 import BeautifulSoup
import pandas as pd
import telegram_send
import time
from datetime import date, datetime


# init
link_m = "https://www.nike.com/pl/t/buty-meskie-air-force-1-07-lKPQ6q/CW2288-111"
product_id_m = "CW2288-111"
link_f = "https://www.nike.com/pl/t/buty-air-force-1-07-J29nBv/DD8959-100"
product_id_f = "DD8959-100"

product_size = "43"
sleep_time = 5 # in min


def get_shoe_status(link, product_id, product_size):
    session = requests.Session()
    try:
        html_data = session.get(link).text
    except:
        telegram_send.send(messages=[f'{now} \n Something went wrong with request'], silent=False)
        
    soup = BeautifulSoup(html_data, "html.parser")
    data = json.loads(soup.find('script',text=re.compile('INITIAL_REDUX_STATE')).text.replace('window.INITIAL_REDUX_STATE=','')[0:-1])

    # getting availables
    ava = data['Threads']['products'][product_id]['availableSkus']
    skus = data['Threads']['products'][product_id]['skus']

    # merging df to be more visible
    df_skus = pd.DataFrame(skus)
    df_available_skus = pd.DataFrame(ava)
    final = df_skus.merge(df_available_skus[['skuId','available', 'level']], on='skuId', how="left")

    try:
        shoes_status = final[final['localizedSize'] == product_size]['available'].values[0]
    except:
        shoes_status = False

    return shoes_status


while True:

    shoes_status_m = get_shoe_status(link_m, product_id_m, product_size)
    shoes_status_f = get_shoe_status(link_f, product_id_f, product_size)
    
    now = datetime.now().strftime("%H:%M:%S")
    if shoes_status_m == True:
        telegram_send.send(messages=[f'{now} \n Meskie Air Force One {product_size} jest już dostępne na stronie'], silent=False)
    elif shoes_status_f == True:
        telegram_send.send(messages=[f'{now} \n Damskie Air Force One {product_size} jest już dostępne na stronie'], silent=False)

    time.sleep(sleep_time * 60)

