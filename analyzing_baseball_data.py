"""
Project for Week 4 of "Python Data Analysis".
Processing CSV files with baseball stastics.

Be sure to read the project description page for further information
about the expected behavior of the program.
"""

import csv

def read_csv_as_list_dict(filename, separator, quote):
    """
    Inputs:
      filename  - name of CSV file
      separator - character that separates fields
      quote     - character used to optionally quote fields
    Output:
      Returns a list of dictionaries where each item in the list
      corresponds to a row in the CSV file.  The dictionaries in the
      list map the field names to the field values for that row.
    """
    table = []
    with open(filename, newline='') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator, quotechar=quote)
        for row in csvreader:
            table.append(row)
    return table

def read_csv_as_nested_dict(filename, keyfield, separator, quote):
    """
    Inputs:
      filename  - name of CSV file
      keyfield  - field to use as key for rows
      separator - character that separates fields
      quote     - character used to optionally quote fields
    Output:
      Returns a dictionary of dictionaries where the outer dictionary
      maps the value in the key_field to the corresponding row in the
      CSV file.  The inner dictionaries map the field names to the
      field values for that row.
    """
    table = {}
    with open(filename, newline='') as csvfile:
        csvreader = csv.DictReader(csvfile, delimiter=separator, quotechar=quote)
        for row in csvreader:
            rowid = row[keyfield]
            table[rowid] = row
    return table

##
## Provided formulas for common batting statistics
##

# Typical cutoff used for official statistics
MINIMUM_AB = 500

def batting_average(info, batting_stats):
    """
    Inputs:
      batting_stats - dictionary of batting statistics (values are strings)
    Output:
      Returns the batting average as a float
    """
    hits = float(batting_stats[info["hits"]])
    at_bats = float(batting_stats[info["atbats"]])
    if at_bats >= MINIMUM_AB:
        return hits / at_bats
    else:
        return 0

def onbase_percentage(info, batting_stats):
    """
    Inputs:
      batting_stats - dictionary of batting statistics (values are strings)
    Output:
      Returns the on-base percentage as a float
    """
    hits = float(batting_stats[info["hits"]])
    at_bats = float(batting_stats[info["atbats"]])
    walks = float(batting_stats[info["walks"]])
    if at_bats >= MINIMUM_AB:
        return (hits + walks) / (at_bats + walks)
    else:
        return 0

def slugging_percentage(info, batting_stats):
    """
    Inputs:
      batting_stats - dictionary of batting statistics (values are strings)
    Output:
      Returns the slugging percentage as a float
    """
    hits = float(batting_stats[info["hits"]])
    doubles = float(batting_stats[info["doubles"]])
    triples = float(batting_stats[info["triples"]])
    home_runs = float(batting_stats[info["homeruns"]])
    singles = hits - doubles - triples - home_runs
    at_bats = float(batting_stats[info["atbats"]])
    if at_bats >= MINIMUM_AB:
        return (singles + 2 * doubles + 3 * triples + 4 * home_runs) / at_bats
    else:
        return 0


##
## Part 1: Functions to compute top batting statistics by year
##

def filter_by_year(statistics, year, yearid):
    """
    Inputs:
      statistics - List of batting statistics dictionaries
      year       - Year to filter by
      yearid     - Year ID field in statistics
    Outputs:
      Returns a list of batting statistics dictionaries that
      are from the input year.
    """
    answer = list(filter(lambda row: row[yearid]==str(year),statistics))
    return answer


def top_player_ids(info, statistics, formula, numplayers):
    """
    Inputs:
      info       - Baseball data information dictionary
      statistics - List of batting statistics dictionaries
      formula    - function that takes an info dictionary and a
                   batting statistics dictionary as input and
                   computes a compound statistic
      numplayers - Number of top players to return
    Outputs:
      Returns a list of tuples, player ID and compound statistic
      computed by formula, of the top numplayers players sorted in
      decreasing order of the computed statistic.
    """
    player_ids = list(set(map(lambda row:row[info['playerid']],statistics)))

    batting_statistics = {}
    for row in statistics:
        if row[info['playerid']]not in batting_statistics.keys() or \
        formula(info, row) > formula (info,batting_statistics[row[info['playerid']]]):
            batting_statistics[row[info['playerid']]]=row.copy()

    tups = []
    for player in player_ids:
        tups.append( (player,formula(info,batting_statistics[player])))
        sorted_list = sorted(tups,key=lambda item: item[1],reverse=True)
    return sorted_list[:numplayers]

