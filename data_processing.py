import pandas as pd
import pickle
#from sklearn.ensemble import AdaBoostRegressor
from py2neo import Graph
import itertools
import re

#citibike = Graph("bolt://localhost:7687", auth=("neo4j", "<password>"))
citibike = Graph("neo4j+s://7417a683.databases.neo4j.io", auth=("neo4j", "7RKgGJvTQDrha88nsBG_6Qg4m7roIh7UYXtD2eE9T-8"))
args = {}
args['hour'] = 16
args['avgwind'] = 6.71
args['precipitation'] = 0.09
args['snow'] = 0
args['temp'] = 65
args['month'] = 12
args['saturday'] = 0
args['sunday'] = 0
def getDemand(args):
    #demand = {}
    df_station = pd.read_csv('stations.csv')
    stations = df_station['start_station_id'].unique().tolist()
    filename = 'finalized_model.sav'
    model = pickle.load(open(filename, 'rb'))
    cleanedArgs = {'hour': int(args['hour']), 'AVG_WIND':float(args['avgwind']), 'PRECIP':float(args['precipitation']), 'SNOW_TOTAL':float(args['snow']), 'MAX_TEMP':float(args['temp']), 'Month': int(args['month']),'DayOfWeek_Saturday':int(args['saturday']), 'DayOfWeek_Sunday':int(args['sunday'])}
    testlist = []
    print(cleanedArgs)
    for station in stations:
        X_test_ = pd.DataFrame([cleanedArgs])
        X_test_.insert(0, 'start_station_id', station)
        #print(X_test)
        #X_test = scaler.fit_transform(X_test1)
        testlist.append(X_test_)
    X_test = pd.concat(testlist)
    X_test = X_test[['hour', 'start_station_id', 'AVG_WIND', 'PRECIP', 'SNOW_TOTAL', 'MAX_TEMP', 'Month',
             'DayOfWeek_Saturday', 'DayOfWeek_Sunday']]   
    ypred = model.predict(X_test)
    demand = X_test[['start_station_id']]
    demand['counts'] = ypred.tolist()
    demand =  demand.sort_values(['counts'], ascending=[False])
    demand10 = demand[['start_station_id']].head(10)
    demand10 = demand10.to_list()
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
        results['start'] = start
        results['stop'] = stop
        listoftrips.append(results)
    
    alltrips = pd.concat(listoftrips)
    alltrips['path'] = alltrips['path'].astype(str)
    alltrips['ids'] = alltrips['path'].apply(split_ids)
    routelist = alltrips.ids.sum()
    routelist_final = list(dict.fromkeys(routelist))    
    alltrips.to_csv('trips.csv', index = False)
    return routelist_final

