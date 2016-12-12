-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

DROP DATABASE IF EXISTS tournament;
CREATE DATABASE tournament;

\c tournament;

CREATE TABLE players (
    id        serial        PRIMARY KEY,
    name      text
);
 
CREATE TABLE matches (
    id       serial         PRIMARY KEY,
    winner   integer        REFERENCES players (id),
    loser    integer        REFERENCES players (id)
);

CREATE VIEW playerwins AS
    SELECT players.id, players.name, COUNT(matches.winner) as wins
        FROM players LEFT JOIN matches
        ON players.id = matches.winner
        GROUP BY players.id;

CREATE VIEW playerlosses AS
    SELECT players.id, players.name, COUNT(matches.loser) as losses
        FROM players LEFT JOIN matches
        ON players.id = matches.loser
        GROUP BY players.id;