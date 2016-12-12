# Tournament

This application depicts a swiss style tournament using postgres to store data and python to manipulate the data

## Getting Started

### Prerequisites

Please make sure that the items below are installed

* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads) 

### Installing

* Clone or download the repository
* Change directories to the vagrant directory
* Run the command below and wait for it to finish (this may take some time depending on your connection)
```sh
vagrant up
```
* Run the command below to log into the machine 
```sh
vagrant ssh
```

* Change directories to the tournament directory
```sh
cd /vagrant/tournament
``` 

* Run the command below to create the database and the required tables
```sh
psql -f tournament.sql
```

* Run the tournament tests file using the command below
```python
python tournament_test.py
```

## Built With

* [Python](https://www.python.org/) - Language used
* [Postgres](https://www.postgresql.org/) - Relational database used

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The team at Udacity for their intro to relational databases course and their assistance
* StackOverflow