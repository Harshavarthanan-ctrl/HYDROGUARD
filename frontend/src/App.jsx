import { useEffect, useState } from "react";
import hydroguardLogo from "./assets/hydroguard-logo.png";
import {

  GeoJSON,

  MapContainer,

  TileLayer,

  Tooltip,

  useMap,

} from "react-leaflet";

import L from "leaflet";

import "leaflet/dist/leaflet.css";

import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const CHENNAI_CENTER = [13.0827, 80.2707];

/* --------------------------------------------------

   Utility

-------------------------------------------------- */

const toRoman = (value) => {

  let number = Number(value);

  if (!Number.isFinite(number)) {

    return "—";

  }

  const numerals = [

    [10, "X"],

    [9, "IX"],

    [5, "V"],

    [4, "IV"],

    [1, "I"],

  ];

  let result = "";

  for (const [unit, numeral] of numerals) {

    while (number >= unit) {

      result += numeral;

      number -= unit;

    }

  }

  return result || "—";

};

const getZoneLabel = (ward) => {

  if (!ward?.zone) {

    return "Zone —";

  }

  const roman = toRoman(ward.zone);

  const name = ward.zone_name;

  return name

    ? `Zone ${roman} — ${name}`

    : `Zone ${roman}`;

};

/* --------------------------------------------------

   Map Controller

-------------------------------------------------- */

function MapController({ wards }) {

  const map = useMap();

  useEffect(() => {

    const validWards = wards.filter(

      (ward) => ward.geometry,

    );

    if (!validWards.length) {

      return;

    }

    const featureCollection = {

      type: "FeatureCollection",

      features: validWards.map((ward) => ({

        type: "Feature",

        geometry: ward.geometry,

        properties: ward,

      })),

    };

    const layer = L.geoJSON(featureCollection);

    map.fitBounds(layer.getBounds(), {

      padding: [20, 20],

    });

    setTimeout(() => {

      map.invalidateSize();

    }, 100);

  }, [wards, map]);

  return null;

}

/* --------------------------------------------------

   Risk Colors

-------------------------------------------------- */

function getRiskColor(category) {

  switch (category) {

    case "Very High":

      return "#b42318";

    case "High":

      return "#d95f35";

    case "Moderate":

      return "#d69214";

    case "Low":

      return "#16845a";

    default:

      return "#7a8796";

  }

}

/* --------------------------------------------------

   Ward Map Layer

-------------------------------------------------- */

function WardLayer({

  ward,

  onSelect,

  selected,

}) {

  const riskColor = getRiskColor(

    ward.risk_category,

  );

  const style = {

    color: selected ? "#102a43" : riskColor,

    weight: selected ? 3 : 1.5,

    fillColor: riskColor,

    fillOpacity: selected ? 0.75 : 0.45,

  };

  return (

    <GeoJSON

      key={ward.ward}

      data={{

        type: "Feature",

        geometry: ward.geometry,

        properties: ward,

      }}

      style={style}

      onEachFeature={(feature, layer) => {

        layer.on({

          click: () => {

            onSelect(ward);

          },

          mouseover: (event) => {

            event.target.setStyle({

              weight: 3,

              fillOpacity: 0.7,

            });

          },

          mouseout: (event) => {

            event.target.setStyle(style);

          },

        });

      }}

    >

      <Tooltip

        direction="top"

        sticky

        className="ward-map-tooltip"

      >

        <div>

          <strong>

            Ward {ward.ward}

          </strong>

          <span>

            {getZoneLabel(ward)}

          </span>

          <span>

            Risk:{" "}

            {ward.hydroguard_risk_index !== null

              ? ward.hydroguard_risk_index.toFixed(2)

              : "Unavailable"}

          </span>

          <span>

            {ward.risk_category ??

              "Unavailable"}

          </span>

        </div>

      </Tooltip>

    </GeoJSON>

  );

}

/* --------------------------------------------------

   Metric

-------------------------------------------------- */

