# API server

## Running

(from project root)
```bash
python3 -m rating_server
```

or, as a Docker microservice:
```bash
docker-compose up rating_server
```
The latter will run flask server in production environment using gunicorn .

## API reference

#### GET /companies

returns the list of companies with details and associated rating:
```json
{
    "companies": [
        {
            "account": "MorganStanley",
            "name": "Morgan Stanley",
            "number_of_tweets": 711,
            "profile_image_url":     "http://pbs.twimg.com/profile_images/767759044849336328/99u_IE90_normal.jpg",
            "score": 0.3120140646976077
        },
        {
          "account": "FedEx",
          "name": "FedEx",
          "number_of_tweets": 1366,
          "profile_image_url": "http://pbs.twimg.com/profile_images/816343288982728705/QN7Xl9NG_normal.jpg",
          "score": 0.24676120058565112
        },
    ]
}
```

where ```score``` is a numerical value of company's customer satisfaction rating in the range of [-1.0, 1.0]

#### GET /company/{account}/length

Returns number of tweets analyzed mentioning @account

```json
{
    "length": 711
}
```

#### GET /company/{account}

Returns tweet ids stored for company in the order of them being added

#### GET /company/{account}/best

Returns most positive tweets mentioning @account

```json
{
  "ids": [
    "846216294651346944",
    "846445243973222402"
  ]
}
```

#### GET /company/{account}/worst

Returns most negative tweets mentioning @account

```json
{
  "ids": [
    "846443801447219200",
    "846650243756253184",
  ]
}
```
