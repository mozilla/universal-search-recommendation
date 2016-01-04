from pylibmc import Client

import conf


memcached = Client([conf.MEMCACHED_HOST])
