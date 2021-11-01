from dbconn import *
import pandas as pd
import os
import time
#from py2neo import Graph, Node, Relationship
conn = dbconn(uri="neo4j+s://7417a683.databases.neo4j.io", user="neo4j", pwd="7RKgGJvTQDrha88nsBG_6Qg4m7roIh7UYXtD2eE9T-8")

#conn.query("CREATE OR REPLACE DATABASE citibikedb")

#nodefile = 'data\\nodes.csv'
#edgefile = 'data\\edges.csv'

#nodes = pd.read_csv(nodefile)
df = pd.read_csv('https://storage.googleapis.com/cse6242_project_ggallagher6/2014.csv')
df_stations = df.drop_duplicates(subset = ['start_station_id','end_station_id'])

##Code to ensure station node is unique###
conn.query('CREATE CONSTRAINT station_id IF NOT EXISTS ON (s:station) ASSERT s.id IS UNIQUE')

def insert_data(query, rows, batch_size = 10000):
    # Function to handle the updating the Neo4j database in batch mode.
    
    total = 0
    batch = 0
    start = time.time()
    result = None
    
    while batch * batch_size < len(rows):

        res = conn.query(query, 
                         parameters = {'rows': rows[batch*batch_size:(batch+1)*batch_size].to_dict('records')})
        total += res[0]['total']
        batch += 1
        result = {"total":total, 
                  "batches":batch, 
                  "time":time.time()-start}
        print(result)
        
    return result


def add_station(rows, batch_size=10000):
    # Adds author nodes to the Neo4j graph as a batch job.
    query = '''
            UNWIND $rows AS row
            MERGE (:station {id: row.start_station_id})
            RETURN count(*) as total
            '''
    return insert_data(query, rows, batch_size)


add_station(df_stations[['end_station_id']])
df_stations.to_csv('stations.csv')

df_stations.head()

def add_trips(rows, batch_size=10000):
   # Adds paper nodes and (:Author)--(:Paper) and 
   # (:Paper)--(:Category) relationships to the Neo4j graph as a 
   # batch job.
 
   query = '''
   UNWIND $rows as row
   MATCH (a:station),(b:station)
   where a.id = row.start_station_id and b.id = row.end_station_id
   CREATE (a)-[r:TRIP]->(b)
   RETURN count(distinct a) as total

   '''
 
   return insert_data(query, rows, batch_size)

add_trips(df_stations[['start_station_id','end_station_id']])