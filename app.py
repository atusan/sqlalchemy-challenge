#homework
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement


app = Flask(__name__)

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        "Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    session = Session(engine)
    last_day = session.query(func.max(Measurement.date)).first()
    first_day = last_day - dt.timedelta(days=365)
    
    prc_results = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date > first_day).\
        order_by(Measurement.date).all()
    session.close()   
    data = []
    for date,prcp in prc_results:
        row = {}
        row['date'] = date
        row['prcp'] = prcp
        data.append(row)
    return jsonify(data)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_num = session.query(Measurement.station).group_by(Measurement.station).all()
    session.close()
    data = []
    for station in station_num:
        row = {}
        row['station'] = station
        data.append(row)
    return jsonify(data)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    last_day = session.query(func.max(Measurement.date)).first()
    first_day = last_day - dt.timedelta(days=365)
    tob_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date > first_day).\
        order_by(Measurement.date).all()
    session.close()

    data = []
    for date,tobs in tob_results:
        row = {}
        row["date"] = date
        row["tobs"] = tobs
        data.append(row)
    return jsonify(data)

@app.route("/api/v1.0/<start>")
def trip_start(start):
    end_date = dt.datetime.strptime(start, '%Y-%m-%d')
    # end_date = dt.datetime.strftime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start_date = end_date-last_year

    session = Session(engine)
    trip_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    trip = list(np.ravel(trip_results))
    session.close()

    return jsonify(trip)

@app.route("/api/v1.0/<start>/<end>")
def trip_start_end(start,end):
    end_date = dt.datetime.strptime(start, '%Y-%m-%d')
    last_year = dt.timedelta(days=365)
    start_date = end_date-last_year

    session = Session(engine)
    trip_results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date<=end_date).all()
    trip = list(np.ravel(trip_results))
    session.close()

    return jsonify(trip)

if __name__ == '__main__':
    app.run(debug=True)
