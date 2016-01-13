from memcache import Client

from app import conf


memcached = Client([conf.MEMCACHED_HOST])
