# Deployment

## Dev Environment

The dev environment is hosted on [Amazon](https://aws.amazon.com/) [Elastic Beanstalk](https://aws.amazon.com/elasticbeanstalk/), with an [ElastiCache](https://aws.amazon.com/elasticache/)-based [memcached](http://memcached.org/) server.

In order to deploy or configure the development environment, you must have [installed](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html) and [configured](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-configuration.html#eb-cli3-credentials) the EB CLI using an account with developer permissions to the Mozilla Cloud Services VPC. If you need permissions and should have them, ask in one of the various [Universal Search communication channels](https://wiki.mozilla.org/Firefox/Universal_Search#Communication).


### Deploy

The `master` branch is deployed to an application called `universal-search-recommendation-dev`, in an environment called `us-recommendation-dev`. To configure your clone to deploy, ensure that the master branch is checked out and run:

```sh
eb init
```

At the first prompt, choose **us-west-2** as the default region.

At the second prompt, choose **universal-search-recommendation-dev** as the application to use.

Next, run:

```sh
eb use us-recommendation-dev
```

After this one-time action, deployments can be made by running:

```sh
eb deploy
```

To deploy a different branch, [additional environments may be created](http://docs.aws.amazon.com/elasticbeanstalk/latest/dg/using-features.managing.html) on the same application.


## Staging/Production Environments

Coming soon.
