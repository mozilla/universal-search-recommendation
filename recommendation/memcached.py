from memcache import Client

from recommendation import conf


memcached = Client([conf.MEMCACHED_HOST])