function Metric({

  label,

  value,

  unit = "",

}) {

  return (

    <div className="metric">

      <span>{label}</span>

      <strong>

        {value ?? "—"}

        {value !== null &&

        value !== undefined &&

        unit

          ? ` ${unit}`

          : ""}

      </strong>

    </div>

  );

}

/* --------------------------------------------------

   Citywide Weather

-------------------------------------------------- */

function CitywideWeather({

  data,

  loading,

  error,

}) {

  if (loading) {

    return (

      <section className="citywide-weather">

        <div className="section-heading">

          <span>CITYWIDE WEATHER MONITORING</span>

          <h2>Chennai Weather Outlook</h2>

          <p>48-hour forecast across all GCC wards.</p>

        </div>

        <div className="citywide-weather-loading">

          Loading citywide weather forecast...

        </div>

      </section>

    );

  }

  if (error) {

    return (

      <section className="citywide-weather">

        <div className="section-heading">

          <span>CITYWIDE WEATHER MONITORING</span>

          <h2>Chennai Weather Outlook</h2>

        </div>

        <div className="citywide-weather-error">

          Unable to load citywide forecast:{" "}

          {error}

        </div>

      </section>

    );

  }

  if (!data) {

    return null;

  }

  const formatTime = (timestamp) =>

    new Date(timestamp).toLocaleTimeString(

      "en-IN",

      {

        timeZone: "Asia/Kolkata",

        hour: "2-digit",

        minute: "2-digit",

        hour12: false,

      },

    );

  const hourlyForecast = data.hourly_forecast ?? [];

  const maxRain = Math.max(

    ...hourlyForecast.map(

      (point) =>

        point.average_precipitation_mm ?? 0,

    ),

    0.1,

  );

  return (

    <section className="citywide-weather">

      <div className="section-heading citywide-weather-heading">

        <div>

          <span>CITYWIDE WEATHER MONITORING</span>

          <h2>Chennai Weather Outlook</h2>

          <p>

            48-hour Open-Meteo forecast across{" "}

            {data.ward_count} GCC wards.

          </p>

        </div>

        <div className="citywide-weather-source">

          <span>FORECAST SOURCE</span>

          <strong>OPEN-METEO</strong>

        </div>

      </div>

      <div className="citywide-weather-summary">

        <div>

          <span>24h Average Rainfall</span>

          <strong>

            {(

              data.average_24h_precipitation_mm ?? 0

            ).toFixed(2)}{" "}

            mm

          </strong>

          <small>Average across wards</small>

        </div>

        <div>

          <span>48h Average Rainfall</span>

          <strong>

            {(

              data.average_48h_precipitation_mm ?? 0

            ).toFixed(2)}{" "}

            mm

          </strong>

          <small>Average across wards</small>

        </div>

        <div>

          <span>Peak Hourly Rainfall</span>

          <strong>

            {(

              data.peak_hourly_precipitation_mm ?? 0

            ).toFixed(2)}{" "}

            mm

          </strong>

          <small>Maximum across wards</small>

        </div>

        <div>

          <span>Highest Rainfall Ward</span>

          <strong>

            {data.peak_rainfall_ward

              ? `Ward ${data.peak_rainfall_ward}`

              : "Unavailable"}

          </strong>

          <small>

            {data.peak_rainfall_zone_name

              ? `Zone ${toRoman(

                  data.peak_rainfall_zone,

                )} — ${

                  data.peak_rainfall_zone_name

                }`

              : data.peak_rainfall_zone

                ? `Zone ${toRoman(

                    data.peak_rainfall_zone,

                  )}`

                : "Zone unavailable"}

          </small>

        </div>

      </div>

      <div className="citywide-risk-highlight">

        <div>

          <span>HIGHEST HYDROGUARD FLOOD RISK</span>

          <strong>

            {data.highest_risk_ward

              ? `Ward ${data.highest_risk_ward}`

              : "Unavailable"}

          </strong>

          <p>

            {data.highest_risk_zone

              ? data.highest_risk_zone_name

                ? `Zone ${toRoman(

                    data.highest_risk_zone,

                  )} — ${

                    data.highest_risk_zone_name

                  }`

                : `Zone ${toRoman(

                    data.highest_risk_zone,

                  )}`

              : "Risk location unavailable"}

          </p>

        </div>

        <div className="citywide-risk-score">

          <strong>

            {data.highest_risk_index !== null &&

            data.highest_risk_index !== undefined

              ? Number(

                  data.highest_risk_index,

                ).toFixed(2)

              : "—"}

          </strong>

          <span>

            {data.highest_risk_category ??

              "Unavailable"}

          </span>

        </div>

      </div>

      <div className="citywide-chart-container">

        <div className="citywide-chart-title">

          <strong>Average Hourly Rainfall Forecast</strong>

          <span>mm · Chennai local time</span>

        </div>

        <div className="citywide-chart">

          {hourlyForecast.map(

            (point, index) => {

              const rainfall =

                point.average_precipitation_mm ??

                0;

              const height =

                rainfall > 0

                  ? Math.max(

                      (rainfall / maxRain) * 100,

                      8,

                    )

                  : 2;

              const showLabel =

                index % 4 === 0 ||

                index ===

                  hourlyForecast.length - 1;

              return (

                <div

                  className="citywide-bar-column"

                  key={point.timestamp}

                  title={`${formatTime(

                    point.timestamp,

                  )} · ${rainfall.toFixed(2)} mm`}

                >

                  <div className="citywide-bar-area">

                    <div

                      className="citywide-bar"

                      style={{

                        height: `${height}%`,

                      }}

                    />

                  </div>

                  {showLabel && (

                    <span>

                      {formatTime(

                        point.timestamp,

                      )}

                    </span>

                  )}

                </div>

              );

            },

          )}

        </div>

      </div>

      <div className="citywide-weather-note">

        Citywide rainfall values shown here are

        ward-average forecast depths. They should

        not be interpreted as a single rainfall

        measurement for the entire Chennai area.

      </div>

    </section>

  );

}

