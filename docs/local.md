# Local Development

A multiple-container Docker configuration is maintained to support local development.


## First-time setup

A few steps are required the first time

- [Install Docker Toolbox](https://www.docker.com/products/docker-toolbox).
- Some environment variables are required. Each of those are contained within `.env.dist`, which should be copied to `.env` and populated as appropriate.
- Create a Docker host:

```bash
docker-machine create --driver virtualbox universal-search
```

- Add an entry to your hosts file:

```bash
sudo sh -c "echo $(docker-machine ip universal-search 2>/dev/null) universal-search.dev >> /etc/hosts"
```


## Start machine and containers

The machine and containers can then be started at any time:

```bash
docker-machine start universal-search
eval $(docker-machine env universal-search)
docker-compose up
```

While `docker-compose up` is running, the recommendation server may be accessed at [http://universal-search.dev](http://universal-search.dev).


## Architecture

An nginx server is the entry point, acting as a reverse proxy to forward requests to a Python container running uWSGI, which manages the application server. Memcached, Celery, and Redis containers run parallel; used for caching, as a task queue, and as a backend for the task queue, respectively.
