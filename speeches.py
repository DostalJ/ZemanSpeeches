from selenium.webdriver import Chrome
from bs4 import BeautifulSoup
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import UnexpectedAlertPresentException
from time import sleep
from pandas import DataFrame
from pandas import to_datetime


def click(id_, driver, sleep_time=0.5):
    button = driver.find_element_by_id(id_=id_)
    sleep(sleep_time)
    button.click()
    sleep(sleep_time)


def download_and_save():
    browser = Chrome(executable_path="./chromedriver")
    browser.get('http://www.zemanmilos.cz/cz/clanky/')

    while True:
        try:
            click(id_='dalsistrankabtn', driver=browser)
        except UnexpectedAlertPresentException:
            alert = browser.switch_to_alert()
            alert.accept()
            break
        except Exception as e:
            print(e)
            sleep(30)
    print('End')
    page_source = browser.page_source
    browser.quit()
    page = BeautifulSoup(page_source, 'lxml')
    with open('./source.html', 'w') as out_file:
        out_file.write(str(page))



page_source = open('./source.html', 'r', encoding='utf8').read()
page = BeautifulSoup(page_source, 'lxml')
articles = page.find_all(name='div', attrs={'class': 'news_view'})

df = DataFrame(columns=['date', 'link', 'title'])

speech_index = 0
for article in articles:
    date = article.span.text[-10:]
    link = article.h3.a['href']
    title = article.h3.a.text

    if 'Projev' in title and int(date[-4:]) > 0:
        new_row = DataFrame(data={'date': date,
                                  'link': link,
                                  'title': title},
                            index=[speech_index])
        df = df.append(new_row)
        speech_index += 1

df['date'] = to_datetime(arg=df['date'], format='%d.%M.%Y')

df.to_csv('./speeches.csv', encoding='utf8', index=False)