function WeatherForecast({

  data,

  loading,

  error,

}) {

  if (loading) {

    return (

      <div className="forecast-panel">

        <div className="forecast-header">

          <div>

            <span>

              WEATHER OUTLOOK

            </span>

            <h3>

              48-Hour Rainfall Forecast

            </h3>

          </div>

        </div>

        <div className="forecast-loading">

          Loading forecast data...

        </div>

      </div>

    );

  }

  if (error) {

    return (

      <div className="forecast-panel">

        <div className="forecast-header">

          <div>

            <span>

              WEATHER OUTLOOK

            </span>

            <h3>

              48-Hour Rainfall Forecast

            </h3>

          </div>

        </div>

        <div className="forecast-error">

          Unable to load weather forecast:{" "}

          {error}

        </div>

      </div>

    );

  }

  if (!data?.forecast?.length) {

    return null;

  }

  const formatTime = (timestamp) =>

    new Date(timestamp).toLocaleTimeString(

      "en-IN",

      {

        timeZone: "Asia/Kolkata",

        hour: "2-digit",

        minute: "2-digit",

        hour12: false,

      },

    );

  const formatDate = (timestamp) =>

    new Date(timestamp).toLocaleDateString(

      "en-IN",

      {

        timeZone: "Asia/Kolkata",

        day: "2-digit",

        month: "short",

      },

    );

  const maxRain = Math.max(

    ...data.forecast.map(

      (point) =>

        point.precipitation_mm ?? 0,

    ),

    0.1,

  );

  return (

    <div className="forecast-panel">

      <div className="forecast-header">

        <div>

          <span>

            WEATHER OUTLOOK

          </span>

          <h3>

            48-Hour Rainfall Forecast

          </h3>

          <p>

            Open-Meteo forecast · Chennai

            local time

          </p>

        </div>

        <div className="forecast-period">

          <strong>

            48 HOURS

          </strong>

          <span>

            Hourly forecast

          </span>

        </div>

      </div>

      <div className="forecast-summary">

        <div>

          <span>

            Next 24h Rainfall

          </span>

          <strong>

            {data.next_24h_precipitation_mm.toFixed(

              1,

            )}{" "}

            mm

          </strong>

        </div>

        <div>

          <span>

            Next 48h Rainfall

          </span>

          <strong>

            {data.next_48h_precipitation_mm.toFixed(

              1,

            )}{" "}

            mm

          </strong>

        </div>

        <div>

          <span>

            Peak Hourly Rainfall

          </span>

          <strong>

            {data.peak_hourly_precipitation_mm.toFixed(

              1,

            )}{" "}

            mm

          </strong>

        </div>

      </div>

      <div className="forecast-chart">

        <div className="forecast-y-label">

          RAINFALL (mm)

        </div>

        <div className="forecast-bars">

          {data.forecast.map(

            (point, index) => {

              const rainfall =

                point.precipitation_mm ?? 0;

              const height =

                rainfall > 0

                  ? Math.max(

                      (rainfall / maxRain) *

                        100,

                      8,

                    )

                  : 2;

              const showLabel =

                index % 4 === 0 ||

                index ===

                  data.forecast.length - 1;

              return (

                <div

                  className="forecast-bar-column"

                  key={point.timestamp}

                  title={`${formatDate(

                    point.timestamp,

                  )} ${formatTime(

                    point.timestamp,

                  )} · ${rainfall.toFixed(

                    1,

                  )} mm`}

                >

                  <div className="forecast-bar-area">

                    <div

                      className="forecast-bar"

                      style={{

                        height: `${height}%`,

                      }}

                    />

                  </div>

                  {showLabel && (

                    <span className="forecast-time">

                      {formatTime(

                        point.timestamp,

                      )}

                    </span>

                  )}

                </div>

              );

            },

          )}

        </div>

      </div>

      <div className="forecast-note">

        Forecast values represent hourly

        precipitation predicted by Open-Meteo.

        They are not observed rainfall

        measurements.

      </div>

    </div>

  );

}

