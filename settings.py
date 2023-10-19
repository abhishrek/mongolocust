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
            'COLLSTATS_WEIGHT': 1,
            }

def init_defaults_from_env():
    for key in DEFAULTS.keys():
        value = os.environ.get(key)
        if value:
            DEFAULTS[key] = value

# get the settings from the environment variables
init_defaults_from_env()
