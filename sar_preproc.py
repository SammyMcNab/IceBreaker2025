import os
import numpy as np
import rasterio
from rasterio.warp import transform_bounds
from shapely.geometry import box


def load_sar_geotiff(path):
    """Load a single-band SAR GeoTIFF. Returns array (in linear units or dB), transform, crs, bounds."""
    with rasterio.open(path) as src:
        arr = src.read(1).astype('float32')
        transform = src.transform
        crs = src.crs
        bounds = src.bounds
        nodata = src.nodata
    return arr, transform, crs, bounds, nodata


def to_db(arr, already_db=False, eps=1e-6):
    if already_db:
        return arr
    # linear -> dB
    arr = np.maximum(arr, eps)
    return 10.0 * np.log10(arr)


def bbox_from_pixel(transform, x_min, y_min, x_max, y_max):
    # transform: Affine
    from rasterio.transform import rowcol
    from rasterio.transform import xy
    # compute four corners in lon/lat
    xs = [x_min, x_max]
    ys = [y_min, y_max]
    coords = []
    for yy in ys:
        for xx in xs:
            lon, lat = xy(transform, yy, xx)
            coords.append((lon, lat))
    return box(coords[0][0], coords[0][1], coords[3][0], coords[3][1])