def lookup_player_names(info, top_ids_and_stats):
    """
    Inputs:
      info              - Baseball data information dictionary
      top_ids_and_stats - list of tuples containing player IDs and
                          computed statistics
    Outputs:
      List of strings of the form "x.xxx --- FirstName LastName",
      where "x.xxx" is a string conversion of the float stat in
      the input and "FirstName LastName" is the name of the player
      corresponding to the player ID in the input.
    """
    master_dict = read_csv_as_nested_dict(info['masterfile'],info['playerid'], \
                                          info["separator"], info["quote"])
    my_list = [None]*4
    answer = []
    for player,point in top_ids_and_stats:
        my_list[0] = "{:.3f}".format(float(point))
        my_list[1] = '---'
        my_list[2] = master_dict[player][info['firstname']]
        my_list[3] = master_dict[player][info['lastname']]
        answer.append(' '.join(my_list))
    return answer
def compute_top_stats_year(info, formula, numplayers, year):
    """
    Inputs:
      info        - Baseball data information dictionary
      formula     - function that takes an info dictionary and a
                    batting statistics dictionary as input and
                    computes a compound statistic
      numplayers  - Number of top players to return
      year        - Year to compute top statistics for
    Outputs:
      Returns a list of strings for the top numplayers in the given year
      according to the given formula.
    """
    statistics = read_csv_as_list_dict(info['battingfile'],info["separator"], info["quote"])
    my_list_year_filtered = filter_by_year(statistics,year,info['yearid'])
    top_ids_and_stats = top_player_ids(info, my_list_year_filtered, formula, numplayers)
    top_stats_year = lookup_player_names(info,top_ids_and_stats)
    return top_stats_year
def aggregate_by_player_id(statistics, playerid, fields):
    """
    Inputs:
      statistics - List of batting statistics dictionaries
      playerid   - Player ID field name
      fields     - List of fields to aggregate
    Output:
      Returns a nested dictionary whose keys are player IDs and whose values
      are dictionaries of aggregated stats.  Only the fields from the fields
      input will be aggregated in the aggregated stats dictionaries.
    """
    dict_of_dict = {}
    for row in statistics:
        if row[playerid] not in dict_of_dict.keys():
            inner_dict = {field:int(row[field]) for field in fields}
            inner_dict[playerid] = row[playerid]

            dict_of_dict[row[playerid]]= inner_dict

        else:
            exis_inner_dict = dict_of_dict[row[playerid]]
            curr_inner_dict = {field:int(row[field]) for field in fields}
            dict_combined = {field: (exis_inner_dict.get(field, 0) + \
                                     curr_inner_dict.get(field, 0)) for \
                                     field in fields}
            dict_combined[playerid]= row[playerid]

            dict_of_dict[row[playerid]]= dict_combined
    return dict_of_dict
def compute_top_stats_career(info, formula, numplayers):
    """
    Inputs:
      info        - Baseball data information dictionary
      formula     - function that takes an info dictionary and a
                    batting statistics dictionary as input and
                    computes a compound statistic
      numplayers  - Number of top players to return
    """
    stats_dict = read_csv_as_list_dict(info['battingfile'], \
                                          info["separator"], info["quote"])
    aggregate_stat = aggregate_by_player_id(stats_dict,info['playerid'],\
                                          info['battingfields'])
    statistics = list(aggregate_stat.values())
    top_ids_and_stats = top_player_ids(info, statistics, formula, numplayers)
    top_stats_career = lookup_player_names(info,top_ids_and_stats)
    return top_stats_career
