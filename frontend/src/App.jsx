import { useEffect, useState } from "react";

import {
  GeoJSON,
  MapContainer,
  TileLayer,
  useMap,
} from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

const CHENNAI_CENTER = [13.0827, 80.2707];

function MapController({ wards }) {
  const map = useMap();

  useEffect(() => {
    const validWards = wards.filter(
      (ward) => ward.geometry,
    );

    if (!validWards.length) return;

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

function WardLayer({ ward, onSelect, selected }) {
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
    />
  );
}

function Metric({ label, value, unit = "" }) {
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

function WardIntelligence({ ward }) {
  if (!ward) {
    return (
      <section className="ward-intelligence empty-intelligence">
        <div className="section-heading">
          <span>WARD INTELLIGENCE</span>
          <h2>Select a ward</h2>
        </div>

        <p>
          Select any Chennai ward from the map to
          view its current HydroGuard risk,
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
          <span>WARD INTELLIGENCE</span>

          <h2>
            Ward {ward.ward}
          </h2>

          <p>
            Greater Chennai Corporation · Zone{" "}
            {ward.zone ?? "—"}
          </p>
        </div>

        <div
          className="risk-status"
          style={{
            backgroundColor: riskColor,
          }}
        >
          {ward.risk_category ?? "Unavailable"}
        </div>
      </div>

      <div className="ward-summary">
        <div className="ward-risk">
          <span>HYDROGUARD RISK INDEX</span>

          <strong>{riskValue}</strong>

          <small>
            Heuristic index · Scale 0–100
          </small>
        </div>

        <div className="summary-item">
          <span>Weather Hazard</span>
          <strong>
            {ward.weather_hazard !== null
              ? ward.weather_hazard.toFixed(2)
              : "—"}
          </strong>
        </div>

        <div className="summary-item">
          <span>Drainage Vulnerability</span>
          <strong>
            {ward.drainage_vulnerability !== null
              ? ward.drainage_vulnerability.toFixed(2)
              : "—"}
          </strong>
        </div>
      </div>

      <div className="intelligence-grid">
        <div className="intelligence-block">
          <h3>Weather Conditions</h3>

          <div className="metrics">
            <Metric
              label="Total Rainfall"
              value={
                ward.total_precipitation_mm !== null
                  ? ward.total_precipitation_mm.toFixed(1)
                  : null
              }
              unit="mm"
            />

            <Metric
              label="Maximum Hourly Rainfall"
              value={
                ward.max_hourly_precipitation_mm !== null
                  ? ward.max_hourly_precipitation_mm.toFixed(1)
                  : null
              }
              unit="mm"
            />

            <Metric
              label="Average Temperature"
              value={
                ward.avg_temperature_c !== null
                  ? ward.avg_temperature_c.toFixed(1)
                  : null
              }
              unit="°C"
            />

            <Metric
              label="Maximum Temperature"
              value={
                ward.max_temperature_c !== null
                  ? ward.max_temperature_c.toFixed(1)
                  : null
              }
              unit="°C"
            />

            <Metric
              label="Average Humidity"
              value={
                ward.avg_relative_humidity_pct !== null
                  ? ward.avg_relative_humidity_pct.toFixed(1)
                  : null
              }
              unit="%"
            />

            <Metric
              label="Maximum Wind"
              value={
                ward.max_wind_speed_kmh !== null
                  ? ward.max_wind_speed_kmh.toFixed(1)
                  : null
              }
              unit="km/h"
            />

            <Metric
              label="Average Pressure"
              value={
                ward.avg_surface_pressure_hpa !== null
                  ? ward.avg_surface_pressure_hpa.toFixed(1)
                  : null
              }
              unit="hPa"
            />

            <Metric
              label="Observations"
              value={ward.observation_count}
            />
          </div>
        </div>

        <div className="intelligence-block">
          <h3>Drainage Infrastructure</h3>

          <div className="metrics">
            <Metric
              label="Vulnerability Score"
              value={
                ward.drainage_vulnerability !== null
                  ? ward.drainage_vulnerability.toFixed(2)
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
          <h3>Data Status</h3>

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
                <strong>Weather Data</strong>
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
                <strong>Drainage Data</strong>
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

      <div className="methodology-note">
        <strong>Methodology note:</strong>{" "}
        The HydroGuard Risk Index is a heuristic
        indicator combining weather hazard and
        drainage vulnerability. It is not a
        calibrated flood probability.
      </div>
    </section>
  );
}

function RiskRanking({ wards, onSelect }) {
  const rankedWards = [...wards]
    .filter(
      (ward) =>
        ward.hydroguard_risk_index !== null,
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
          <span>RISK PRIORITY</span>

          <h2>
            Highest Risk Wards
          </h2>

          <p>
            Current HydroGuard risk index ranking
            across scored wards.
          </p>
        </div>

        <div className="ranking-count">
          TOP 10
        </div>
      </div>

      <div className="ranking-table">
        <div className="ranking-row ranking-head">
          <span>Rank</span>
          <span>Ward</span>
          <span>Zone</span>
          <span>Risk Index</span>
          <span>Category</span>
        </div>

        {rankedWards.map((ward, index) => (
          <button
            className="ranking-row ranking-item"
            key={ward.ward}
            onClick={() => onSelect(ward)}
          >
            <span className="rank-number">
              {index + 1}
            </span>

            <span className="ward-number">
              Ward {ward.ward}
            </span>

            <span>
              {ward.zone ?? "—"}
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
        ))}
      </div>
    </section>
  );
}

function App() {
  const [wards, setWards] = useState([]);
  const [selectedWard, setSelectedWard] =
    useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

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

        const data = await response.json();

        setWards(data.wards);

        setSelectedWard((current) => {
          if (!current) return null;

          return (
            data.wards.find(
              (ward) =>
                ward.ward === current.ward,
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

    const refreshInterval = setInterval(
      loadRiskData,
      5 * 60 * 1000,
    );

    return () => {
      clearInterval(refreshInterval);
    };
  }, []);

  const scoredWards = wards.filter(
    (ward) =>
      ward.hydroguard_risk_index !== null,
  );

  const moderateOrHigher =
    scoredWards.filter(
      (ward) =>
        ward.hydroguard_risk_index >= 25,
    );

  const unavailableWards = wards.filter(
    (ward) =>
      ward.hydroguard_risk_index === null,
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
          <div className="brand-mark">
            HG
          </div>

          <div>
            <h1>HydroGuard AI</h1>

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

          <span>Risk Map</span>
          <span>Weather</span>
          <span>Drainage</span>
          <span>Reports</span>
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
              drainage vulnerability and ward-level
              risk assessment.
            </p>
          </div>

          <div className="refresh-info">
            <strong>DATA PIPELINE</strong>
            <span>
              Automatic hourly weather refresh
            </span>
            <small>
              Dashboard refresh: every 5 minutes
            </small>
          </div>
        </section>

        <section className="stats">
          <div className="stat-card">
            <span>Total Wards</span>
            <strong>
              {loading ? "—" : wards.length}
            </strong>
            <small>
              Official GCC ward coverage
            </small>
          </div>

          <div className="stat-card">
            <span>Scored Wards</span>
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
            <span>Moderate+ Risk</span>
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
            <span>Data Unavailable</span>
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
            Unable to load risk data: {error}
          </div>
        )}

        {loading ? (
          <div className="loading">
            Loading Chennai ward risk data...
          </div>
        ) : (
          <>
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
                    Official GCC ward boundaries
                    with current HydroGuard risk
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
            />

            <RiskRanking
              wards={wards}
              onSelect={setSelectedWard}
            />
          </>
        )}

        <section className="legend-section">
          <div className="section-heading">
            <span>RISK CLASSIFICATION</span>
            <h2>HydroGuard Risk Categories</h2>
          </div>

          <div className="legend-items">
            <div>
              <span className="legend-dot low" />
              <strong>Low</strong>
              <span>0–24.99</span>
            </div>

            <div>
              <span className="legend-dot moderate" />
              <strong>Moderate</strong>
              <span>25–49.99</span>
            </div>

            <div>
              <span className="legend-dot high" />
              <strong>High</strong>
              <span>50–74.99</span>
            </div>

            <div>
              <span className="legend-dot very-high" />
              <strong>Very High</strong>
              <span>75–100</span>
            </div>

            <div>
              <span className="legend-dot unavailable" />
              <strong>Unavailable</strong>
            </div>
          </div>
        </section>
      </main>

      <footer className="footer">
        <div>
          <strong>HYDROGUARD AI</strong>

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
            Last generated: {lastUpdated}
          </span>
        </div>
      </footer>
    </div>
  );
}

export default App;