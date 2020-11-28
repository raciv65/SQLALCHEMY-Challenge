# Set up dependemncies
from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

## Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect



###############################################################
# Database Setup
###############################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base=automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

## Save references to each table
Measurement=Base.classes.measurement
Station=Base.classes.station

#################################################################
# Flask Setup
#################################################################

app=Flask(__name__)

#################################################################
# Flask Routes
#################################################################

#Home page and list all routes

@app.route("/")
def home():
    #List all available api routes.
    return  (
        f'<h1>Available Routes</h1>'
        f'''
        <ul>
        <p>
            <li>/api/v1.0/precipitation</li></li>
        </p>
        <p>
            <li>/api/v1.0/stations</li>
        </p>
        <p>
            <li>/api/v1.0/tobs</li>
        </p>
        <p>
            <li>/api/v1.0/&lt;start&gt;             (i.e. /api/v1.0/2016-08-01)</li>
        </p>
        <p>
            <li>/api/v1.0/&lt;start&gt;/&lt;end&gt; (i.e. /api/v1.0/2016-08-01/2017-05-15)</li>
        </p>
        </ul>
        '''

    )

#/api/v1.0/precipitation
#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    ## Calculate the date 1 year ago from the last data point in the database
    last_day=(
         session
        .query(Measurement.date)
        .order_by(Measurement.date.desc())
        .first()
    )
#auxiliar to calculate the last 12 months (a year or 365 days)
    target=dt.datetime.strptime(last_day[0],'%Y-%m-%d')-dt.timedelta(days=365)
    
    #Query
    query_target=(
    session
    .query(Measurement.date, func.avg(Measurement.prcp))
    .filter(Measurement.date>=target)
    .group_by(Measurement.date).all()
    )

    #Close session of the data base
    session.close()

#auxiliar to make a dict for jsonify
    List_Precipation=[]    

    for date, prcp in query_target:
        dictionary={}
        dictionary[date]=round(prcp,2)
        List_Precipation.append(dictionary)


    #Return JSON
    return jsonify(List_Precipation)

#/api/v1.0/stations
#Return a JSON list of stations from the dataset
@app.route("/api/v1.0/stations")
def station():
    session=Session(engine)
#Query
    query_station=(
    session
    .query(Station.name, Measurement.station)
    .filter(Measurement.station==Station.station)
    .group_by(Measurement.station).all()
    )

#Close the session
    session.close()
##auxiliar to make a dict for jsonify

    List_Station=[]
    for name, station in query_station:
        dic_Station={}
        dic_Station['Station']=station
        dic_Station['Name']=name

        List_Station.append(dic_Station)

    #Return JSON
    return jsonify(List_Station)
    
#/api/v1.0/tobs
#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year
@app.route("/api/v1.0/tobs")
def temperature():
    session=Session(engine)
    ## Calculate the date 1 year ago from the last data point in the database
    last_day=(
         session
        .query(Measurement.date)
        .order_by(Measurement.date.desc())
        .first()
    )
    #auxiliar to calculate the last 12 months (a year or 365 days)
    target=dt.datetime.strptime(last_day[0],'%Y-%m-%d')-dt.timedelta(days=365)

    #Query to the most active station
    query_stationMostActive=(
    session
    .query(Station.name, Measurement.station, func.count(Measurement.station))
    .filter(Measurement.station==Station.station)
    .group_by(Measurement.station)
    .order_by(func.count(Measurement.station).desc()).limit(1).all()
    )
    #Query of temperature observations (TOBS) for the previous year
    query_temperatute=(
        session
        .query(Measurement.station, Measurement.date, Measurement.tobs)
        .filter(Measurement.station==query_stationMostActive[0][1])
        .filter(Measurement.date>=target).all()
    )
    
     #Close the session
    session.close() 
    ##auxiliar to make a dict for jsonify

    List_Temper=[]
    for station, date, temp in query_temperatute:
        dic_Temper={}
        dic_Temper[date]=temp
        List_Temper.append(dic_Temper)

   
    #Return JSON   
    return jsonify(
        Station=f'{query_stationMostActive[0][0]}',
        Temperature=List_Temper
        )
    

#/api/v1.0/<start>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date
@app.route("/api/v1.0/<start>")
def temperature_range_start(start):
    session=Session(engine)

    #Transform in data type
    start=dt.datetime.strptime(start,'%Y-%m-%d')

    query_start=(
        session
        .query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
        .filter(Measurement.date >= start)
        .group_by(Measurement.date).all()
    )

     #Close the session
    session.close()

 ##auxiliar to make a dict for jsonify

    List_TemperStart=[]
    for date, min, avg, max in query_start:
        dic_TemperStart={}
        dic_TemperStart['Date']=date
        dic_TemperStart['Temp Min']=round(min,2)
        dic_TemperStart['Tem Avg']=round(avg,2)
        dic_TemperStart['Temp Max']=round(max,2)
        List_TemperStart.append(dic_TemperStart)

   
    #Return JOSN
    return jsonify(List_TemperStart)

#/api/v1.0/<start>/<end>
#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def temperature_range_start_end(start, end):
    session=Session(engine)

    #Transform in data type
    start=dt.datetime.strptime(start,'%Y-%m-%d')
    end=dt.datetime.strptime(end,'%Y-%m-%d')

    query_start_end=(
        session
        .query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs))
        .filter(Measurement.date >= start)
        .filter(Measurement.date <= end)
        .group_by(Measurement.date).all()
    )

    #Close the session
    session.close()
    #auxiliar to make a dict for jsonify

    List_TemperStartEnd=[]
    for date, min, avg, max in query_start_end:
        dic_TemperStartEnd={}
        dic_TemperStartEnd['Date']=date
        dic_TemperStartEnd['Temp Min']=round(min,2)
        dic_TemperStartEnd['Tem Avg']=round(avg,2)
        dic_TemperStartEnd['Temp Max']=round(max,2)
        List_TemperStartEnd.append(dic_TemperStartEnd)

    
    #Return JOSN
    return jsonify(List_TemperStartEnd)
    session.close()


if __name__ == '__main__':
    app.run(debug=True)