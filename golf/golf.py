import pandas as pd
import xlwings as xw

from event import Event
from configure import feeds


def main():
    wb = xw.Book.caller()
    get_results()
    sort_standings()


def get_results():
    wb = xw.Book.caller()
    ws_results = wb.sheets['RESULTS']
    ws_get_data = wb.sheets['Get Data']

    tournament_name = ws_get_data.range('B4').value
    year = ws_get_data.range('B3').value
    tournament = Event(name=tournament_name, year=int(year))
    last_row = ws_results.range('A' + str(ws_results.cells.last_cell.row)).end('up').row
    ws_results.range('A1').offset(last_row, 0).options(index=False, header=False).value = tournament.results

    wb.sheets['PICKS'].activate()


def sort_standings():
    wb = xw.Book.caller()
    ws_picks = wb.sheets['PICKS']

    participants = ws_picks.range('A7:A87').options(pd.Series, index=False, header=False).value

    for feed in feeds:
        money = ws_picks.range(feed.source_range).options(pd.Series, index=False, header=False).value
        standings = pd.concat([participants, money], axis=1)
        standings.columns = ['participants', 'money']
        if standings.query('money > 0').shape[0] > 0:
            standings_sorted = standings[['participants', 'money']].sort_values(by=['money'], ascending=False)
            ws_picks.range(feed.destination_range).options(index=False, header=False).value = standings_sorted

    wb.sheets['PICKS'].activate()


if __name__ == "__main__":
    xw.books.active.set_mock_caller()
    main()
