# Peller.Tech Test Polls web application

This is a test challenge for Peller.Tech interviewing process.  
Based on python and aiohttp webserver.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

* Python 3.8.1

### Installing

* get project files from github  
`git clone https://github.com/eugeny-m/peller_tech_polls.git`  
`cd peller_tech_polls`
* create python environment  
`python3.8 -m venv venv`
* activate venv  
`source venv/bin/activate`
* install requirements  
`pip install -U pip`  
`pip install -r requirements.txt`
* create config file with postgres credentials, example in `config/polls.yaml`
* create database in postgres manually with name from config file (database)  
`CREATE DATABASE <database> ENCODING 'UTF8'`  
or uncomment 133 line `# setup_db(USER_CONFIG['postgres'])` in init_db.py  
if you have default postgres setup
* init db  
`python init_db.py --config '/path/to/config/file.yaml'`

## Running

* run app  
`python main.py --config '/path/to/config/file.yaml'`
* check in your webbrowser  
`http://127.0.0.1:8080`  
`http://127.0.0.1:8080/admin`

## Built With

* [Python 3.8.1](https://www.python.org)
* [aiohttp 3.6.2](https://github.com/aio-libs/aiohttp)
* [bootstrap](https://getbootstrap.com)
* [PostgreSQL 12](https://www.postgresql.org)

## Authors

* **Eugeny Maksimov** -  [eugeny-m](https://github.com/eugeny-m)  
