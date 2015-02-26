#!/usr/bin/env python
import roslib
roslib.load_manifest("soma_geospatial_store")
import rospy
import pymongo
import math

class GeoSpatialStoreProxy():
        
    def __init__(self, db, collection):
        host = rospy.get_param('mongodb_host', 'localhost')
        port = rospy.get_param('mongodb_port', '62345')
        self._client = pymongo.MongoClient(host,port)
        self._db = db
        self._collection = collection

        # create indexes
        self._client[self._db][self._collection].ensure_index([("loc", pymongo.GEOSPHERE)])

        # self._client[self._db][self._collection].ensure_index([("uuid", 1)], 
        #                                                       unique= True,
        #                                                       sparse=True)

        # self._client[self._db][self._collection].ensure_index([("soma_id", 1),("soma_map",1),("soma_config",1)],
        #                                                       unique=True,
        #                                                       sparse=True)

        # self._client[self._db][self._collection].ensure_index([("soma_roi_id",1),("soma_map",1),("soma_config",1)], 
        #                                                       unique= True,
        #                                                       sparse=True)

                
    def insert(self, geo_json):
        return self._client[self._db][self._collection].insert(geo_json)

    def update(self, _id, geo_json):
        self.remove(_id)
        return self.insert(geo_json)

    def remove(self, _id):
        return self._client[self._db][self._collection].remove(_id)

    def find_one(self, query_json):
        return self._client[self._db][self._collection].find_one(query_json)
        
    def find(self, query_json):
        return self._client[self._db][self._collection].find(query_json)

    def find_projection(self, query_json, projection):
        return self._client[self._db][self._collection].find(query_json, projection)


    def coords_to_lnglat(self, x, y):
        earth_radius = 6371000.0 # in meters
        lng = 90 - math.degrees(math.acos(float(x) / earth_radius))
        lat = 90 - math.degrees(math.acos(float(y) / earth_radius))        
        return [lng , lat]
        
    # helper functions
    def obj_ids(self, soma_map, soma_config):
        query =  {   "soma_id": {"$exists": "true"},
                     "soma_map":  soma_map ,
                    "soma_config": soma_config
        }
        res = self.find_projection(query, {"soma_id": 1})
        ret = []
        for ent in res:
            ret.append(ent["soma_id"])
        return ret

    def roi_ids(self, soma_map, soma_config):
        query =  {  "soma_roi_id": {"$exists": "true"},
                    "soma_map":  soma_map ,
                    "soma_config": soma_config
                }
        res = self.find_projection(query, {"soma_roi_id": 1})
        ret = []
        for ent in res:
            ret.append(ent["soma_roi_id"])
        return ret

    def type_of_obj(self, soma_id, soma_map, soma_config):
        query =  { "soma_id": soma_id,
                   "soma_map":  soma_map ,
                   "soma_config": soma_config
        }
        res = self.find_projection(query, {"type": 1})
        if res.count() == 0:
            return None
        return res[0]['type']

    def type_of_roi(self, soma_roi_id, soma_map, soma_config):
        query =  { "soma_roi_id": soma_roi_id,
                   "soma_map":  soma_map ,
                   "soma_config": soma_config
        }
        res = self.find_projection(query, {"type": 1})
        if res.count() == 0:
            return None
        return res[0]['type']

        
    def geom_of_obj(self, soma_id, soma_map, soma_config):
        query =  { "soma_id": soma_id,
                   "soma_map":  soma_map ,
                   "soma_config": soma_config
        }
        res = self.find_projection(query, {"loc": 1})
        if res.count() == 0:
            return None
        return res[0]['loc']

        
    def geom_of_roi(self, roi_id, soma_map, soma_config):
        query =  { "soma_roi_id": roi_id,
                   "soma_map":  soma_map ,
                   "soma_config": soma_config
        }
        res = self.find_projection(query, {"loc": 1})
        if res.count() == 0:
            return None
        return res[0]['loc']
        
    def geom_of_trajectory(self, uuid):
        query =  { "uuid": uuid}
        res = self.find_projection(query, {"loc": 1})
        if res.count() == 0:
            return None
        return res[0]['loc']
