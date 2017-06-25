from requests import get  # downloading page source
from bs4 import BeautifulSoup  # BeautifulSoup for processing html source pages
from pandas import DataFrame  # DataFrame for storing and manipulating data
from pandas import to_datetime  # convert string to datetime
from time import sleep  # sleeping


class TrumpArticlesDownloader:
    def __init__(self, base_url, sleep_time=0.3):
        """
        Class for downloading Trump's speeches from official WhiteHouse webpage
        Args:
            base_url: url of the official white house webpage with speeches
            sleep_time: sleeping time (after every request) [seconds]
        """
        self.base_url = base_urls  # url of the official white house webpage
        self.sleep_time = sleep_time  # sleeping time (after every request)

        self.dates = []  # dates for all articles
        self.titles = []  # titles for all articles
        self.links = []  # links for all articles

    def get_dates_titles_links(self, source):
        """
        Parse dates, titles and links for all articles from given source of the
        page. Adds dates, titles and links to self.dates, self.titles,
        self.links
        Args:
            source: html source of the page
        """
        page = BeautifulSoup(source, 'lxml')  # convert to usable format
        # find all fields with title and link
        speeches_info = page.findAll(name='h3',
                                     attrs={'class': 'field-content'})
        # find all fields with dates
        dates_info = page.findAll(name='span',
                                  attrs={'class': 'field-content'})

        for i in range(len(speeches_info)):  # for all articles
            speech = speeches_info[i]  # field with title and link
            date = dates_info[i]  # field with date

            title = speech.text  # title of the speech
            # print('-'*40)
            # print(title)
            # if the title is suitable (article is speech)
            if (('Remarks by President Trump' in title
                 or 'President Donald J. Trump’s Weekly Address' in title
                 or 'Statement by President' in title)
                and ('and' not in title)):
                self.titles.append(title)  # add title
                self.links.append('https://www.whitehouse.gov'
                                  + speech.a['href'])  # add link
                self.dates.append(date.text)  # add date
                # print('YES')
            # print('-'*40)

    def scrap_articles_info(self, base_url):
        """
        From base webpage (page with article lists) scrap all information
        about Trump's speeches.
        Args:
            base_url: url of the official white house webpage with speeches
        """
        page_number = 0  # page number
        while True:  # while there are articles
            sleep(self.sleep_time)  # sleep
            # get html source of the page
            source = get(base_url.format(page_number)).text.encode('utf8')
            # if there aren't any more articles
            if b'views-field views-field-created' not in source:
                break  # stop scraping
            else:
                self.get_dates_titles_links(source)  # scrap info about article
                page_number += 1  # go to next page

    def scrap_article(self, link):
        """
        Scrap text of the single article from the page with single article.
        Args:
            link: link to the page with single article
        Returns:
            speech: text of the speech
        """
        sleep(self.sleep_time)  # sleep
        source = get(link).text.encode('utf8')  # encode source of the page
        page = BeautifulSoup(source, 'lxml')  # read in BeautifulSoup
        # find article text
        text = page.find(name='div', attrs={'class': 'field-item even'})
        # divide to paragraphs
        paragraphs = [x.text for x in text.findAll('p')]

        speech = ''.join(paragraphs[2:])  # join only text
        speech = speech.replace(u'\n', u'')  # replace newline tag
        speech = speech.replace(u'\t', u'')  # replace newline tag
        speech = speech.replace(u'\xa0', u' ')  # replace hard space tag
        speech = speech[16:-70]  # remove 'THE MRS PRESIDENT'
        return speech

    def download_speeches(self):
        """
        Download all Donald Trump's speeches from White House webpage.
        Returns:
            df: DataFrame, columns=['date', 'link' 'title', 'text']
        """
        # get info about articles
        self.scrap_articles_info(base_url=self.base_url)

        df = DataFrame(columns=['date', 'link', 'title'])  # define DataFrame
        df['date'] = self.dates
        df['link'] = self.links
        df['title'] = self.titles
        # convert dates to datetime type
        df['date'] = to_datetime(arg=df['date'], infer_datetime_format=True)

        speeches = []  # list for speeches
        for link in df['link'].values:  # for each article page
            # print('-'*40)
            # print(link)
            # print('-'*40)
            speech = self.scrap_article(link=link)  # scrap text of the speech
            speeches.append(speech)  # add to the list
        df['text'] = speeches  # add to the DataFrame
        return df


URL = 'https://www.whitehouse.gov/briefing-room/speeches-and-remarks?term_node_tid_depth=31&page={}'
myTrumpArticlesDownloader = TrumpArticlesDownloader(base_url=URL)
df = myTrumpArticlesDownloader.download_speeches()

# save data
df.to_csv('./speeches.csv', encoding='utf8', index=False, sep=';')
