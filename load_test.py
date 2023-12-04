from locust import between
from locust_plugins import constant_total_ips
from mongo_user import MongoUser, mongodb_task
from settings import DEFAULTS

import pymongo
import random
import math

# preset string of len 501. Used to generate random text
STR = '8oqws3EKxNXol1ksDuRIXCPyuDspQKQhQsV1yY00NEAzQmptCJd5DVNcC6RNARWQvzKUTgiYZnmhdxhEuyuses9ZIFLUQSbwm3wPWwLigaVGYiOMcEksxT4zp16wTR5bctuRZ0KfJgFAs3jEjtycmCoReNCft1k6XLcds6ek9PdcmrukMqL7HWw05OTT1ofz8UysTZar1ugRNmGFW6NTkyS5Xb32rWZIMA6xP8iDZObVe9q8A032H3KbrpPq25pcPkk031RlixirJE9eXy9Uwvhsg1WlYRjJKntPpGPNTCekOCR4i38hjJAfxLsGWSonAycQUUEBMlO2OeysuGjLWGxODp8YgDVMW1ksbLiUFutvuiooYpQqZwQZO29s5dT21nSLzqMNzasmUv5U7lDztHezawOETvZTxPBZESYkUdrwA4dQtH08uXQgY5qZBsRoQA0Q4HstZqWGJaNtd7kvJKaIVQBh9OkYSbOQsbmUTFRLmkcNr3GY1'

class MongoSampleUser(MongoUser):
    """
    Generic sample mongodb workload generator
    """
    # no delays between operations
    wait_time = constant_total_ips(int(DEFAULTS['TPS']))

    def __init__(self, environment):
        super().__init__(environment)

    # [0 to maxVal)     maxVal not included
    def get_rand(self, maxVal):
        return math.floor(random.random() * maxVal)
        
    def generate_new_document(self, collId):
        """
        Generate a new sample document
        """
        assert collId < DEFAULTS['NUM_COLLECTIONS'], "Wrong Collection ID in generate_new_document " + str(collId)
        s1 = self.get_rand(450)
        s2 = self.get_rand(450)
        s3 = self.get_rand(450)
        s4 = self.get_rand(450)
        l1 = self.get_rand(50)
        l2 = self.get_rand(50)
        l3 = self.get_rand(50)
        l4 = self.get_rand(50)
        document = {
            'first_name': STR[s1 : s1 + l1],
            'last_name':  STR[s2 : s2 + l2],
            'address':    STR[s3 : s3 + l3],
            'city':       STR[s4 : s4 + l4],
            'assets':   self.get_rand(10000000),
            'expenses': self.get_rand(1000000),
            'ticker':   self.get_rand(100000),
        }
        return document

    def on_start(self):
        """
        Executed every time a new test is started - place init code here
        """
        # prepare the collections
        indexes = [
            pymongo.IndexModel([('first_name', pymongo.ASCENDING)]),
            pymongo.IndexModel([('last_name', pymongo.DESCENDING)]),
            pymongo.IndexModel([('address', pymongo.ASCENDING)]),
            pymongo.IndexModel([('city', pymongo.DESCENDING)]),
            pymongo.IndexModel([('assets', pymongo.ASCENDING)]),
            pymongo.IndexModel([('expenses', pymongo.DESCENDING)]),
            pymongo.IndexModel([('ticker', pymongo.ASCENDING)])
        ]

        for collId in range(DEFAULTS['NUM_COLLECTIONS']):
            collName = DEFAULTS['COLLECTION_PREFIX'] + '_' + str(collId)
            self.collections[collId] = self.ensure_collection(collId, collName, indexes)

    @mongodb_task(weight=int(DEFAULTS['INSERT_WEIGHT']))
    def insert_single_document(self):
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)
        document = self.generate_new_document(collId)
        result = self.collections[collId].insert_one(document)

        # update the cache if FIND or UPDATE op is also enabled
        if DEFAULTS['FIND_WEIGHT'] + DEFAULTS['UPDATE_WEIGHT'] != 0:
            if len(self.cache[collId]) < DEFAULTS['DOCS_TO_CACHE']:
                self.cache[collId].append(result.inserted_id)
            else:
                if random.randint(0, 9) == 0:
                    self.cache[collId][random.randint(0, len(self.cache[collId]) - 1)] = result.inserted_id

    @mongodb_task(weight=int(DEFAULTS['FIND_WEIGHT']))
    def find_document(self):
        # select a random collection
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)

        # at least one insert needs to happen
        if not self.cache[collId]:
            if random.randint(0, 10000) == 0:
                print('Empty Cache. Cannot perform "Find" op')
            return

        # find a random document using an index
        cached_val = random.choice(self.cache[collId])
        query = {'_id': cached_val }
        self.collections[collId].find_one(query)

    @mongodb_task(weight=int(DEFAULTS['BULK_INSERT_WEIGHT']), batch_size=int(DEFAULTS['DOCS_PER_BATCH']))
    def insert_documents_bulk(self):
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)
        self.collections[collId].insert_many(
            [self.generate_new_document(collId) for _ in
             range(int(DEFAULTS['DOCS_PER_BATCH']))])

    @mongodb_task(weight=int(DEFAULTS['UPDATE_WEIGHT']))
    def udpate_single_document(self):
        # select a random collection
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)

        # at least one insert needs to happen
        if not self.cache[collId]:
            if random.randint(0, 10000) == 0:
                print('Empty Cache. Cannot perform "Update" op')
            return

        # find a random document
        k = self.get_rand(len(self.cache[collId]))
        cached_val = self.cache[collId][k]

        # generate a new document that will update the old value
        document = self.generate_new_document(collId)

        # udpate the document
        newValues = { "$set": document }
        query = {'_id': cached_val }
        self.collections[collId].update_one(query, newValues)

    @mongodb_task(weight=int(DEFAULTS['DELETE_WEIGHT']))
    def delete_document(self):
        # select a random collection
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)

        res = self.collections[collId].delete_one({})
        if res.deleted_count == 0:
            print('Delete failed')

    @mongodb_task(weight=int(DEFAULTS['COLLSTATS_WEIGHT']))
    def cmd_coll_stats(self):
        collId = random.randint(0, DEFAULTS['NUM_COLLECTIONS']-1)
        collName = DEFAULTS['COLLECTION_PREFIX'] + '_' + str(collId)        
        print(self.db.command('collStats', collName))

    @mongodb_task(weight=int(DEFAULTS['DBSTATS_WEIGHT']))
    def cmd_db_stats(self):
        print(self.db.command('dbStats'))
