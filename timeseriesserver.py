import os
import json
import pandas as pd
import arrow
import atexit
from flask import Flask, send_from_directory, render_template, request
from Utils.Util1 import response
from Utils.Util1 import readJsonFile
from Utils.Util1 import exitReg
from Utils.Util1 import validateISOTS
from Utils.Util1 import validateTSOrder
from Utils.Util1 import getDetailData
from Utils.Util1 import bgProcessing
from Utils.Util1 import ReadData



# init
cfg = {}
# eventsdata = pd.DataFrame(columns=['eventID', 'fileRef', 'timestart', 'epochstart', 'timeend', 'epochend'])
eventmodes = {
    "lifespan": {
        "start": ["birth", "start"],
        "end": ["death", "end"]
    }
}

atexit.register(exitReg)

# del old pickle file
if os.path.exists("eventsdata.pkl"):
    os.remove("eventsdata.pkl")



# read pd data
readDataObj = ReadData()




# read configurations
cfg = readJsonFile('data.json')

# start locker - to avoid repeat starts

runTimeConfig = {
    "startLock": False
}



app = Flask(__name__, template_folder='UI', static_folder=os.path.join("UI", "assets"), static_url_path='/assets')

@app.route('/timeline/filter/time')
def timelinetimefilter():
    # define response data
    data = {}
    message = "Hello API"
    statusCode = 200

    query = request.args
    filterdata = {}
    proceedKey = True

    print(readDataObj.eventsdata.head())
    
    # validate timestamp
    if ( proceedKey and "start" in query and not validateISOTS(query['start']) ):
        proceedKey = False
        message = """Invalid timestamp format for start query (passed: """ + query['start'] + """)."""
        data['Correct-format'] = """YYYY-MM-DDTH:M:S"""
        data['Valid-examples'] = """2021-09, 2021-09-01, 2021-09-01T10, 2021-09-01T10:00:00"""
        data['Note'] = """YYYY-MM are mandatory ones"""
        statusCode = 400

    if ( proceedKey and "end" in query and not validateISOTS(query['end']) ):
        proceedKey = False
        message = """Invalid timestamp format for start query (passed: """ + query['start'] + """)."""
        data['Correct-format'] = """YYYY-MM-DDTH:M:S"""
        data['Valid-examples'] = """2021-09, 2021-09-01, 2021-09-01T10, 2021-09-01T10:00:00"""
        data['Note'] = """YYYY-MM are mandatory ones"""
        statusCode = 400

    if ( proceedKey and "start" in query and "end" in query and not validateTSOrder(query['start'], query['end']) ):
        proceedKey = False
        message = """start timestamp cannot be greater than end time. Check if you have exchanged start and end time filters."""
        statusCode = 400

    if ( proceedKey ):
        filterdata = readDataObj.readPData()
        #filter start
        if ("start" in query):
            startfilter = arrow.get(query['start']).to('Asia/Calcutta').timestamp()
            filterdata = filterdata[(filterdata.epochstart >= startfilter) | (filterdata.epochstart.isnull())]
            if ("end" in query):
                # filter out exceeding dates of start from filter
                endfilter = arrow.get(query['end']).to('Asia/Calcutta').timestamp()
                filterdata = filterdata[(filterdata.epochstart <= endfilter) | (filterdata.epochstart.isnull())]

        #filter start
        if ("end" in query):
            endfilter = arrow.get(query['end']).to('Asia/Calcutta').timestamp()
            filterdata = filterdata[(filterdata.epochend <= endfilter) | (filterdata.epochend.isnull())]
            if ("start" in query):
                startfilter = arrow.get(query['start']).to('Asia/Calcutta').timestamp()
                filterdata = filterdata[(filterdata.epochend >= startfilter) | (filterdata.epochend.isnull())]

        retData = []
        for index, row in filterdata.iterrows():
            retData.append(getDetailData(row['eventID'], row['fileRef'], cfg['config']['datafolder']))

        data['events'] = retData
        

        # filterdata = data[(data.epochstart < -9340790400) & (data.epochend > -9143452801)]
    # data['filter'] = filterdata
    

    # send response
    return response(data, message, statusCode), statusCode

@app.route('/timeline')
def timeline():
    return render_template('index.html')

@app.route('/start')
def startinit():
    # define response data
    data = {}
    message = "Hello API"
    statusCode = 200

    if not runTimeConfig["startLock"]:
        try:
            # start bg threads
            data["started Threads"] = bgProcessing()
            message = "started server"
            runTimeConfig["startLock"] = True
            statusCode = 202
        except Exception as e:
            message = "error occured on server side"
            data['error'] = str(e)
    else:
        message = "server has already started to process"
        statusCode = 406
        

    # send response
    return response(data, message, statusCode), statusCode

@app.route('/')
def hello_world():
    # define response data
    data = {}
    message = "Hello API"
    statusCode = 200

    # send response
    return response(data, message, statusCode), statusCode

if __name__ == '__main__':
   app.run(host='0.0.0.0',port=8000,debug=True)