/* --------------------------------------------------

   Ward Intelligence

-------------------------------------------------- */

function WardIntelligence({

  ward,

  weatherForecast,

  weatherLoading,

  weatherError,

}) {

  if (!ward) {

    return (

      <section className="ward-intelligence empty-intelligence">

        <div className="section-heading">

          <span>

            WARD INTELLIGENCE

          </span>

          <h2>

            Select a ward

          </h2>

        </div>

        <p>

          Select any Chennai ward from the map

          to view its current HydroGuard risk,

          weather and drainage intelligence.

        </p>

      </section>

    );

  }

  const riskValue =

    ward.hydroguard_risk_index !== null

      ? ward.hydroguard_risk_index.toFixed(2)

      : "—";

  const riskColor = getRiskColor(

    ward.risk_category,

  );

  return (

    <section className="ward-intelligence">

      <div className="section-heading">

        <div>

          <span>

            WARD INTELLIGENCE

          </span>

          <h2>

            Ward {ward.ward}

          </h2>

          <p>

            Greater Chennai Corporation ·{" "}

            {getZoneLabel(ward)}

          </p>

        </div>

        <div

          className="risk-status"

          style={{

            backgroundColor: riskColor,

          }}

        >

          {ward.risk_category ??

            "Unavailable"}

        </div>

      </div>

      <div className="ward-summary">

        <div className="ward-risk">

          <span>

            HYDROGUARD RISK INDEX

          </span>

          <strong>

            {riskValue}

          </strong>

          <small>

            Heuristic index · Scale 0–100

          </small>

        </div>

        <div className="summary-item">

          <span>

            Weather Hazard

          </span>

          <strong>

            {ward.weather_hazard !== null

              ? ward.weather_hazard.toFixed(2)

              : "—"}

          </strong>

        </div>

        <div className="summary-item">

          <span>

            Drainage Vulnerability

          </span>

          <strong>

            {ward.drainage_vulnerability !==

            null

              ? ward.drainage_vulnerability.toFixed(

                  2,

                )

              : "—"}

          </strong>

        </div>

      </div>

      <div className="intelligence-grid">

        <div className="intelligence-block">

          <h3>

            Weather Conditions

          </h3>

          <div className="metrics">

            <Metric

              label="Total Rainfall"

              value={

                ward.total_precipitation_mm !==

                null

                  ? ward.total_precipitation_mm.toFixed(

                      1,

                    )

                  : null

              }

              unit="mm"

            />

            <Metric

              label="Maximum Hourly Rainfall"

              value={

                ward.max_hourly_precipitation_mm !==

                null

                  ? ward.max_hourly_precipitation_mm.toFixed(

                      1,

                    )

                  : null

              }

              unit="mm"

            />

            <Metric

              label="Average Temperature"

              value={

                ward.avg_temperature_c !== null

                  ? ward.avg_temperature_c.toFixed(

                      1,

                    )

                  : null

              }

              unit="°C"

            />

            <Metric

              label="Maximum Temperature"

              value={

                ward.max_temperature_c !== null

                  ? ward.max_temperature_c.toFixed(

                      1,

                    )

                  : null

              }

              unit="°C"

            />

            <Metric

              label="Average Humidity"

              value={

                ward.avg_relative_humidity_pct !==

                null

                  ? ward.avg_relative_humidity_pct.toFixed(

                      1,

                    )

                  : null

              }

              unit="%"

            />

            <Metric

              label="Maximum Wind"

              value={

                ward.max_wind_speed_kmh !== null

                  ? ward.max_wind_speed_kmh.toFixed(

                      1,

                    )

                  : null

              }

              unit="km/h"

            />

            <Metric

              label="Average Pressure"

              value={

                ward.avg_surface_pressure_hpa !==

                null

                  ? ward.avg_surface_pressure_hpa.toFixed(

                      1,

                    )

                  : null

              }

              unit="hPa"

            />

            <Metric

              label="Observations"

              value={

                ward.observation_count

              }

            />

          </div>

        </div>

        <div className="intelligence-block">

          <h3>

            Drainage Infrastructure

          </h3>

          <div className="metrics">

            <Metric

              label="Vulnerability Score"

              value={

                ward.drainage_vulnerability !==

                null

                  ? ward.drainage_vulnerability.toFixed(

                      2,

                    )

                  : null

              }

            />

            <Metric

              label="Data Availability"

              value={

                ward.drainage_data_available

                  ? "Available"

                  : "Unavailable"

              }

            />

          </div>

        </div>

        <div className="intelligence-block">

          <h3>

            Data Status

          </h3>

          <div className="data-status-grid">

            <div>

              <span

                className={

                  ward.weather_data_available

                    ? "status-check available"

                    : "status-check"

                }

              >

                {ward.weather_data_available

                  ? "✓"

                  : "!"}

              </span>

              <div>

                <strong>

                  Weather Data

                </strong>

                <small>

                  {ward.weather_data_available

                    ? "Available"

                    : "Unavailable"}

                </small>

              </div>

            </div>

            <div>

              <span

                className={

                  ward.drainage_data_available

                    ? "status-check available"

                    : "status-check"

                }

              >

                {ward.drainage_data_available

                  ? "✓"

                  : "!"}

              </span>

              <div>

                <strong>

                  Drainage Data

                </strong>

                <small>

                  {ward.drainage_data_available

                    ? "Available"

                    : "Unavailable"}

                </small>

              </div>

            </div>

          </div>

        </div>

      </div>

      <WeatherForecast

        data={weatherForecast}

        loading={weatherLoading}

        error={weatherError}

      />

      <div className="methodology-note">

        <strong>

          Methodology note:

        </strong>{" "}

        The HydroGuard Risk Index is a heuristic

        indicator combining weather hazard and

        drainage vulnerability. It is not a

        calibrated flood probability.

      </div>

    </section>

  );

}

