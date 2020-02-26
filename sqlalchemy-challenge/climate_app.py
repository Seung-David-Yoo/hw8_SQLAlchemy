#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 24 21:18:21 2020

@author: yoo
"""

import numpy as np

import datetime as dt
import pandas as pd
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

#weather app
app = Flask(__name__)


data=session.query(Measurement.date).order_by(Measurement.date.desc()).first()
data=list(np.ravel(data))[0]
data=dt.datetime.strptime(data, '%Y-%m-%d')

data_year = int(dt.datetime.strftime(data, '%Y'))
data_month = int(dt.datetime.strftime(data, '%m'))
data_day = int(dt.datetime.strftime(data, '%d'))

date_oneyaer_before=dt.date(data_year, data_month, data_day)-dt.timedelta(days=365)
date_oneyaer_before = dt.datetime.strftime(date_oneyaer_before, '%Y-%m-%d')


def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()





@app.route("/")
def home():
    return (f"Station <br/>"
            f"precipitation  <br/>"
            f"Tobs <br/>"
            f"Start  <br/>"
            f"End <br/>"
            )

@app.route("/api/v1.0/tobs")
def tobs():

    results = (session.query(Measurement.date, Measurement.tobs, Measurement.station)
                      .filter(Measurement.date > date_oneyaer_before)
                      .order_by(Measurement.date)
                      .all())

    data_temp = []
    for result in results:
        tempDict = {result.date: result.tobs, "Station": result.station}
        data_temp.append(tempDict)

    return jsonify(data_temp)

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = (session.query(Measurement.date, Measurement.prcp, Measurement.station)
                      .filter(Measurement.date > date_oneyaer_before)
                      .order_by(Measurement.date)
                      .all())
    
    precipData = []
    for result in results:
        precipDict = {result.date: result.prcp, "Station": result.station}
        precipData.append(precipDict)

    return jsonify(precipData)

@app.route("/api/v1.0/stations")
def stations():
    
    
    data_station= session.query(Station.name, Station.station).all()

    return jsonify(data_station)
    

@app.route('/api/v1.0/datesearch/<start>')
def start(start):
    start_only=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)).filter(Measurement.date >date_oneyaer_before ).all()
                
    return jsonify(start_only)


@app.route('/api/v1.0/datesearch/<start>/<end>')
def startEnd(start, end):
    
    temps=calc_temps(start, end)
                    #'2012-02-28', '2012-03-05'
    date = []                       
    date_dict={'start_date':start, 'end_date':end}
    date.append(date_dict)
    date.append({'TMIN' : temps[0][0]})
    date.append({'TAVG' : temps[0][1]})
    date.append({'TMAX' : temps[0][2]})
    
    
    return jsonify(date)   
    
if __name__ == "__main__":
   app.run(debug=True)
     


