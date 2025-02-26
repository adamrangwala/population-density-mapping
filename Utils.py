#######################
# Import libraries
from typing import Tuple, Optional
from osmnx.geocoder import geocode  # encodes strings as earth engine encodable lat, lon
from geopandas import GeoDataFrame
import pandas as pd
from pandas import DataFrame
from shapely.geometry import Polygon, Point, box


#######################
#Functions

# Interpret Inputted Address Text Input 
def validate_coordinates(lat: float, lon: float) -> None:
    if lat < -90 or lat > 90 or lon < -180 or lon > 180:
        raise ValueError(
            "longitude (-90 to 90) and latitude (-180 to 180) coordinates "
            "are not within valid ranges."
        )

# Exception for geocoding class
class GeoCodingError(Exception):
    pass

# Retrieve polygon address text
def get_aoi(
    address: Optional[str] = None,
    coordinates: Optional[Tuple[float, float]] = None,
    radius: int = 1000,
) -> Polygon:
    """
    Gets rectangular Polygon from input address or coordinates.

    Args:
        address: Address string
        coordinates: lat, lon
        radius: Radius in meter
        rectangular: Optionally return aoi as rectangular polygon, default False.

    Returns:
        shapely Polygon
    """
    if address is not None:
        if coordinates is not None:
            raise ValueError(
                "Both address and latlon coordinates were provided, please "
                "select only one!"
            )
        try:
            lat, lon = geocode(address)
        except ValueError as e:
            raise GeoCodingError(f"Could not geocode address '{address}'") from e
    else:
        lat, lon = coordinates  # type: ignore
    validate_coordinates(lat, lon)

    df = GeoDataFrame(
        DataFrame([0], columns=["id"]), crs="EPSG:4326", geometry=[Point(lon, lat)]
    )
    df = df.to_crs(df.estimate_utm_crs())
    df.geometry = df.geometry.buffer(radius)
    df = df.to_crs(crs=4326)
    poly = df.iloc[0].geometry
    
    return poly

