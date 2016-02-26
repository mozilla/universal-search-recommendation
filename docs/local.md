## Local Development

A multiple-container Docker configuration is maintained to support local development.


### Configuration

Some environment variables are required. Each of those are contained within `.env.dist`, which should be copied to `.env` and populated as appropriate.


### Services

`universal-search-recommendation` requires several additional services: a [Memcached](http://memcached.org/) cache backend, a [Celery](http://www.celeryproject.org/) task queue, and a [Redis](http://redis.io/) Celery backend. A [Compose](https://docs.docker.com/compose/) configuration is included to streamline setup and management of those services.


#### Set up Docker host.

The first time you set up the services, you must create the Docker host.

- [Install Docker Toolbox](https://www.docker.com/products/docker-toolbox).
- Create a Docker host:

```bash
docker-machine create --driver virtualbox universal-search-dev
```

- Add an entry to your `hosts` file:

```bash
sudo sh -c "echo $(docker-machine ip universal-search-dev 2>/dev/null) universal-search.dev >> /etc/hosts"
```


#### Start services.

After the host is set up, you can run each service by:

```
docker-machine start universal-search-dev
eval $(docker-machine env universal-search-dev)
docker-compose up -d
```

To verify that each service is up, run:

```bash
docker-compose ps
```

In the output you should see containers named `recommendation_memcached_1`, `recommendation_redis_1`, and `recommendation_worker_1`. The state for each of these should be `Up`.


### Application

`universal-search-recommendation` is managed as a Docker container that is separately built from the services, but run on the same host as the services.

To build it:

```bash
docker build -t universal-search-recommendation .
```

To run it:

```bash
docker run -d -e "RECOMMENDATION_SERVICES=`docker-machine ip universal-search-dev`" -p 80:8000/tcp universal-search-recommendation
```

To verify that the application is running:

```bash
docker ps --filter ancestor="universal-search-recommendation"
```

You should see one container running, and its status should begin with `Up`.


### Usage

If the application and services are all running, you should be able to access to access the recommendation server at [http://universal-search.dev](http://universal-search.dev). After making changes to the application, you will need to stop it:

```bash
docker stop $(docker ps --filter ancestor="universal-search-recommendation" --format="{{.ID}}")
```

Then rebuild and start it back up, per above.
