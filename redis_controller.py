import redis


def get_redis_connection(host, port, password):

    redis_pool = redis.ConnectionPool(
            host=host,
            port=port,
            password=password
        )

    return redis.Redis(
        connection_pool=redis_pool,
        charset="utf-8"
    )
