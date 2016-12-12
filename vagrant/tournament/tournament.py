#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#
import psycopg2

ALL_RESULTS = "ALL"
ONE_RESULT = "ONE"
NO_RESULTS = "NONE"


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def executeQuery(results, statement, data=None, data2=None):
    """
    This function abstracts the different pieces required by
    psycopg2 and allows execution of a SQL command
    """
    conn = connect()
    cursor = conn.cursor()

    if data and data2:
        cursor.execute(statement, ((data, ), (data2, )))
    elif data:
        cursor.execute(statement, (data, ))
    else:
        cursor.execute(statement)

    if results == ALL_RESULTS:
        result = cursor.fetchall()
    elif results == ONE_RESULT:
        result = cursor.fetchone()
    else:
        result = None

    conn.commit()
    cursor.close()
    conn.close()

    return result


def deleteMatches():
    """Remove all the match records from the database."""
    executeQuery(NO_RESULTS, "TRUNCATE TABLE matches;")


def deletePlayers():
    """Remove all the player records from the database."""
    executeQuery(NO_RESULTS, "TRUNCATE TABLE players CASCADE;")


def countPlayers():
    """Returns the number of players currently registered."""
    result = executeQuery(ONE_RESULT, "SELECT COUNT(*) FROM players;")
    return result[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    statement = "INSERT INTO players (name) VALUES (%s);"
    executeQuery(NO_RESULTS, statement, name)


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a player
    tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    """
    Joins 2 subtables, one with rows containing id/name/win and the other
    containing the id/name/ loss pair to get the id/name/wins/matches
    """
    statement = """
    SELECT win.id, win.name, win.wins, (win.wins+loss.losses) as matches
    FROM
    (SELECT players.id, players.name, COUNT(matches.winner) as wins
    FROM players LEFT JOIN matches
    ON players.id = matches.winner
    GROUP BY players.id) win
    LEFT JOIN
    (SELECT players.id, players.name, COUNT(matches.loser) as losses
    FROM players LEFT JOIN matches
    ON players.id = matches.loser
    GROUP BY players.id) loss
    ON win.id = loss.id
    ORDER BY win.wins;
    """

    standings = executeQuery(ALL_RESULTS, statement)
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """

    statement = """
    INSERT INTO matches (winner, loser) VALUES (%s, %s);
    """

    executeQuery(NO_RESULTS, statement, winner, loser)


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    num_players = countPlayers()
    if num_players == 0 or num_players % 2 != 0:
        return None

    # Get the current player standings to determine the pairing
    standings = playerStandings()

    pairings = []

    # Loop through standings 2 at a time and pair each player with the next one
    for index in xrange(0, len(standings), 2):
        p1 = standings[index]
        p2 = standings[index+1]
        pairings.append((p1[0], p1[1], p2[0], p2[1]))

    return pairings



