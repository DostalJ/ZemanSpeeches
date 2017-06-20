from time import sleep  # sleeping
from requests import get  # downloading page source
from bs4 import BeautifulSoup  # BeautifulSoup for processing html source pages
from pandas import DataFrame  # DataFrame for storing and manipulating data
from pandas import to_datetime  # convert string to datetime
from selenium.common.exceptions import UnexpectedAlertPresentException  # selenium alert exception
from selenium.webdriver import Chrome  # Chrome browser driver


def click(id_, driver, sleep_time=0.5):
    """
    Clicks button with given id.
    Args:
        id_: id of the buttton
        driver: browser
        sleep_time: sleeps twice (after finding button and after clicking)
    """
    button = driver.find_element_by_id(id_=id_)  # find button
    sleep(sleep_time)  # sleep
    button.click()  # click
    sleep(sleep_time)  # sleep

URL = 'http://www.zemanmilos.cz/cz/'
def download_page_with_articles(url):
    """
    Clicks on button 'dalsistrankabtn' until all articles listed.
    Args:
        url: url to page with list of articles
    Returns:
        page_source: html source of whole page
    """
    print('Opening browser.')
    browser = Chrome(executable_path="./chromedriver")  # open browser
    browser.get(url)  # get page

    while True:
        try:
            # click on button for next articles
            click(id_='dalsistrankabtn', driver=browser)
        except UnexpectedAlertPresentException:  # if all articles listed
            alert = browser.switch_to_alert()
            alert.accept()  # accept the alert window
            break
        except Exception as e:
            print(e)
            sleep(30)
    print('Closing browser.')
    page_source = browser.page_source  # get source page
    browser.quit()
    return page_source
page_source = download_page_with_articles(url=URL + 'clanky/')


def process_page(page_source):
    """
    From source page with all articles get title, date, link
    Args:
        page_source: html source of the page with articles
    Returns:
        df: pandas DataFrame with columns=['date', 'link', 'title']
    """
    page = BeautifulSoup(page_source, 'lxml')  # process

    # find all articles
    articles = page.find_all(name='div', attrs={'class': 'news_view'})

    df = DataFrame(columns=['date', 'link', 'title'])  # create DataFrame
    speech_index = 0
    for article in articles:  # for all listed articles
        # date article was published
        date = article.span.text[-10:]
        # link to article
        link = 'http://www.zemanmilos.cz/' + article.h3.a['href']
        # title of the article
        title = article.h3.a.text

        # if the article is 'Projev' and has acceptable data
        if 'Projev' in title and int(date[-4:]) > 0:
            new_row = DataFrame(data={'date': date,
                                      'link': link,
                                      'title': title},
                                index=[speech_index])
            df = df.append(new_row)  # add to DataFrame
            speech_index += 1

    # parse date (only date, without time)
    df['date'] = to_datetime(arg=df['date'], format='%d.%M.%Y').dt.floor('d')
    return df
df = process_page(page_source=page_source)


def download_articles(df):
    """
    Download text of each article.
    Args:
        df: pandas DataFrame with columns=['date', 'link', 'title']
    Returns:
        df: pandas DataFrame with columns=['date', 'link', 'title', 'text']
    """
    print('Downloading each article...')
    speeches = []
    for speech_link in df['link'].values:  # for every link to article
        try:
            # get article source page
            req = get(url=speech_link).text.encode(encoding='utf8')
            # convert to html
            page = BeautifulSoup(markup=req, features='lxml')
            # find text of the speech
            speech = page.find(name='div', attrs={'class': 'wrap_detail'}).text
        except Exception as e:  # if exception occurs
            print('Exception for link {:s}:'.format(speech_link),  e)
        speech = speech.replace(u'\n', u'')  # replace newline tag
        speech = speech.replace(u'\xa0', u' ')  # replace hard space tag
        speeches.append(speech)
    df['text'] = speeches  # add to DataFrame
    return df
df = download_articles(df=df)
print('Done.')

# save to csv
df.to_csv('./speeches.csv', encoding='utf8', index=False, sep=';')

# from pandas import read_csv
# df = read_csv(filepath_or_buffer='./speeches.csv', sep=';', encoding='utf8')
