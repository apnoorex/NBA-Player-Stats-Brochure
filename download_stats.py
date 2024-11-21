import pandas as pd
import urllib.request
from bs4 import BeautifulSoup


def clean_salary_entries(salary):
    """ Sums up all the income because sometimes players have retained earnings."""
    sal = salary.replace(',', '').split('$')
    sal = [int(s) for s in sal if s != '']
    return '$' + f"{sum(sal):,}"

def download_stats(player):
    """ Collects stats and salary information for a player from Spotrac website as
    of 2024. Only stats after 2011 are available."""
    # Step 1. Get players ID on Spotrac.
    player_name = player.lower().replace(' ', '+')

    page = urllib.request.urlopen(f"https://www.spotrac.com/search?q={player_name}")
    soup = BeautifulSoup(page, "html.parser")
    rows = soup.find_all("a", class_="list-group-item")

    if len(rows) > 0:
        id = rows[0]['href'].split('/')[-1]
        players_page = f"https://www.spotrac.com/nba/player/statistics/_/id/{id}"
    else:
        players_page = f"https://www.spotrac.com/search?q={player_name}"

    # Step 2. Get salaries.
    page = urllib.request.urlopen(players_page)

    soup = BeautifulSoup(page, "html.parser")
    rows = soup.find_all("tr", class_="")
    earnings = []
    header_met = False
    for row in rows:
        r = row.text.replace(' ', '').split()
        if r == ['Year', 'Team(s)', 'Age', 'Base', 'Signing', 'Incentives', 'CashTotal', 'CashCumulative']:
            header_met = True
        if r == ['Years', 'Team', 'Base', 'Signing', 'Incentives', 'CashCumulative']:
            header_met = False
        if header_met:
            earnings.append(r)

    columns = ['Year', 'Age', 'BaseSalary', 'CashTotal', 'CashCumulative']
    new_columns = ['Year', 'Age', 'BaseSalary']
    salaries = pd.DataFrame(earnings[1:], columns=columns)
    salaries = salaries.drop(salaries[salaries['Year'].astype(int) < 2011].index)
    salaries = salaries[new_columns]
    salaries = salaries.reset_index(drop=True)

    salaries['BaseSalary'] = salaries['BaseSalary'].apply(clean_salary_entries)

    # Step 3. Get stats.
    rows = soup.find_all("tr", class_="")
    statistics = []
    header_met = False
    for row in rows:
        r = row.text.replace(' ', '').split()
        if r == ['Year', 'Team', 'GP', 'GS', 'Min/Gm', 'Pt/Gm', 'Reb/Gm', 'Ast/Gm', 'Stl/Gm', 'Blk/Gm', 'FG%', '3PT%', 'FT%']:
            header_met = True
        if header_met: # Spotrac doesn't provide 'games started' info for 2011 and 2012.
            if r[0] in ['2011', '2012']:
                r.insert(3, 'n/a')
            statistics.append(r)

    statistics = pd.DataFrame(statistics[1:], columns=statistics[0])

    current_team_abrv = statistics['Team'].values.copy()[0]
    is_active = True if statistics['Year'].values[0] == '2024' else False

    statistics = statistics.drop(statistics[statistics['Year'].astype(int) == 2024].index)
    statistics = statistics.iloc[::-1].reset_index(drop=True)

    # Join stats and salaries into one table.
    statistics['Age'] = salaries['Age'].values
    statistics['BaseSalary'] = salaries['BaseSalary'].values
    final_columns = ['Year', 'Age', 'Team', 'GP', 'GS', 'Min/Gm', 'Pt/Gm', 'Reb/Gm', 'Ast/Gm', 'Stl/Gm', 'Blk/Gm', 'FG%', '3PT%', 'FT%', 'BaseSalary']
    statistics = statistics[final_columns]

    # Save stats to file.
    csv_file_name = f"{player.replace(' ', '_')}.csv"
    statistics.to_csv(f"out_data/{csv_file_name}")

    # Step 4. Get players info.
    rows = soup.find_all("div", class_="row m-0 mt-0 pb-3")
    information = []
    for row in rows:
        r = row.text.split('/n')[0].split('\n')
        information.append(r)
    information = [info for info in information[0] if info != '']

    players_info = ['Team: ' + information[0], information[2], information[3], information[5], current_team_abrv, is_active]

    # Save to file.
    file_name = f"{player.replace(' ', '_')}.txt"
    with open(f"out_data/{file_name}", "w") as output:
        for row in players_info:
            output.write(str(row) + '\n')    
