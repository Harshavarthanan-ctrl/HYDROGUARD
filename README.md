# HydroGuard AI

### Real-Time Urban Flood Intelligence & Response System

HydroGuard is a prototype urban flood-intelligence platform for
ward-level flood-risk monitoring in Chennai, India. It combines weather
forecasts, Greater Chennai Corporation (GCC) GIS data,
drainage-vulnerability features, and a heuristic risk index in a web
dashboard.

> **Status:** Prototype / decision-support demonstration. Risk scores
> are heuristic indices, not calibrated flood probabilities or an
> officially validated warning service.

## Key Features

-   Ward-level monitoring for 200 Chennai wards.
-   GIS-based analysis of GCC ward boundaries and storm-water drains.
-   Weather forecast ingestion from Open-Meteo.
-   Segment-level and ward-level drainage feature engineering.
-   Combined weather-hazard and drainage-vulnerability index.
-   Risk categories: Low, Moderate, High, Very High, and Unavailable.
-   FastAPI REST API.
-   React + Vite dashboard with Leaflet maps.
-   PostgreSQL/PostGIS spatial data storage.
-   Automated weather and risk refresh workflow.

## How It Works

1.  Ingest GCC ward and storm-water drainage GIS features.

2.  Retrieve forecasts from Open-Meteo for representative points in
    wards.

3.  Derive drainage condition and infrastructure vulnerability features.

4.  Calculate a heuristic weather-hazard index from forecast rainfall.

5.  Combine the indices using the current prototype weights:

    `HydroGuard Risk Index = 0.60 × Weather Hazard + 0.40 × Drainage Vulnerability`

6.  Serve ward risk and forecast data through FastAPI.

7.  Display citywide and ward-level information in the web dashboard.

Risk-category bands: - **Low:** 0--24.99 - **Moderate:** 25--49.99 -
**High:** 50--74.99 - **Very High:** 75--100

Weights and bands are prototype design choices and have not been
calibrated against a comprehensive historical flood-event dataset.

## Technology Stack

  Area              Technologies
  ----------------- ---------------------------------------
  Backend           Python, FastAPI, Pydantic
  Data processing   Pandas, GeoPandas, NumPy
  Database          PostgreSQL, PostGIS
  GIS               GCC GIS services, GeoPackage, Shapely
  Weather           Open-Meteo API
  Frontend          React, Vite, JavaScript, CSS
  Maps              Leaflet, React-Leaflet
  Testing           pytest
  Development       Git, Docker, Docker Compose

## Data Sources

### Greater Chennai Corporation GIS

Official GCC GIS service:
https://gisgcc.chennaicorporation.gov.in/server/rest/services/GCCDepts/GCC_COLLABORATION_LAYER/MapServer

-   Ward layer: `6`
-   Storm Water Drain layer: `8`

The ward fields used by this project contain ward and zone identifiers,
not locality names.

### Open-Meteo

Forecast API documentation: https://open-meteo.com/en/docs

Forecast values can change between refreshes. Forecast data should not
be described as historical measurements or satellite observations.

## Architecture

``` text
GCC Ward & Drainage GIS ──┐
                          ├──> Ingestion and validation
Open-Meteo Forecast API ──┘              |
                                         v
                               PostgreSQL + PostGIS
                                         |
                                         v
                             Feature engineering/refresh
                                         |
                                         v
                              Ward-level risk calculation
                                         |
                                         v
                                    FastAPI API
                                         |
                                         v
                               React + Leaflet dashboard
```

## Project Structure

The exact structure may vary by branch.

``` text
HYDROGUARD/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── ingestion/
│   │   │   ├── gis/
│   │   │   └── weather/
│   │   ├── risk_categories.py
│   │   ├── risk_index.py
│   │   ├── risk_refresh.py
│   │   └── risk_weather.py
│   └── tests/
├── frontend/
│   ├── public/
│   └── src/
├── data/
│   └── processed/
├── run_hydroguard.bat
└── README.md
```

## Prerequisites

