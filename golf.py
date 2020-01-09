from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import pandas as pd
from bs4 import BeautifulSoup
import xlwings as xw


def main():
    wb = xw.Book.caller()
    ws_results = wb.sheets['RESULTS']
    ws_picks = wb.sheets['PICKS']

    event = wb.sheets['Get Data'].range('B4').value
    year = wb.sheets['Get Data'].range('B3').value
    results = get_results(event=event, year=int(year))
    last_row = ws_results.range('A' + str(ws_results.cells.last_cell.row)).end('up').row
    ws_results.range('A1').offset(last_row, 0).options(index=False, header=False).value = results

    participants = ws_picks.range('A7:A87').options(pd.Series, index=False, header=False).value
    money = ws_picks.range('AX7:AX87').options(pd.Series, index=False, header=False).value
    standings = pd.concat([participants, money], axis=1)
    standings.columns = ['participants', 'money']
    sorted_standings = standings.sort_values(by=['money'], ascending=False)
    ws_picks.range('E96').options(index=False, header=False).value = sorted_standings


def get_results(event, year):
    """
    Attempts to get the results of an event by making a GET request to the PGA
    Tour's API. Returns a pandas DataFrame.
    """
    base_url = 'https://www.pgatour.com/tournaments/'
    url = f"{base_url}{event}/past-results/jcr:content/mainParsys/pastresults.selectedYear.{year}.html"
    url_en = f"{base_url}{event}/en/past-results/jcr:content/mainParsys/pastresults.selectedYear.{year}.html"

    try:
        results = simple_get(url)
        if results is None:
            results = simple_get(url_en)
    finally:
        html = BeautifulSoup(results, 'html.parser')
        table = html.find('table')
        df = pd.read_html(str(table))[0]
        df.columns = [' '.join(col).strip() for col in df.columns.values]
        df.columns = [
            'PLAYER',
            'POS',
            'ROUND 1',
            'ROUND 2',
            'ROUND 3',
            'ROUND 4',
            'TOTAL SCORE',
            'TO PAR',
            'OFFICIAL MONEY',
            'FEDEXCUPPOINTS'
        ]
        df['EVENT'] = event
        df['PLAYER_EVENT'] = df['PLAYER'] + '-' + df['EVENT']

        out = df[['PLAYER_EVENT', 'PLAYER', 'EVENT', 'OFFICIAL MONEY']]
        return out


def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)


def log_error(e):
    print(e)


if __name__ == "__main__":
    xw.books.active.set_mock_caller()
    main()