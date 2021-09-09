from flask import jsonify
import json
import re
import os
import glob
import arrow
import sched
import time
import timeit
from pathlib import Path
import threading
import pandas as pd

def bgProcessing():
    # init thread to run in bg

    threadsList = {}


    # read data
    ReadDataObj = ReadData()
    threadsList["readingThread"] = threading.Thread(target=ReadDataObj.startReading, args=(), daemon=True)

    # processing data
    ProcessDataObj = ProcessData()
    threadsList["processingThread"] = threading.Thread(target=ProcessDataObj.startProcessing, args=(), daemon=True)

    # start processing tasks / threads
    for t in threadsList:
        threadsList[t].start()

    return list(threadsList.keys())

def exitReg():
    print("exiting server!") 



def response(data={}, message="", statusCode=200):
    retData = {
        "message": message,
        "data": data,
        "statusCode": statusCode
    }
    return jsonify(retData)

def readJsonFile(filename):
    with open(filename, 'r') as jfl:
        fldata = jfl.read()
        return json.loads(fldata)

def writeJsonFile(filename, jsondata):
    with open(filename, 'w') as jfl:
        json.dump(jsondata, jfl)

def detTimeKeys(keys, evtmode):
    timekeys = {}
    for key in keys:
        for pkey in evtmode:
            if key in evtmode[pkey]:
                # timekeys[pkey] = evtmode[pkey].index(key)
                timekeys[pkey] = key
                break
    return timekeys

def validateISOTS(ts):
    regex = r"^([\+-]?\d{4}(?!\d{2}\b))((-?)((0[1-9]|1[0-2])(\3([12]\d|0[1-9]|3[01]))?|W([0-4]\d|5[0-2])(-?[1-7])?|(00[1-9]|0[1-9]\d|[12]\d{2}|3([0-5]\d|6[1-6])))([T\s]((([01]\d|2[0-3])((:?)[0-5]\d)?|24\:?00)([\.,]\d+(?!:))?)?(\17[0-5]\d([\.,]\d+)?)?([zZ]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?)?)?$"
    if (re.match(regex, ts)):
        # validate minimum YYYY-MM
        regex = r"[0-9]{2,4}-[0-9]{2}"
        return re.match(regex, ts)
    else:
        return False

def validateTSOrder(start, end):
    startep = arrow.get(start).to('Asia/Calcutta').timestamp()
    endep = arrow.get(end).to('Asia/Calcutta').timestamp()
    return startep <= endep

def getDetailData(id, file, datafolder="data"):
    seldata = readJsonFile(os.path.join(datafolder, file))
    if id in seldata:
        # insert id
        seldata[id]['id'] = id
        return seldata[id]
    else:
        return {}


class ProcessData:
    def __init__(self):
        self.configData = readJsonFile("data.json")
        self.eventmodes = {
            "lifespan": {
                "start": ["birth", "start"],
                "end": ["death", "end"]
            }
        }
        self.s = sched.scheduler(time.time, time.sleep)
        

    def setHumanlyTimeInFile(self, file):
        # read file
        evtdata = readJsonFile(file)

        # loop through events and update relative - hummanly time
        for evt in evtdata:
            if "time" in evtdata[evt]:
                for spanType in evtdata[evt]['time'][evtdata[evt]['type']]:
                    # get time to local arrowformat
                    localtim = arrow.get(evtdata[evt]['time'][evtdata[evt]['type']][spanType]["ts"]).to('Asia/Calcutta')
                    # update time
                    evtdata[evt]['time'][evtdata[evt]['type']][spanType]["humanly"] = localtim.humanize()
                    
        # write back to file
        writeJsonFile(file, evtdata)

    def updateDataFiles(self):
        # from JSON to files
        # loop through files list and remove unexist / duplicates
        processedfiles = []
        gnamelist = list(self.configData['files'].keys())
        for gname in gnamelist:
            filepath = os.path.join(self.configData['config']['datafolder'], self.configData['files'][gname]['file'])
            if not os.path.exists(filepath):
                self.configData['unextfiles'][gname] = self.configData['files'][gname]['file']
                del self.configData['files'][gname]
            elif os.path.exists(filepath):
                if self.configData['files'][gname]['file'] not in processedfiles:
                    processedfiles.append(self.configData['files'][gname]['file'])
                else:
                    del self.configData['files'][gname]
        writeJsonFile("data.json", self.configData)

        # from files to JSON
        # exclude the ones starting with underscore _ -> they are examples or helpers
        datapath = self.configData['config']['datafolder'] + "/[!_]*json"
        files = glob.glob(datapath)
        for file in files:
            print("processing : ", file)
            gname = Path(file)

            self.setHumanlyTimeInFile(file)

            if gname.stem not in self.configData['files']:
                self.configData['files'][gname.stem] = {
                    "type": "group",
                    "file": gname.name
                }
                if gname.name in self.configData["unextfiles"]:
                    del self.configData["unextfiles"][gname.name]
            else:
                # nothing as of now - decide later
                pass

            writeJsonFile("data.json", self.configData)

    def _startProcessing(self, sc):
        self.updateDataFiles()
        self.s.enter(10, 1, self._startProcessing, (sc,))
        pass

    def startProcessing(self):
        self.s.enter(1, 1, self._startProcessing, (self.s,))
        self.s.run()

