import redis
import json


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


def get_question_data(redis_conn, key):
    try:
        return json.loads(
            str(
                redis_conn.get(
                    key
                ),
                encoding='utf-8'
            )
        )
    except TypeError:
        return None


def set_question_data(redis_conn, key, data):
    redis_conn.set(
        key,
        json.dumps(data)
    )


def delete_user_cache(redis_conn, key): redis_conn.delete(key)
