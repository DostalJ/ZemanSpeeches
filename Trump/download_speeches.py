from requests import get  # downloading page source
from bs4 import BeautifulSoup  # BeautifulSoup for processing html source pages
from pandas import DataFrame, to_datetime
from time import sleep


class TrumpArticlesDownloader:
    def __init__(self, base_url, sleep_time=0.3):
        self.base_url = base_url
        self.sleep_time = sleep_time

        self.dates = []
        self.titles = []
        self.links = []

    def get_dates_titles_links(self, source):
        page = BeautifulSoup(source, 'lxml')
        speeches_info = page.findAll(name='h3',
                                     attrs={'class': 'field-content'})
        dates_info = page.findAll(name='span',
                                  attrs={'class': 'field-content'})

        for i in range(len(speeches_info)):
            speech = speeches_info[i]
            date = dates_info[i]

            title = speech.text
            # print('-'*40)
            # print(title)
            if (('Remarks by President Trump' in title
                 or 'President Donald J. Trump’s Weekly Address' in title
                 or 'Statement by President' in title)
                 and ('and' not in title)):
                self.titles.append(title)
                self.links.append('https://www.whitehouse.gov' + speech.a['href'])
                self.dates.append(date.text)
                # print('YES')
            # print('-'*40)

    def scrap_articles_info(self, base_url):
        page_number = 0
        while True:
            sleep(self.sleep_time)
            source = get(base_url.format(page_number)).text.encode(encoding='utf8')
            if b'views-field views-field-created' not in source:
                break
            else:
                self.get_dates_titles_links(source=source)
                page_number += 1

    def scrap_article(self, link):
        sleep(self.sleep_time)
        source = get(link).text.encode(encoding='utf8')
        page = BeautifulSoup(source, 'lxml')
        text = page.find(name='div', attrs={'class': 'field-item even'})
        paragraphs = [x.text for x in text.findAll('p')]

        speech = ''.join(paragraphs[2:])
        speech = speech.replace(u'\n', u'')  # replace newline tag
        speech = speech.replace(u'\t', u'')  # replace newline tag
        speech = speech.replace(u'\xa0', u' ')  # replace hard space tag
        speech = speech[16:-70]
        return speech

    def download_speeches(self):
        self.scrap_articles_info(base_url=self.base_url)

        df = DataFrame(columns=['date', 'link', 'title'])
        df['date'] = self.dates
        df['link'] = self.links
        df['title'] = self.titles

        df['date'] = to_datetime(arg=df['date'], infer_datetime_format=True)

        speeches = []
        for link in df['link'].values:
            # print('-'*40)
            # print(link)
            # print('-'*40)
            speech = self.scrap_article(link=link)
            speeches.append(speech)
        df['text'] = speeches
        return df


URL = 'https://www.whitehouse.gov/briefing-room/speeches-and-remarks?term_node_tid_depth=31&page={}'
myTrumpArticlesDownloader = TrumpArticlesDownloader(base_url=URL)
df = myTrumpArticlesDownloader.download_speeches()
df.to_csv('./speeches.csv', encoding='utf8', index=False, sep=';')
