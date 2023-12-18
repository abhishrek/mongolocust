import os

DEFAULTS = {'DB_NAME': 'perfdb',  
            'NUM_COLLECTIONS': 6,
            'COLLECTION_PREFIX': 'col', # collection name will be "<prefix>_<N>"
            'CLUSTER_URL': f'mongodb+srv://<user>:<pwd>@cluster_url',   # give connection string here
            
            'DOCS_TO_CACHE' : 10000,    # There is one cache per collection per thread. 
            'DOCS_PER_BATCH': 100,  # For bulk insert/update

            # Define Weifgts of your workload
            'FIND_WEIGHT': 5,
            'INSERT_WEIGHT': 5,
            'UPDATE_WEIGHT': 1,
            'DELETE_WEIGHT': 0,
            'BULK_INSERT_WEIGHT': 0,
            'COLLSTATS_WEIGHT': 0,
            'DBSTATS_WEIGHT': 0,
            
            # To achieve a particular TPS please adjust the TPS value. Setting it to -1 means there will be no delay between threads, maximizing the client's attempt to achieve the highest possible TPS.
            'TPS' : -1, 
            'CREATE_INDEX_ON_ALL_FIELD' : False # to create index on all field of collection set it to true
            }

def init_defaults_from_env():
    for key in DEFAULTS.keys():
        value = os.environ.get(key)
        if value:
            if key in ['DB_NAME', 'COLLECTION_PREFIX', 'CLUSTER_URL']:
                DEFAULTS[key] = value
            else :
                # Environment variables are being explicitly converted to integers from their string representation.
                DEFAULTS[key] = int(value)

# get the settings from the environment variables
init_defaults_from_env()
