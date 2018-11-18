# Import Dependencies
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
from flask import Flask, jsonify
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################
# Create an engine for the chinook.sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect hawaii database into a new model
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save references to the invoices and invoice_items tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
         f"<strong>Available Routes:</strong><br/>"
         
         f"/api/v1.0/precipitation<br/>"
         f"- Dates and Temperature Observations from last year<br/>"
         
         f"/api/v1.0/stations<br/>"
         f"- List of weather stations from the dataset<br/>"

         f"/api/v1.0/tobs<br/>"
         f"- List of temperature observations (tobs) from the previous year<br/>"

         f"/api/v1.0/<start><br/>"
         f"- List of min, avg, and max temperature for a given start date<br/>"
        
         f"/api/v1.0/<start>/<end><br/>"
         f"- List of min, avg, and max temperature for a given start/end range<br/>"
    )
    
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary"""
    # Query Invoices for Billing Country
    precipitation = session.query(Measurement.date, func.avg(Measurement.tobs)).\
    group_by(Measurement.date).all()
    tobs_list = []
    for tobs in precipitation:
        tobs_dict = {}
        tobs_dict[tobs[0]] = round(tobs[1])
        tobs_list.append(tobs_dict)

    return jsonify(tobs_list)
    
@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset """
    # Query all stations
    stations = session.query(Station.name).all()
    station_list = list(np.ravel(stations))
    
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of Temperature Observations (tobs) for the previous year """
    # Query for all temperature observations from previous year
    tobs = session.query(Measurement.tobs).\
    filter(Measurement.date.between('2017-01-01', '2017-12-31')).all()
    
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start_temp(start):
    """Return a json list of the minimum temperature, the average temperature, 
    and the max temperature for a given start."""
    TMIN = session.query(func.min(Measurement.tobs)).\
           filter(Measurement.date == start).all()
    TMAX = session.query(func.max(Measurement.tobs)).\
           filter(Measurement.date == start).all()
    TAVG = session.query(func.avg(Measurement.tobs)).\
           filter(Measurement.date == start).all()
    result = TMIN, TMAX, TAVG
    temp_list = list(np.ravel(result))
    temp_dist = {'TMIN':temp_list[0], 'TMAX':temp_list[1], 'TAVG':temp_list[2]}
    
    return jsonify(temp_dist)
    
@app.route("/api/v1.0/<start>/<end>")
def start_end(start=None, end=None):
    """Return a JSON list of the minimum temperature, the average temperature, 
    and the max temperature for a given start or start-end range."""
    TMIN = session.query(func.min(Measurement.tobs)).\
           filter(Measurement.date.between(start, end)).all()
    TMAX = session.query(func.max(Measurement.tobs)).\
           filter(Measurement.date.between(start, end)).all()
    TAVG = session.query(func.avg(Measurement.tobs)).\
           filter(Measurement.date.between(start, end)).all()
    result = TMIN, TMAX, TAVG
    temp_list = list(np.ravel(result))
    temp_dist = {'TMIN':temp_list[0], 'TMAX':temp_list[1], 'TAVG':temp_list[2]}
    
    return jsonify(temp_dist)

if __name__ == '__main__':
    app.run()