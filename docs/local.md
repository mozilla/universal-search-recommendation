# Local Development

A multiple-container Docker configuration is maintained to support local development.


## Architecture

`universal-search-recommendation` is built as a containerized Docker application, but to run it, several additional services are required:

- a [Memcached](http://memcached.org/) cache backend
- a [Celery](http://www.celeryproject.org/) task queue
- a [Redis](http://redis.io/) broker for the task queue

A [Compose](https://docs.docker.com/compose/) configuration is included to streamline setup and management of those services for local development. They are run alongside the application container on a single [Docker Machine](https://docs.docker.com/machine/overview/) VM.


## Usage

A `./server` utility script is included to streamline use of the Docker containers.


### First-time setup

First, run the following script:

```bash
./server init
```

This creates a host VM called `universal-search-dev`. Then, it configures a consistent hostname ([universal-search.dev](http://universal-search.dev/)) for local development (requires `sudo`).

You will need to [install Docker Toolbox](https://www.docker.com/products/docker-toolbox) and configure your shell. The script will walk you through it.


### Configuration

Some environment variables are required. Each of those are contained within `.env.dist`, which should be copied to `.env` and populated as appropriate.

- `BING_ACCOUNT_KEY` - account key for Bing's [Web Search API](http://datamarket.azure.com/dataset/bing/searchweb).
- `EMBEDLY_API_KEY` - an API key to access Embedly's [Extract API](http://embed.ly/extract).
- `YAHOO_OAUTH_KEY` and `YAHOO_OAUTH_SECRET` - authentication credentials for Yahoo's [BOSS Search API](https://developer.yahoo.com/boss/search/).


### Development

Finally, you're ready to go. The `./server` script has a number of additional commands to help out.

- `./server start` - builds and starts the application server and supporting services.
- `./server stop` - kills and removes the application container, then stops the supporting services.
- `./server restart` - runs `./server stop`, then `./server start`.

You can also start, stop, or restart the app or service containers individually:

- `./server start app`
- `./server stop app`
- `./server restart app`
- `./server start services`
- `./server stop services`
- `./server restart services`