class ReadData:
    def __init__(self):
        self.eventsdata = pd.DataFrame(columns=['eventID', 'fileRef', 'timestart', 'epochstart', 'timeend', 'epochend'])
        self.cfgfile = "data.json"
        self.eventmodes = {
            "lifespan": {
                "start": ["birth", "start"],
                "end": ["death", "end"]
            }
        }
        self.s = sched.scheduler(time.time, time.sleep)

    def readData(self):
        # read configuration
        cfg = readJsonFile(self.cfgfile)

        if os.path.exists("eventsdata.pkl"):
            self.eventsdata = pd.read_pickle("eventsdata.pkl")

        # read actual data
        for eventfile in cfg['files']:
            # defined only type group
            if (cfg['files'][eventfile]['type'] == "group"):
                # read the sub file
                evtdata = readJsonFile(os.path.join(cfg['config']['datafolder'], cfg['files'][eventfile]['file']))

                # loop through the events and add to dataframe
                for evt in evtdata:
                    if ("time" in evtdata[evt]):
                        # time entry exist - proceed for extraction
                        if (evtdata[evt]['type'] in self.eventmodes):
                            # define the start and end keys
                            startendkey = detTimeKeys(evtdata[evt]['time'][evtdata[evt]['type']].keys(), self.eventmodes[evtdata[evt]['type']])
                            times = {
                                "start": None,
                                "epochstart": None,
                                "end": None,
                                "epochend": None
                            }

                            # set start and end value which ever applicable
                            if "start" in startendkey:
                                times['start'] = evtdata[evt]['time'][evtdata[evt]['type']][startendkey['start']]["ts"]

                                tm = arrow.get(times['start'])
                                local = tm.to('Asia/Calcutta')
                                times['epochstart'] = float(local.timestamp())
                                # reference for rev conversion if negative
                                #datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=(-10725091200))
                            if "end" in startendkey:
                                times['end'] = evtdata[evt]['time'][evtdata[evt]['type']][startendkey['end']]["ts"]

                                tm = arrow.get(times['end'])
                                local = tm.to('Asia/Calcutta')
                                times['epochend'] = float(local.timestamp())

                            # update old data entry or insert new data entry
                            existingEntry = self.eventsdata.loc[self.eventsdata['eventID']==evt].index.tolist()
                            updateIndex = None if len(existingEntry)<=0 else existingEntry[0]
                            if updateIndex is None:
                                updateIndex = len(self.eventsdata.index)
                            # self.eventsdata.drop(self.eventsdata.loc[self.eventsdata['eventID']==evt].index, inplace=True)
                            self.eventsdata.loc[updateIndex] = [evt, cfg['files'][eventfile]['file'], times['start'], times['epochstart'], times['end'], times['epochend']]
            else:
                raise Exception("Invalid eventfile type: " + cfg['files'][eventfile]['type'])


    def _startReading(self, sc):
        self.readData()
        self.eventsdata.head(20)
        self.eventsdata.to_pickle("eventsdata.pkl")
        print("done processing (_startReading): rescheduling in 10 sec")
        self.s.enter(10, 1, self._startReading, (sc,))

    def startReading(self):
        self.s.enter(1, 1, self._startReading, (self.s,))
        self.s.run()

    def readPData(self):
        pkldata = pd.read_pickle("eventsdata.pkl")
        return pkldata