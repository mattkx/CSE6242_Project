import pandas as pd
import pickle
#from sklearn.ensemble import AdaBoostRegressor
from py2neo import Graph
import itertools
import re

#citibike = Graph("bolt://localhost:7687", auth=("neo4j", "<password>"))
citibike = Graph("neo4j+s://7417a683.databases.neo4j.io", auth=("neo4j", "7RKgGJvTQDrha88nsBG_6Qg4m7roIh7UYXtD2eE9T-8"))
def getDemand(args):
    demand = {}
    df_station = pd.read_csv('stations.csv')
    stations = df_station['start_station_id'].unique().tolist()
    filename = 'finalized_model.sav'
    model = pickle.load(open(filename, 'rb'))
    cleanedArgs = {'hour': int(args['hour']), 'AVG_WIND':float(args['avgwind']), 'PRECIP':float(args['precipitation']), 'SNOW_TOTAL':float(args['snow']), 'MAX_TEMP':float(args['temp']), 'Month': int(args['month']),'DayOfWeek_Saturday':int(args['saturday']), 'DayOfWeek_Sunday':int(args['sunday'])}
    print(cleanedArgs)
    for station in stations:
        X_test = pd.DataFrame([cleanedArgs])
        X_test['start_station_id'] = station
        print(X_test)
        ypred = model.predict(X_test)
        rowdict = {station:ypred}
        demand.update(rowdict)
   
    demand10 = sorted(demand, key=demand.get, reverse=True)[:10]
    
    return demand10
def f(l, n):
    return  [l[i:i+n] for i in range(len(l) - n + 1)] 
def split_ids(df):
    return re.findall("\((.*?)\)", df)

def getNeo4JRoute(demand):
    #demand = demand10
   
    trips = f(demand,2)
    listoftrips = []
    for stations in trips:
        start = str(stations[0])
        stop = str(stations[1])
    
        query_string = '''
        MATCH (s1:station) where id(s1) = '''+str(start)+'''
    MATCH (s2:station) where id(s2) = '''+str(stop)+'''
    CALL apoc.algo.dijkstra(s1, s2, 'NEAR', 'distance') YIELD path, weight
    RETURN path, weight
    
    '''
    
        results = citibike.run(query_string).to_data_frame()
        listoftrips.append(results)
    
    alltrips = pd.concat(listoftrips)
    alltrips['path'] = alltrips['path'].astype(str)
    alltrips['ids'] = alltrips['path'].apply(split_ids)
    routelist = alltrips.ids.sum()
    routelist_final = list(dict.fromkeys(routelist))    
    alltrips.to_csv('trips.csv', index = False)
    return routelist_final

