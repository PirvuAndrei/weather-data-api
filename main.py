import os
import io
import pandas as pd
from flask import Flask, render_template, jsonify
from google.cloud import storage

app = Flask(__name__)

# --- CLOUD STORAGE CONFIGURATION ---
BUCKET_NAME = "weather-data-api-bucket"

# Global cache for DataFrames to avoid downloading from GCS on every request
_data_cache = {}

def _download_blob_as_text(path_in_bucket):
    """Helper function to download content from GCS as text."""
    client = storage.Client()
    bucket = client.get_bucket(BUCKET_NAME)
    blob = bucket.blob(path_in_bucket)
    return blob.download_as_text()

def _preprocess_dataframe(df):
    """
    Cleans column names, converts 'TG' to temperature, handles missing values (-999.9),
    and converts 'DATE' to datetime objects.
    """
    # Strip whitespace from all column names (fixes the ECA&D format issues)
    df.columns = df.columns.str.strip()

    # Convert 'TG' to temperature and handle missing values (-999.9)
    if 'TG' in df.columns:
        df['TG'] = pd.to_numeric(df['TG'], errors='coerce')
        df['TG'] = df['TG'] / 10
        # Inlocuim valorile lipsa cu string-ul "LOST"
        df.loc[df['TG'] == -999.9, 'TG'] = "LOST"

    # Convert 'DATE' to datetime objects
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d', errors='coerce')

    return df

def get_stations_dataframe():
    """Loads and caches the stations dataframe."""
    if 'stations' not in _data_cache:
        stations_content = _download_blob_as_text("data/stations.txt")
        df = pd.read_csv(io.StringIO(stations_content), skiprows=17)
        _data_cache['stations'] = _preprocess_dataframe(df)
    return _data_cache['stations']

def get_station_data_dataframe(station_id):
    """Loads and caches a specific station's weather data dataframe."""
    cache_key = f"station_data_{station_id}"
    if cache_key not in _data_cache:
        path = f"data/TG_STAID{str(station_id).zfill(6)}.txt"
        content = _download_blob_as_text(path)
        df = pd.read_csv(io.StringIO(content), skiprows=20)
        _data_cache[cache_key] = _preprocess_dataframe(df)
    return _data_cache[cache_key]

# Încărcăm lista de stații la pornire
df_station = get_stations_dataframe()

@app.route("/")
def home():
    # Afișăm pe prima pagină tabelul cu stațiile
    return render_template("home.html", 
                           data=df_station[["STAID", "STANAME"]].to_html())

@app.route("/api/v1/<station>/<date>")
def api(station, date):
    try:
        query_date = pd.to_datetime(date)
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400

    try:
        df = get_station_data_dataframe(station)
    except Exception as e:
        return jsonify({"error": f"Station {station} not found or error loading data."}), 404

    # Filter directly on the datetime column
    date_df = df.loc[df["DATE"] == query_date]

    if date_df.empty:
        temperature = "N/A" # No data for this specific date
    else:
        temperature = date_df["TG"].squeeze()
        # Daca sunt mai multe inregistrari (n-ar trebui), luam prima valoare
        if isinstance(temperature, pd.Series):
             temperature = temperature.iloc[0]

    return jsonify({"station": station, "date": date, "temperature": temperature})

@app.route("/api/v1/<station>")
def all_data(station):
    try:
        df = get_station_data_dataframe(station)
    except Exception as e:
        return jsonify({"error": f"Station {station} not found."}), 404
        
    df_copy = df.copy() 
    if 'DATE' in df_copy.columns:
        df_copy['DATE'] = df_copy['DATE'].dt.strftime('%Y-%m-%d')
        
    result = df_copy.to_dict(orient="records")
    return jsonify(result)

@app.route("/api/v1/yearly/<station>/<year>")
def on_year(station, year):
    try:
        year_int = int(year)
    except ValueError:
        return jsonify({"error": "Invalid year format. Please use YYYY."}), 400

    try:
        df = get_station_data_dataframe(station)
    except Exception as e:
         return jsonify({"error": f"Station {station} not found."}), 404

    # Filter by year directly on the datetime column
    yearly_df = df[df['DATE'].dt.year == year_int].copy() 

    if 'DATE' in yearly_df.columns:
        yearly_df['DATE'] = yearly_df['DATE'].dt.strftime('%Y-%m-%d')

    result = yearly_df.to_dict(orient="records")
    return jsonify(result)

if __name__ == "__main__":
    # CRUCIAL CHANGE FOR CLOUD RUN:
    # Get the port from the environment variable
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)