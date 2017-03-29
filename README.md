# Goal

This project aims to aggregate company customer satisfaction score based on mentions of company's account on Twitter and textual analysis.

Current implementation aggregates rating for some companies from the Fortune 500 list, and can be found [here](http://tinyurl.com/l6axna9).

# Implementation

There are 3 components to the system, implemented as independent microservices with docker:

- [Synchronization Service](sync_service/)
- [API server](rating_server/)
- Redis DB

All services and code is meant to be run from the root of the project, see details below.

# Testing

```bash
python3 -m pytest */tests/test_*.py
```

# Initialization

Before the Synchronization service can be run continuously, it has to be initialized with a list of companies:

```bash
docker-compose run sync_service python3 -m sync_service init companies.full.txt
```

This command will go through company names listed in ```companies.full.txt```,
will try to find company's Twitter account by name, and add it to the DB

# Running

```bash
docker-compose up
```

Will start the API server at ```:5000``` as well as begin fetching tweets for companies from Twitter.