-   Python 3.12 (recommended for the current development environment)
-   Node.js and npm
-   Docker Desktop with Docker Compose
-   Git

## Run Locally

Commands below assume Windows PowerShell and that you are in the project
root.

### 1. Start PostgreSQL/PostGIS

If the repository has a Docker Compose configuration for the database:

``` powershell
docker compose up -d
docker ps
```

The current development setup uses a PostGIS container named
`hydroguard-postgis` and a database named `hydroguard`. Use the actual
values configured in your local environment if they differ.

### 2. Configure the database connection

If the application expects a `.env` file, create it locally and set the
connection string to match your database, for example:

``` dotenv
DATABASE_URL=postgresql://hydroguard:YOUR_LOCAL_PASSWORD@localhost:5432/hydroguard
```

Use your own local credentials. **Never commit `.env` files, passwords,
API tokens, or other secrets to GitHub.**

### 3. Start the backend

From the project root:

``` powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

-   Backend: http://127.0.0.1:8000
-   API documentation: http://127.0.0.1:8000/docs
-   Health check: http://127.0.0.1:8000/health

### 4. Start the frontend

Open a second terminal:

``` powershell
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, usually http://localhost:5173.

Keep the database, backend, and frontend running while using the
dashboard.

## Main API Endpoints

  -----------------------------------------------------------------------------------
  Method                  Endpoint                            Purpose
  ----------------------- ----------------------------------- -----------------------
  GET                     `/health`                           Backend health check

  GET                     `/api/v1/risk/wards`                Retrieve ward-level
                                                              risk results

  GET                     `/api/v1/risk/wards/{ward}`         Retrieve risk for one
                                                              ward

  GET                     `/api/v1/weather/forecast`          Retrieve citywide
                                                              weather forecast

  GET                     `/api/v1/weather/forecast/{ward}`   Retrieve a ward
                                                              forecast
  -----------------------------------------------------------------------------------

Open `/docs` while the backend is running to inspect response schemas
and test endpoints.

## Testing

Activate the virtual environment, then run from the project root:

``` powershell
pytest
```

To run a specific test file:

``` powershell
pytest backend/tests/test_gcc_features.py
```

Use the test files present in your current branch; filenames may change
over time.

## Automated Refresh

The repository includes `run_hydroguard.bat` for refreshing weather and
risk data. If using Windows Task Scheduler, verify the script paths,
environment configuration, logging, and database availability. Test the
script manually before scheduling it.

## Important Limitations

-   The HydroGuard index is a **heuristic decision-support score**, not
    a probability of flooding.
-   The 60% weather / 40% drainage weighting and risk bands are not
    statistically calibrated.
-   Validation requires historical rainfall, observed flood incidents,
    waterlogging reports, and independent evaluation.
-   Open-Meteo forecasts are not historical ground observations or
    satellite-derived flood extent.
-   Runoff data may be missing and is not necessarily used in the
    current weather-hazard calculation.
-   Missing drainage measurements can limit cross-section feature
    reliability.
-   Some drain geometries may fall just outside ward polygons due to
    source or boundary precision.
-   This prototype should not be the sole basis for emergency decisions.

## Responsible Use

HydroGuard is intended for learning, research, prototyping, and
decision-support exploration. It is not an official Greater Chennai
Corporation product and is not affiliated with or endorsed by GCC unless
separately authorized. Consult official alerts and emergency services
for operational decisions.

## Future Improvements

-   Calibrate risk scores against documented flood events.
-   Incorporate historical rainfall and waterlogging observations.
-   Add uncertainty estimates and data-quality indicators.
-   Improve ingestion monitoring, logging, and failure recovery.
-   Add automated CI tests and deployment hardening.
-   Improve accessibility, timestamps, and source attribution.

## Contributing

1.  Fork the repository.
2.  Create a feature branch.
3.  Add or update tests.
4.  Run the test suite.
5.  Submit a pull request describing the change and its limitations.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

------------------------------------------------------------------------

**Built as an urban flood-intelligence prototype for Chennai, India.**
