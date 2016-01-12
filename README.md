# universal-search-recommendation

Universal Search recommendation server.

[![Build Status](https://travis-ci.org/mozilla/universal-search-recommendation.svg?branch=master)](https://travis-ci.org/mozilla/universal-search-recommendation) [![Coverage Status](https://coveralls.io/repos/mozilla/universal-search-recommendation/badge.svg?branch=master&service=github)](https://coveralls.io/github/mozilla/universal-search-recommendation?branch=master) [![Requirements Status](https://requires.io/github/mozilla/universal-search-recommendation/requirements.svg?branch=master)](https://requires.io/github/mozilla/universal-search-recommendation/requirements/?branch=master)

## Methodology

This recommendation service is intended to return a suggested search result—and additional metadata for it—for an incomplete search string. Following: a walkthrough of the methodology using the search term "the mar", an in-process search where the user is looking for information about the film [The Martian](http://www.imdb.com/title/tt3659388/).

First, we want to determine the user's intended search from the in-process search string. We do that by passing the query to a search suggestion engine. That engine might respond with the following suggestions:

```json
[
  "the martian",
  "the martian trailer",
  "the martian movie",
  "the martian book",
  "the marion star",
  "the mary sue"
]
```

We'll take top of those, `the martian`, and perform a search on that using a full search engine API:

```json
{
  "abstract": "Directed by Ridley Scott. With Matt Damon, Jessica Chastain, Kristen Wiig, Kate Mara. During a manned mission to Mars, Astronaut Mark Watney is presumed dead after a ...",
  "clickurl": "http://www.imdb.com/title/tt3659388/",
  "date": "",
  "dispurl": "www.imdb.com/title/tt3659388",
  "title": "<b>The Martian</b> (2015) - IMDb",
  "url": "http://www.imdb.com/title/tt3659388/"
}
```

Using the data from that search result, we then run it through a series of classifiers. Each of these attempt to match and enhance results with data from additional sources.

An IMDb enhancer might recognize that the above result is a movie from IMDb and add the following data:

```json
{
  "date": "2 October 2015",
  "genre": [
     "Adventure",
     "Drama",
     "Sci-Fi"
  ],
  "rating": {
    "actual": 8.2,
    "max": 10
  },
  "credits": {
    "acting": [
      "Matt Damon",
      "Jessica Chastain",
      "Kristen Wiig"
    ],
    "directing": [
      "Ridley Scott"
    ],
    "writing": [
      "Drew Goddard",
      "Andy Weir"
    ]
  }
}
```

Summed up, the response from the API would look like this:

```json
{
  "enhancements": {
    "imdb": {
      "date": "2 October 2015",
      "genre": [
         "Adventure",
         "Drama",
         "Sci-Fi"
      ],
      "rating": {
        "actual": 8.2,
        "max": 10
      },
      "credits": {
        "acting": [
          "Matt Damon",
          "Jessica Chastain",
          "Kristen Wiig"
        ],
        "directing": [
          "Ridley Scott"
        ],
        "writing": [
          "Drew Goddard",
          "Andy Weir"
        ]
      }
    }
  },
  "query": {
    "completed": "the martian",
    "original": "the mar"
  },
  "result": {
    "abstract": "Directed by Ridley Scott. With Matt Damon, Jessica Chastain, Kristen Wiig, Kate Mara. During a manned mission to Mars, Astronaut Mark Watney is presumed dead after a ...",
    "title": "The Martian (2015) - IMDb",
    "url": "http://www.imdb.com/title/tt3659388/"
  }
}
```

## Local development

**Prerequisites**: [memcached v1.4.25](http://memcached.org/), [libmemcached 1.0.18](http://libmemcached.org/libMemcached.html), [python 3.5.1](https://www.python.org/), [virtualenv](https://virtualenv.readthedocs.org/en/latest/)

To install:

```sh
git clone https://github.com/mozilla/universal-search-recommendation.git
cd universal-search-recommendation
mkvirtualenv universal-search-recommendation  # You may need to set --python to point to the python 3.5 executable.
pip install -r requirements.txt
```

To run the server:

```sh
source .env
python server.py
```


### Configuration

Some environment variables are required. Each of those are contained within `.env.dist`, which should be renamed to `.env` and populated before developing:

- `YAHOO_OAUTH_KEY`: an OAuth key with access to Yahoo's [BOSS Search API](https://developer.yahoo.com/boss/search/).
- `YAHOO_OAUTH_SECRET`: the secret for the key contained in `YAHOO_OAUTH_KEY`.

Additional confuration can be done by setting these optional environment variables:

- `RECOMMENDATION_ENV`: the environment in which the server is being run. Options: `development`, `staging`, `testing`, `production`. Default: `development`.
- `RECOMMENDATION_HOST`: the host at which you'd like the server to run. Default: `0.0.0.0`
- `RECOMMENDATION_PORT`: the port at which you'd like the server to listen. Default: `5000`
- `MEMCACHED_HOST`: the host at which memcached is listening. Default: `127.0.0.1`


### Testing

To run the test suite:

```sh
nosetests
```
