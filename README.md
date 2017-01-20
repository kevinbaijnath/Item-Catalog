# Item Catalog

This application depicts a swiss style tournament using postgres to store data and python to manipulate the data

## Getting Started

### Prerequisites

Please make sure that the items below are installed

* [Python](https://www.python.org/)
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

* Change directories to the catalog directory
```sh
cd /vagrant/catalog
``` 

* Run the command below to create the database and the required tables
```sh
python database_setup.py
```

* Run the command below to populate the database with course entries
```sh
python populatecourses.py
```

* Run the project file
```sh
python project.py
```

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* The team at Udacity
* Stack Overflow
