import pylibmc

from recommendation import conf


memcached = pylibmc.Client([conf.MEMCACHED_HOST])
