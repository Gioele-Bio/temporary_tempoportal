from dash import callback, html, dash_table, dcc, Input, Output, State, MATCH
import fakeredis
import hashlib
import io
import json
import os
import pandas as pd
import plotly
import redis
import warnings


class redis_store:
    """Save data to Redis using the hashed contents as the key.
    Serialize Pandas DataFrames as memory-efficient Parquet files.

    Otherwise, attempt to serialize the data as JSON, which may have a
    lossy conversion back to its original type. For example, numpy arrays will
    be deserialized as regular Python lists.

    Connect to Redis with the environment variable `REDIS_URL` if available.
    Otherwise, use FakeRedis, which is only suitable for development and
    will not scale across multiple processes.
    """
    # THIS NEEDS TO BE CHANGED TO VARIABLE OF USER BEING LOGGED IN! !!! 
    # from flask_login import current_user (then current user.email)
    # if current_user != None:
    if 'REDIS_URL' in os.environ:
        r =  redis.StrictRedis.from_url(os.environ["REDIS_URL"])
    else:
        warnings.warn('Using FakeRedis - Not suitable for Production Use.')
        r = fakeredis.FakeStrictRedis()

    # Hash object
    @staticmethod
    def _hash(serialized_obj):
        return hashlib.sha512(serialized_obj).hexdigest()

    # Save object in redis store based on type, return key
    @staticmethod
    def save(value):
        # If it is a df, digest it and save it as parquet
        if isinstance(value, pd.DataFrame):
            buffer = io.BytesIO()
            value.to_parquet(buffer, compression='gzip')
            buffer.seek(0)
            df_as_bytes = buffer.read()
            hash_key = redis_store._hash(df_as_bytes)
            type = 'pd.DataFrame'
            serialized_value = df_as_bytes
        # If it is not, just encode it as json dump
        else:
            serialized_value = json.dumps(value, cls=plotly.utils.PlotlyJSONEncoder).encode('utf-8')
            hash_key = redis_store._hash(serialized_value)
            type = 'json-serialized'

        redis_store.r.set(
            f'_dash_aio_components_value_{hash_key}',
            serialized_value
        )
        redis_store.r.set(
            f'_dash_aio_components_type_{hash_key}',
            type
        )
        return hash_key

    # Load data from the store!
    @staticmethod
    def load(hash_key):
        data_type = redis_store.r.get(f'_dash_aio_components_type_{hash_key}')
        serialized_value = redis_store.r.get(f'_dash_aio_components_value_{hash_key}')
        try:
            # If it is a df, read it w pandas
            if data_type == b'pd.DataFrame':
                value = pd.read_parquet(io.BytesIO(serialized_value))
            # Else unpack json dump
            else:
                value = json.loads(serialized_value)
        except Exception as e:
            print(e)
            print(f'ERROR LOADING {data_type - hash_key}')
            raise e
        return value
