##Overview of Application

The main logic of trading resides in app.py module.
All the database models and code to connect to db resides in models.py module.
Logging logic resides in logger.py module.
The actual API calls to get and trade coins is in crypto_api.py module

##Steps to run application

1. Make sure .env file is present in the files
2. In command prompt/terminal, cd to the directory where the application files are downloaded
3. When inside folder ..\pgny-interview-assessment\interview-assessment-master, run `make init`, this spins up docker containers (both db and vm with python)
4. After the init finishes running, run `python app.py` to start the application.
	a. If db connection error appears, please retry after 2 minutes, since setting network between db and vm might take some time initially.
	b. At any point, to quit the application, please use ctrl+c
	c. All the logs are written to ./storage/logs/app.py file