import json
from flask import Flask, render_template

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
    
    return render_template('map.html')

if __name__ == '__main__':
    app.run()
