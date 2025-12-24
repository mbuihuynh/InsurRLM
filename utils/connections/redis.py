import os
# from rediscluster import RedisCluster
# from redis.sentinel import Sentinel


REDIS_KAFKA_MODE = os.getenv('REDIS_KAFKA_MODE', default="cluster")

if REDIS_KAFKA_MODE == "cluster":
    from rediscluster import RedisCluster as RedisLib

elif REDIS_KAFKA_MODE == "sentinel":
    from redis.sentinel import Sentinel as RedisLib


class RedisClusterConnection():
    def __init__(self):
        self.config = dict()
        
        port = int(os.getenv('REDIS_PORT', default="6379"))
        lstHost = os.getenv('REDIS_HOST', default="localhost")

        arrClusterAddress = []
        arrClusterAddress = lstHost.split(',')
        
        nodes = [tuple(x.split(":")) for x in arrClusterAddress]
        startup_nodes = [{"host":x[0], "port":x[1]} for x in nodes]
        
        self.config.update({'cluster': startup_nodes})
        self.config.update({'password': os.getenv('REDIS_PASSWORD', default="")})

    def getConfig(self):
        return self.config

    def getConnection(self):
        redis_info = self.getConfig() 
        redis_cluster = RedisLib(startup_nodes=redis_info['cluster'], password=redis_info['password'], decode_responses=True)
        return redis_cluster
    
    def getPrefixKey(self, type):
        return self.PREFIX_KEY[type]
    
class RedisSentinelConnection():
    def __init__(self):
        self.config = dict()
        
        port = int(os.getenv('REDIS_PORT', default="6379"))
        lstHost = os.getenv('REDIS_HOST', default="localhost")

        arrSentinelHost = []
        for item in lstHost.split(','):
            sentinel = (item, port)
            arrSentinelHost.append(sentinel)

        self.config.update(
            {'redis_sentinel_host': arrSentinelHost})
        self.config.update({'service_name': os.getenv('REDIS_SERVICE_NAME', default="")})
        self.config.update({'password': os.getenv('REDIS_PASSWORD', default="")})

    def getConfig(self):
        return self.config

    def getConnection(self):
        redis_info = self.getConfig()
        sentinel = RedisLib(redis_info['redis_sentinel_host'],socket_timeout=0.2)
        master = sentinel.master_for(redis_info['service_name'], socket_timeout=0.5, password=redis_info['password'],decode_responses=True)
        return master
    
    def getPrefixKey(self, type):
        return self.PREFIX_KEY[type]
    
def getRedisConnection(redis_type):

    if redis_type == "cluster":
        return RedisClusterConnection
    
    return RedisSentinelConnection