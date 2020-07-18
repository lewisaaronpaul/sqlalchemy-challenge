import numpy as np
import datetime as dt
# Import flask
from flask import Flask, jsonify
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

# Initialize the Base object using the automap_base in order to refelect the database.
from sqlalchemy.ext.automap import automap_base
Base = automap_base()

#################################################
# Database Setup
#################################################

# We need an engine connected to the hawaii.sqlite database.
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Refection of hawaii.sqlite database.
# Use the prepare method on the Base object create a refection of the entire database.
Base.prepare(engine, reflect=True)

# Let's create reference to the ORM objects.
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
# The app factory
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Step 2 - Climate App<br/>"
        f"The available Routes:<br/>"
        f"<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"/api/v1.0/<start><br/>"
        f"  For example: /api/v1.0/2017-01-25<br/>"
        f"<br/>"
        f"/api/v1.0/<start>/<end><br/>"
        f"  For example: /api/v1.0/2011-06-09/2017-12-23"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session link for Python to interact with the hawaii.sqlite database.
    session = Session(engine)

    """Returns the list of all precipitation measurements"""

    # Perform query on the Measurement ORM object.
    # Create a dictionary using date and prcp as keys.
    prcp_query = session.query(Measurement.date, Measurement.prcp).order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from each row data and append to the precipitation_list.
    precipitation_list = []
    for date, prcp in prcp_query:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        # Building precipitation_list during each loop.
        precipitation_list.append(precipitation_dict)

    return jsonify(precipitation_list)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session link for Python to interact with the hawaii.sqlite database.
    session = Session(engine)

    """Returns the names of all stations."""

    # Perform query on the Station ORM object.
    # Create a dictionary using station_id and name as keys.
    station_query = session.query(Station.station, Station.name).order_by(Station.station).all()

    session.close()

    # Create a dictionary from each row data and append to station_list.
    station_list = []
    for station, name in station_query:
        station_dict = {}
        station_dict["station_id"] = station
        station_dict["name"] = name
        # Building station_list during each loop.
        station_list.append(station_dict)

    return jsonify(station_list)

#########################################################
# Most active station:
# name: WAIHEE 837.5, HI US
# station: USC00519281
#########################################################

# Query the dates and temperature observations of the most active station for the last year
# of data.

@app.route("/api/v1.0/tobs")
def tobs():
    # The last 12 months of temperature observations for WAIHEE 837.5, HI US.
    temp_last_date = dt.date(2017, 8 ,18)
    temp_query_date = temp_last_date - dt.timedelta(days=365)
    # Create our session link for Python to interact with the hawaii.sqlite database.
    session = Session(engine)

    """Returns the dates and temperature observations of the most active station (WAIHEE) for the last year."""

    # Perform query on the Measurement ORM object.
    # Create a dictionary using date and temp as keys.
    temp_query = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= temp_query_date).\
        filter(Measurement.station == 'USC00519281').order_by(Measurement.date).all()

    session.close()

    # Create a dictionary from each row data and append to temp_list.
    temp_list = []
    for date, tobs in temp_query:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temp"] = tobs
        # Building temp_list during each loop.
        temp_list.append(temp_dict)

    return jsonify(temp_list)

@app.route("/api/v1.0/<start>")
def start_date(start):
    # Create our session link for Python to interact with the hawaii.sqlite database.
    session = Session(engine)

    """When given the start only date, calculate TMIN, TAVG, and TMAX for all dates 
    greater than and equal to the start date."""

    # Perform query on the Measurement ORM object.
    # Create a dictionary using date, TMIN, TAVG, and TMAX as keys.
    results = session.query(func.min(Measurement.tobs).label('TMIN'),func.max(Measurement.tobs).\
        label('TMAX'), func.avg(Measurement.tobs).label('TAVG')).filter(Measurement.date >= start).all()

    session.close()

    # Create a dictionary from each row data and append to agg_list.
    agg_list = []
    for TMIN, TMAX, TAVG in results:
        agg_dict = {}
        agg_dict["date"] = f"Greater than {start}"
        agg_dict["TMIN"] = TMIN
        agg_dict["TMAX"] = TMAX
        agg_dict["TAVG"] = round(TAVG, 2)
        # Building agg_list during each loop.
        agg_list.append(agg_dict)

    return jsonify(agg_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session link for Python to interact with the hawaii.sqlite database.
    session = Session(engine)

    """When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates 
    between the start and end date inclusive."""

    # Perform query on the Measurement ORM object.
    # Create a dictionary using date_start, date_end, TMIN, TAVG, and TMAX as keys.
    query_start_end = session.query(func.min(Measurement.tobs).label('TMIN'),func.max(Measurement.tobs).\
        label('TMAX'), func.avg(Measurement.tobs).label('TAVG'))
    result_start_end = query_start_end.filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary from each row data and append to start_end_list.
    start_end_list = []
    for TMIN, TMAX, TAVG in result_start_end:
        start_end_dict = {}
        start_end_dict["date_start"] = start
        start_end_dict["date_end"] = end
        start_end_dict["TMIN"] = TMIN
        start_end_dict["TMAX"] = TMAX
        start_end_dict["TAVG"] = round(TAVG, 2)
        # Building start_end_list during each loop.
        start_end_list.append(start_end_dict)

    return jsonify(start_end_list)

if __name__ == '__main__':
    app.run(debug=True)