/* --------------------------------------------------

   Risk Ranking

-------------------------------------------------- */

function RiskRanking({

  wards,

  onSelect,

}) {

  const rankedWards = [...wards]

    .filter(

      (ward) =>

        ward.hydroguard_risk_index !==

        null,

    )

    .sort(

      (a, b) =>

        b.hydroguard_risk_index -

        a.hydroguard_risk_index,

    )

    .slice(0, 10);

  return (

    <section className="ranking-section">

      <div className="section-heading ranking-heading">

        <div>

          <span>

            RISK PRIORITY

          </span>

          <h2>

            Highest Risk Wards

          </h2>

          <p>

            Current HydroGuard risk index

            ranking across scored wards.

          </p>

        </div>

        <div className="ranking-count">

          TOP 10

        </div>

      </div>

      <div className="ranking-table">

        <div className="ranking-row ranking-head">

          <span>

            Rank

          </span>

          <span>

            Ward

          </span>

          <span>

            Zone

          </span>

          <span>

            Risk Index

          </span>

          <span>

            Category

          </span>

        </div>

        {rankedWards.map(

          (ward, index) => (

            <button

              className="ranking-row ranking-item"

              key={ward.ward}

              onClick={() =>

                onSelect(ward)

              }

            >

              <span className="rank-number">

                {index + 1}

              </span>

              <span className="ward-number">

                Ward {ward.ward}

              </span>

              <span>

                {ward.zone_name

                  ? `${toRoman(

                      ward.zone,

                    )} — ${

                      ward.zone_name

                    }`

                  : ward.zone

                    ? `Zone ${toRoman(

                        ward.zone,

                      )}`

                    : "—"}

              </span>

              <span className="ranking-score">

                {ward.hydroguard_risk_index.toFixed(

                  2,

                )}

              </span>

              <span>

                <span

                  className="category-pill"

                  style={{

                    backgroundColor:

                      getRiskColor(

                        ward.risk_category,

                      ),

                  }}

                >

                  {ward.risk_category}

                </span>

              </span>

            </button>

          ),

        )}

      </div>

    </section>

  );

}

