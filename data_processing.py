import pandas as pd
import pickle
#from sklearn.ensemble import AdaBoostRegressor
from py2neo import Graph

#conn = dbconn(uri="neo4j+s://7417a683.databases.neo4j.io", user="neo4j", pwd="7RKgGJvTQDrha88nsBG_6Qg4m7roIh7UYXtD2eE9T-8")
citibike = Graph("neo4j+s://7417a683.databases.neo4j.io", auth=("neo4j", "7RKgGJvTQDrha88nsBG_6Qg4m7roIh7UYXtD2eE9T-8"))
def getDemand(args):
    demand = {}
    df_station = pd.read_csv('stations.csv')
    stations = df_station['start_station_id'].unique().tolist()
    filename = 'finalized_model.sav'
    model = pickle.load(open(filename, 'rb'))
    args = {'hour': 0, 'AVG_WIND':1.0, 'PRECIP':1.0, 'SNOW_TOTAL':0, 'MAX_TEMP':32, 'Month':1,
         'DayOfWeek_Saturday':0, 'DayOfWeek_Sunday':0}
    for station in stations:
        X_test = pd.DataFrame([args])
        X_test['start_station_id'] = station
        ypred = model.predict(X_test)
        rowdict = {station:ypred}
        demand.update(rowdict)
   
    demand10 = sorted(demand, key=demand.get, reverse=True)[:10]
    
    return demand10

def getNeo4JRoute(demand):

    
    query_string = '''
    MATCH (s1:station { name: 'Brooklyn Bridge Park - Pier 2' })
MATCH (s2:station { name: 'Rivington St & Ridge St' })
CALL apoc.algo.dijkstra(s1, s2, 'NEAR', 'distance') YIELD path, weight
RETURN path, weight

'''
    results = citibike.run(query_string)

    
    
    return routelist