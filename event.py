from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import pandas as pd
from bs4 import BeautifulSoup


class Event(object):
    def __init__(self, name: str, year: int) -> None:
        self.name = name
        self.year = year

        self.url = self._build_url()

        self._raw_html = self._simple_get()
        self._df = self._process_event_results()

        self.results = self._get_player_earnings()

    def _build_url(self) -> str:
        url_prefix = f'https://www.pgatour.com/tournaments/{self.name}'
        url_suffix = f'/past-results/jcr:content/mainParsys/pastresults.selectedYear.{self.year}.html'

        if self.name == 'wgc-mexico-championship':
            url = url_prefix + '/en' + url_suffix
        else:
            url = url_prefix + url_suffix

        return url

    def _get_player_earnings(self) -> pd.DataFrame:
        player = self._df.PLAYER
        earnings = self._df.OFFICIALMONEY
        df = pd.concat([player, earnings], axis=1)
        df['EVENT'] = self.name
        df['PLAYER_EVENT'] = df['PLAYER'] + '-' + df['EVENT']
        return df[['PLAYER_EVENT', 'PLAYER', 'EVENT', 'OFFICIALMONEY']]

    def _process_event_results(self) -> pd.DataFrame:
        """
        Processes the contents on GET requests and returns a Dataframe of
        the results
        """
        html = BeautifulSoup(self._raw_html, 'html.parser')
        table = html.find('table')
        return pd.read_html(str(table))[0]

    def _simple_get(self) -> bytes:
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(self.url)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(self.url, str(e)))
            return None

    @staticmethod
    def is_good_response(resp) -> bool:
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    @staticmethod
    def log_error(e):
        print(e)