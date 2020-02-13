from flask import Flask, jsonify, request, render_template, url_for

import os
from matplotlib import style
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime as dt
from pprint import pprint
import black

import sqlalchemy
from sqlalchemy import create_engine, inspect, func, MetaData, desc
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/prcp")
def prcp_route():
    return render_template("prcp.html", prcp=prcp_df.to_html())


@app.route("/mosttemp")
def mosttemp():
    return render_template("mosttemp.html", mosttemp=most_temp_data_df.to_html())


engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

session = Session(engine)

measurement = Base.classes.measurement
station = Base.classes.station

prcp_query = []
for row in (
    session.query(measurement.date, measurement.prcp)
    .filter(measurement.date < dt.datetime(2017, 8, 23))
    .filter(measurement.date > dt.datetime(2016, 8, 23))
):
    prcp_query.append(row)

prcp_df = pd.DataFrame(prcp_query, columns=["date", "prcp"])

prcp_df = prcp_df.sort_values(by=["date"])

prcp_df.assign(date=pd.to_datetime(prcp_df["date"])).groupby(
    pd.Grouper(key="date", freq="1M")
).mean().plot.bar()
plt.xlabel("Date (Mean by Month)", size=25)
plt.ylabel("Precipitation", size=25)
plt.legend(fontsize=25)
plt.xticks(rotation=45)
plt.savefig(os.path.join("static", "prcp_fig"), dpi=300, bbox_inches="tight")

# Highest number of temperature observations
most_temp = (
    session.query(measurement.station, func.count(measurement.tobs))
    .group_by(measurement.tobs)
    .order_by(desc(func.count(measurement.tobs)))
    .limit(1)
    .all()
)

most_temp_data = []
for row in (
    session.query(measurement.date, measurement.tobs)
    .filter(measurement.station == most_temp[0][0])
    .filter(measurement.date <= dt.date(2017, 8, 23))
    .filter(measurement.date >= dt.date(2016, 8, 23))
):
    most_temp_data.append(row)

most_temp_data_df = pd.DataFrame(most_temp_data, columns=["date", "tobs"]).sort_values(
    by=["date"]
)

most_temp_data_df.assign(date=pd.to_datetime(most_temp_data_df["date"])).groupby(
    pd.Grouper(key="date", freq="1M")
).mean().plot.bar(figsize=(17, 8))
plt.xlabel("Date (Mean by Month)", size=25)
plt.ylabel("Precipitation", size=25)
plt.legend(fontsize=25)
plt.xticks(rotation=45)
plt.savefig(os.path.join("static", "temp_fig"), dpi=600, bbox_inches="tight")

if __name__ == "__main__":
    app.run(debug=True)
