import time

import httpx


GCC_WARD_LAYER_URL = (
    "https://gisgcc.chennaicorporation.gov.in/server/rest/services/"
    "GCCDepts/GCC_COLLABORATION_LAYER/MapServer/6"
)

MAX_RETRIES = 3
BATCH_SIZE = 2000


def fetch_wards() -> dict:
    params = {
        "where": "1=1",
        "outFields": "objectid,pro_z_no,pro_ward_n",
        "returnGeometry": "true",
        "outSR": 4326,
        "resultRecordCount": BATCH_SIZE,
        "f": "geojson",
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = httpx.get(
                f"{GCC_WARD_LAYER_URL}/query",
                params=params,
                timeout=120.0,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise RuntimeError(data["error"])

            if data.get("type") != "FeatureCollection":
                raise ValueError(
                    "GCC Ward API did not return a "
                    "GeoJSON FeatureCollection"
                )

            return data

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError,
        ) as exc:

            last_error = exc

            print(
                f"Ward request failed "
                f"(attempt {attempt}/{MAX_RETRIES}): {exc}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))

    raise RuntimeError(
        f"GCC Ward request failed after "
        f"{MAX_RETRIES} attempts"
    ) from last_error


if __name__ == "__main__":
    data = fetch_wards()

    features = data.get("features", [])

    print("=== GCC WARD DOWNLOAD ===")
    print(f"Total wards received: {len(features)}")

    ward_ids = [
        feature.get("properties", {}).get("pro_ward_n")
        for feature in features
    ]

    ward_ids = [ward for ward in ward_ids if ward is not None]

    print(f"Unique ward IDs: {len(set(ward_ids))}")
    print(f"First 10 ward IDs: {ward_ids[:10]}")