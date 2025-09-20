import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd
from scipy.spatial import cKDTree
from pyproj import Transformer


def load_ais(csv_path):
    df = pd.read_csv(csv_path, parse_dates=['timestamp'])
    # ensure columns exist
    required = {'mmsi','timestamp','lat','lon','sog','cog'}
    missing = required - set(df.columns)
    if missing:
        raise ValueError('Missing AIS columns: ' + ','.join(missing))
    return df


def to_mercator(gdf):
    return gdf.to_crs(epsg=3857)


def interp_position(a_prev, a_next, target_time):
    # linear interpolation between two AIS points (assumes timestamps are sorted)
    t0 = a_prev['timestamp'].astype('int64') / 1e9
    t1 = a_next['timestamp'].astype('int64') / 1e9
    if t1 == t0:
        return a_prev['lon'], a_prev['lat']
    alpha = (target_time.astype('int64')/1e9 - t0) / (t1 - t0)
    lon = a_prev['lon'] + alpha * (a_next['lon'] - a_prev['lon'])
    lat = a_prev['lat'] + alpha * (a_next['lat'] - a_prev['lat'])
    return lon, lat


def build_ais_kdtree(ais_df):
    g = gpd.GeoDataFrame(ais_df, geometry=gpd.points_from_xy(ais_df.lon, ais_df.lat), crs='EPSG:4326')
    g_merc = g.to_crs(epsg=3857)
    coords = np.vstack([g_merc.geometry.x, g_merc.geometry.y]).T
    tree = cKDTree(coords)
    return tree, g_merc


def match_detection(det_lon, det_lat, scene_time, ais_df, time_window_s=600, max_dist_m=800):
    # filter AIS by time window
    lo = scene_time - pd.Timedelta(seconds=time_window_s)
    hi = scene_time + pd.Timedelta(seconds=time_window_s)
    ais_sub = ais_df[(ais_df.timestamp >= lo) & (ais_df.timestamp <= hi)].copy()
    if ais_sub.empty:
        return None, None
    # for simplicity find nearest AIS position in filtered set
    g = gpd.GeoDataFrame(ais_sub, geometry=gpd.points_from_xy(ais_sub.lon, ais_sub.lat), crs='EPSG:4326')
    g_merc = g.to_crs(epsg=3857)
    coords = np.vstack([g_merc.geometry.x, g_merc.geometry.y]).T
    tree = cKDTree(coords)
    transformer = Transformer.from_crs('EPSG:4326', 'EPSG:3857', always_xy=True)
    x, y = transformer.transform(det_lon, det_lat)
    dist, idx = tree.query([x, y], k=1)
    if dist <= max_dist_m:
        match_row = g_merc.iloc[idx]
        return match_row.to_dict(), dist
    return None, dist