/* --------------------------------------------------

   Main Application

-------------------------------------------------- */

function App() {

  const [wards, setWards] =

    useState([]);

  const [selectedWard, setSelectedWard] =

    useState(null);

  const [loading, setLoading] =

    useState(true);

  const [error, setError] =

    useState(null);

  const [weatherForecast, setWeatherForecast] =

    useState(null);

  const [weatherLoading, setWeatherLoading] =

    useState(false);

  const [weatherError, setWeatherError] =

    useState(null);

  const [

    citywideForecast,

    setCitywideForecast,

  ] = useState(null);

  const [

    citywideWeatherLoading,

    setCitywideWeatherLoading,

  ] = useState(false);

  const [

    citywideWeatherError,

    setCitywideWeatherError,

  ] = useState(null);

  /* --------------------------------------------------

     Load Risk Data

  -------------------------------------------------- */

  useEffect(() => {

    async function loadRiskData() {

      try {

        const response = await fetch(

          `${API_URL}/api/v1/risk/wards`,

        );

        if (!response.ok) {

          throw new Error(

            `API returned ${response.status}`,

          );

        }

        const data =

          await response.json();

        setWards(data.wards);

        setSelectedWard((current) => {

          if (!current) {

            return null;

          }

          return (

            data.wards.find(

              (ward) =>

                ward.ward ===

                current.ward,

            ) ?? null

          );

        });

      } catch (err) {

        setError(err.message);

      } finally {

        setLoading(false);

      }

    }

    loadRiskData();

    const refreshInterval =

      setInterval(

        loadRiskData,

        5 * 60 * 1000,

      );

    return () => {

      clearInterval(

        refreshInterval,

      );

    };

  }, []);

  /* --------------------------------------------------

     Load Selected Ward Forecast

  -------------------------------------------------- */

  useEffect(() => {

    if (!selectedWard?.ward) {

      setWeatherForecast(null);

      return;

    }

    async function loadWeatherForecast() {

      setWeatherLoading(true);

      setWeatherError(null);

      try {

        const response = await fetch(

          `${API_URL}/api/v1/weather/forecast/${selectedWard.ward}`,

        );

        if (!response.ok) {

          throw new Error(

            `Weather API returned ${response.status}`,

          );

        }

        const data =

          await response.json();

        setWeatherForecast(data);

      } catch (err) {

        setWeatherError(

          err.message,

        );

        setWeatherForecast(null);

      } finally {

        setWeatherLoading(false);

      }

    }

    loadWeatherForecast();

    const refreshInterval =

      setInterval(

        loadWeatherForecast,

        5 * 60 * 1000,

      );

    return () => {

      clearInterval(

        refreshInterval,

      );

    };

  }, [selectedWard?.ward]);

  /* --------------------------------------------------

     Load Citywide Forecast

  -------------------------------------------------- */

  useEffect(() => {

    async function loadCitywideForecast() {

      setCitywideWeatherLoading(true);

      setCitywideWeatherError(null);

      try {

        const response = await fetch(

          `${API_URL}/api/v1/weather/forecast`,

        );

        if (!response.ok) {

          throw new Error(

            `Weather API returned ${response.status}`,

          );

        }

        const data =

          await response.json();

        setCitywideForecast(data);

      } catch (err) {

        setCitywideWeatherError(

          err.message,

        );

        setCitywideForecast(null);

      } finally {

        setCitywideWeatherLoading(false);

      }

    }

    loadCitywideForecast();

    const refreshInterval =

      setInterval(

        loadCitywideForecast,

        5 * 60 * 1000,

      );

    return () => {

      clearInterval(

        refreshInterval,

      );

    };

  }, []);

  const scoredWards =

    wards.filter(

      (ward) =>

        ward.hydroguard_risk_index !==

        null,

    );

  const moderateOrHigher =

    scoredWards.filter(

      (ward) =>

        ward.hydroguard_risk_index >=

        25,

    );

  const unavailableWards =

    wards.filter(

      (ward) =>

        ward.hydroguard_risk_index ===

        null,

    );

  const lastUpdated =

    selectedWard?.generated_at

      ? new Date(

          selectedWard.generated_at,

        ).toLocaleString()

      : "Automatic refresh enabled";

  return (

    <div className="app">

      <header className="header">

        <div className="brand">

<img
  src={hydroguardLogo}
  alt="HydroGuard"
  className="hydroguard-logo"
/>

          <div>

            <h1>

              HydroGuard AI

            </h1>

            <p>

              Urban Flood Intelligence &

              Response System

            </p>

          </div>

        </div>

        <div className="system-status">

          <span className="status-dot" />

          <div>

            <strong>

              SYSTEM OPERATIONAL

            </strong>

            <small>

              API Connected

            </small>

          </div>

        </div>

      </header>

      <nav className="navigation">

        <div className="nav-inner">

          <span className="nav-active">

            Dashboard

          </span>

          <span>

            Risk Map

          </span>

          <span>

            Weather

          </span>

          <span>

            Drainage

          </span>

          <span>

            Reports

          </span>

        </div>

      </nav>

      <main className="dashboard">

        <section className="page-heading">

          <div>

            <span>

              GREATER CHENNAI CORPORATION

            </span>

            <h2>

              Citywide Flood Risk Monitoring

            </h2>

            <p>

              Real-time weather intelligence,

              drainage vulnerability and

              ward-level risk assessment.

            </p>

          </div>

          <div className="refresh-info">

            <strong>

              DATA PIPELINE

            </strong>

            <span>

              Automatic hourly weather refresh

            </span>

            <small>

              Dashboard refresh: every 5

              minutes

            </small>

          </div>

        </section>

        <section className="stats">

          <div className="stat-card">

            <span>

              Total Wards

            </span>

            <strong>

              {loading

                ? "—"

                : wards.length}

            </strong>

            <small>

              Official GCC ward coverage

            </small>

          </div>

          <div className="stat-card">

            <span>

              Scored Wards

            </span>

            <strong>

              {loading

                ? "—"

                : scoredWards.length}

            </strong>

            <small>

              Risk index available

            </small>

          </div>

          <div className="stat-card">

            <span>

              Moderate+ Risk

            </span>

            <strong>

              {loading

                ? "—"

                : moderateOrHigher.length}

            </strong>

            <small>

              Index ≥ 25

            </small>

          </div>

          <div className="stat-card">

            <span>

              Data Unavailable

            </span>

            <strong>

              {loading

                ? "—"

                : unavailableWards.length}

            </strong>

            <small>

              Requires data coverage

            </small>

          </div>

        </section>

        {error && (

          <div className="error">

            Unable to load risk data:{" "}

            {error}

          </div>

        )}

        {loading ? (

          <div className="loading">

            Loading Chennai ward risk data...

          </div>

        ) : (

          <>

            <CitywideWeather

              data={citywideForecast}

              loading={

                citywideWeatherLoading

              }

              error={

                citywideWeatherError

              }

            />

            <section className="map-section">

              <div className="section-heading map-heading">

                <div>

                  <span>

                    GEOSPATIAL RISK MONITORING

                  </span>

                  <h2>

                    Chennai Ward Risk Map

                  </h2>

                  <p>

                    Official GCC ward

                    boundaries with current

                    HydroGuard risk

                    intelligence.

                  </p>

                </div>

                <div className="map-source">

                  SOURCE

                  <strong>

                    GCC GIS

                  </strong>

                </div>

              </div>

              <div className="map-wrapper">

                <MapContainer

                  center={CHENNAI_CENTER}

                  zoom={11}

                  className="map"

                >

                  <TileLayer

                    attribution="&copy; OpenStreetMap contributors"

                    url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"

                  />

                  <MapController

                    wards={wards}

                  />

                  {wards

                    .filter(

                      (ward) =>

                        ward.geometry,

                    )

                    .map((ward) => (

                      <WardLayer

                        key={ward.ward}

                        ward={ward}

                        selected={

                          selectedWard?.ward ===

                          ward.ward

                        }

                        onSelect={

                          setSelectedWard

                        }

                      />

                    ))}

                </MapContainer>

                <div className="map-overlay">

                  <strong>

                    CHENNAI

                  </strong>

                  <span>

                    Ward-level monitoring

                  </span>

                </div>

              </div>

            </section>

            <WardIntelligence

              ward={selectedWard}

              weatherForecast={

                weatherForecast

              }

              weatherLoading={

                weatherLoading

              }

              weatherError={

                weatherError

              }

            />

            <RiskRanking

              wards={wards}

              onSelect={

                setSelectedWard

              }

            />

          </>

        )}

        <section className="legend-section">

          <div className="section-heading">

            <span>

              RISK CLASSIFICATION

            </span>

            <h2>

              HydroGuard Risk Categories

            </h2>

          </div>

          <div className="legend-items">

            <div>

              <span className="legend-dot low" />

              <strong>

                Low

              </strong>

              <span>

                0–24.99

              </span>

            </div>

            <div>

              <span className="legend-dot moderate" />

              <strong>

                Moderate

              </strong>

              <span>

                25–49.99

              </span>

            </div>

            <div>

              <span className="legend-dot high" />

              <strong>

                High

              </strong>

              <span>

                50–74.99

              </span>

            </div>

            <div>

              <span className="legend-dot very-high" />

              <strong>

                Very High

              </strong>

              <span>

                75–100

              </span>

            </div>

            <div>

              <span className="legend-dot unavailable" />

              <strong>

                Unavailable

              </strong>

            </div>

          </div>

        </section>

      </main>

      <footer className="footer">

        <div>

          <strong>

            HYDROGUARD AI

          </strong>

          <span>

            Urban Flood Intelligence &

            Response System

          </span>

        </div>

        <div className="footer-meta">

          <span>

            Weather: Open-Meteo

          </span>

          <span>

            GIS: Greater Chennai Corporation

          </span>

          <span>

            Last generated:{" "}

            {lastUpdated}

          </span>

        </div>

      </footer>

    </div>

  );

}

export default App;