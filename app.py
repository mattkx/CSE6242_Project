import json
from flask import Flask, render_template, jsonify, request

from data_processing import *

app = Flask(__name__)
app.config.update(
    DEBUG=False,
)

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@app.route('/project_info', methods=['GET', 'POST'])
def project_info():
    return render_template('project_info.html')
    
@app.route('/map_view', methods=['GET', 'POST'])
def map_view():
   
    return render_template('project.html')

@app.route('/demand', methods=['GET'])
def demandModel():
    argsDict = dict(request.args)  #this is how to access the input args in dict form
    
    #for station in stations:
    demand = getDemand(argsDict)
    print(demand)
    orderedListOfStations = getNeo4JRoute(demand)
    print(orderedListOfStations)
    # at this point you have a list of stations in order of which to reallocate first
    #change next call from random list to the list of stations
    response = jsonify({'data':orderedListOfStations})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response
if __name__ == '__main__':
    app.run()
