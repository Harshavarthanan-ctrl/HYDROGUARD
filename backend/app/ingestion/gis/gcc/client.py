import time

import httpx

GCC_WARD_LAYER_URL = (
    "https://gisgcc.chennaicorporation.gov.in/server/rest/services/"
    "GCCDepts/GCC_COLLABORATION_LAYER/MapServer/6"
)
GCC_DRAIN_LAYER_URL = (
    "https://gisgcc.chennaicorporation.gov.in/server/rest/services/"
    "GCCDepts/GCC_COLLABORATION_LAYER/MapServer/8"
)

DEFAULT_BATCH_SIZE = 500
MAX_FEATURES = 100_000
MAX_RETRIES = 3


def fetch_drainage_batch(
    offset: int,
    batch_size: int = DEFAULT_BATCH_SIZE,
) -> dict:

    params = {
        "where": "1=1",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": 32644,
        "resultOffset": offset,
        "resultRecordCount": batch_size,
        "f": "geojson",
    }

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = httpx.get(
                f"{GCC_DRAIN_LAYER_URL}/query",
                params=params,
                timeout=60.0,
            )

            response.raise_for_status()

            data = response.json()

            if "error" in data:
                raise RuntimeError(data["error"])

            if data.get("type") != "FeatureCollection":
                raise ValueError(
                    "GCC API did not return a "
                    "GeoJSON FeatureCollection"
                )

            return data

        except (
            httpx.TimeoutException,
            httpx.NetworkError,
            httpx.HTTPStatusError,
        ) as exc:

            last_error = exc

            if attempt < MAX_RETRIES:
                time.sleep(2 ** (attempt - 1))

    raise RuntimeError(
        f"GCC API request failed after "
        f"{MAX_RETRIES} attempts"
    ) from last_error


def fetch_all_drainage(
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_features: int = MAX_FEATURES,
) -> dict:

    all_features = []
    seen_ids = set()
    offset = 0

    while len(all_features) < max_features:

        remaining = max_features - len(all_features)

        current_batch_size = min(
            batch_size,
            remaining,
        )

        print(
            f"Fetching records "
            f"{offset} → "
            f"{offset + current_batch_size - 1}..."
        )

        data = fetch_drainage_batch(
            offset=offset,
            batch_size=current_batch_size,
        )

        features = data.get("features", [])

        if not features:
            break

        new_features = []

        for feature in features:

            feature_id = feature.get("id")

            if feature_id in seen_ids:
                continue

            seen_ids.add(feature_id)
            new_features.append(feature)

        all_features.extend(new_features)

        print(
            f"Received {len(features)} | "
            f"New: {len(new_features)} | "
            f"Total: {len(all_features)}"
        )

        if len(features) < current_batch_size:
            break

        offset += len(features)

    return {
        "type": "FeatureCollection",
        "features": all_features,
    }


if __name__ == "__main__":

    geojson = fetch_all_drainage()

    print(
        "\n=== COMPLETE GCC DRAINAGE DOWNLOAD ==="
    )

    print(
        f"Total unique features: "
        f"{len(geojson['features'])}"
    )