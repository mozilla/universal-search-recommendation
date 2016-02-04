# API

The recommendation server provides a single API endpoint that, given a partial search string, will attempt to complete that search and make a destination recommendation.


## Request

GET requests should be made to the root of the server with a single querystring parameter containing the query:

```bash
GET http://universal-search.dev/?q=the%20mart
```

## Response Status

The HTTP status code will tell you about the status of the request:

* `200` - request successfully received, successfully returned recommendation. The response body will contain the recommendation.
* `202` - request successfully received, but the recommendation was not contained in cache. The response body will contain an empty object literal.
* `400` - the request did not contain a query.
* `500` - application error. If running in `DEBUG` mode, details about the exception will be contained in the response body.


## Response Body

If the status code indicates that a recommendation has been returned, the response body will contain that recommendation following this general form:

```json
{
  "enhancers": {
    "wikipedia": {"...": "..."},
    "omdb": {"...": "..."}
  },
  "query": {
    "completed": "the martian",
    "original": "the mart"
  },
  "result": {
    "abstract": "Directed by Ridley Scott. With Matt Damon, Jessica Chastain, Kristen Wiig, Kate Mara. During a manned mission to Mars, Astronaut Mark Watney is presumed dead after a...",
    "title": "The Martian (2015) - IMDb",
    "url": "http://www.imdb.com/title/tt3659388/"
  }
}
```

There will always be three keys in the root object:

* `enhancers` will be an object containing [context-specific metadata](#enhancers) for the destination recommendation provided in `result`.
* `query` will be an object containing information about the text of the query itself:
    * `original` will be a string containing the original query, as passed in the request.
    * `completed` will be a string containing the query, as completed.
* `result` includes basic information about a destination recommendation for the completed result:
    * `abstract` will be a string containing a short textual overview of the recommendation.
    * `title` will be a string containing a title for the recommendation.
    * `url` will be a string containing a URL for the recommendation.


### Enhancers

The server will identify the recommendation as belonging to a zero or more special classes of results. For each class it belongs to, additional metadata will be included in the `enhancers` object of the response. If none apply, `enhancers` will be an empty object.


#### `domain`

If the `result` is the root of a hostname (i.e. there is no path), the `domain` classifier is applied:

```json
{
  "enhancers": {
    "domain": {
      "fqdn": "https://www.imdb.com/",
      "logo": "https://logo.clearbit.com/www.imdb.com"
    }
  },
  "query": {"...": "..."},
  "result": {"...": "..."}
}
```

* `fqdn` will be a string containing the fully qualified domain name of the result.
* `logo` will be a string containing a prospective URL to a logo for the domain, as returned by [Clearbit's Logo API](https://clearbit.com/docs#logo-api). This is not guaranteed to be a valid image.


#### `embedly`

In three cases:

* The recommended destination is the root of a hostname.
* The recommended destination is a top-level directory on a hostname.
* The recommended destination is a Wikipedia article.

an `embedly` classifier is applied.

```json
{
  "enhancers": {
    "embedly": {
      "favicon": {
        "colors": [
          {
            "color": [247, 247, 247],
            "weight": 0.4558105469
          },
          {
            "color": [29, 29, 29],
            "weight": 0.1066894531
          }
        ],
        "url": "https://i.embed.ly/1/image?url=https%3A%2F%2Fen.wikipedia.org%2Fstatic%2Ffavicon%2Fwikipedia.ico&key=11ecbb09b10d4f8cb59beb77741c7105"
      },
      "image": {
        "caption": null,
        "height": 330,
        "size": 19375,
        "url": "https://i.embed.ly/1/image?url=https%3A%2F%2Fupload.wikimedia.org%2Fwikipedia%2Fen%2Fthumb%2Fc%2Fcd%2FThe_Martian_film_poster.jpg%2F220px-The_Martian_film_poster.jpg&key=11ecbb09b10d4f8cb59beb77741c7105",
        "width": 220
      }
    }
  },
  "query": {"...": "..."},
  "result": {"...": "..."}
}
```

* `favicon` will be an object containing information about the `result`'s favicon:
    * `colors` will be an array of prominent colors in the favicon, each containing
        * `color`, a fixed-length array representing the `[r, g, b]` values of that color
        * `weight`, a float representing the relative prominence of that color on a `0.0`
 to `1.0` scale.
    * `url` will be a string containing an Embedly-proxied URL to the favicon.
* `images` will be an object containing information about a key image for the `result`:
    * `caption` will be a string containing any known caption for the key image.
    * `height` will be an integer representing the height of the key image, in pixels.
    * `size` will be an integer representing the file size of the key image, in bytes.
    * `url` will be a string containing an Embedly-proxied URL to the image.
    * `width` will be an integer representing the width of the key image, in pixels.


#### `wikipedia`

If the `result` is a Wikipedia article, the `wikipedia` classifier is applied.

```json
{
  "enhancers": {
    "wikipedia": {
      "abstract": "The Martian is a 2015 American science fiction film directed by Ridley Scott and starring Matt Damon. The film is based on Andy Weir's 2011 novel The Martian, which was adapted into a screenplay by Drew Goddard. Damon stars as an astronaut who is mistakenly presumed dead and left behind on Mars. The film depicts his struggle to survive and others' efforts to rescue him. The film's ensemble cast also features Jessica Chastain, Kristen Wiig, Jeff Daniels, Michael Pe\u00f1a, Kate Mara, Sean Bean, Sebastian Stan, Aksel Hennie, and Chiwetel Ejiofor.\nProducer Simon Kinberg began developing the film after 20th Century Fox optioned the novel in March 2013. Drew Goddard adapted the novel into a screenplay and was initially attached to direct, but the film did not move forward. Scott replaced Goddard, and with Damon in place as the main character, production was approved. Filming began in November 2014 and lasted approximately 70 days. Approximately 20 sets were built on a sound stage in Budapest, Hungary, one of the largest in the world. Wadi Rum in Jordan was also used as a practical backdrop for filming.\nThe film premiered at the 2015 Toronto International Film Festival on September 11, 2015. 20th Century Fox released the film in theaters in the United States on October 2, 2015. The film was released in 2D, 3D, IMAX 3D and 4DX. The film received positive reviews and has grossed over $598 million worldwide, becoming Scott's highest-grossing film to date, as well as the tenth-highest-grossing film of 2015. It received several accolades, including the Golden Globe Award for Best Motion Picture \u2013 Musical or Comedy, and seven Academy Award nominations, including Best Picture and Best Adapted Screenplay for Goddard. For his performance, Damon received several awards nominations, including the Academy Award for Best Actor, the BAFTA for Best Actor, the Critic's Choice Award for Best Actor, and he won the Golden Globe for Best Actor in a Musical or Comedy.",
      "slug": "The_Martian_(film)",
      "title": "The Martian (film)"
    }
  },
  "query": {"...": "..."},
  "result": {"...": "..."}
}
```

* `abstract` will be a string containing a short abstract of the Wikipedia article.
* `slug` will be a string containing the Wikipedia article's URL slug.
* `title` will be a string containing the Wikipedia article's title.
