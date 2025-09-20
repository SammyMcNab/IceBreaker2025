import os, glob, uuid, pandas as pd
from datetime import datetime
import rasterio

from config import CONFIG
from sar_preproc import load_sar_geotiff, to_db
from cfar_detector import ca_cfar, extract_bboxes
from ais_matcher import load_ais, match_detection
from scoring import score_match


def process_scene(sar_path, ais_df, config):
    arr, transform, crs, bounds, nodata = load_sar_geotiff(sar_path)
    image_db = to_db(arr, already_db=False)

    det_map = ca_cfar(image_db, guard=config['cfar_guard'], train=config['cfar_train'], pfa=config['cfar_pfa'])
    bboxes = extract_bboxes(det_map)

    # TODO: replace with scene timestamp from Maxar metadata
    scene_time = datetime.utcnow()

    results = []
    for b in bboxes:
        cy, cx = b['centroid']
        lon, lat = rasterio.transform.xy(transform, int(cy), int(cx))
        length_m = (b['maxr'] - b['minr']) * abs(transform.a)

        match, dist = match_detection(lon, lat, pd.to_datetime(scene_time), ais_df,
                                      time_window_s=config['time_window_s'], max_dist_m=config['max_dist_m'])
        matched_mmsi = match.get('mmsi') if match else None
        reported_len = match.get('length') if match else None

        score = score_match(dist or 1e6, 0, length_m, reported_len, config)
        is_dark = score < config['score_threshold']

        results.append({
            'id': str(uuid.uuid4()),
            'scene': os.path.basename(sar_path),
            'scene_time': scene_time,
            'lon': lon,
            'lat': lat,
            'length_m': length_m,
            'matched_mmsi': matched_mmsi,
            'matched_dist_m': dist,
            'score': score,
            'is_dark': is_dark
        })

    return results

def run_all(config):
    ais_df = load_ais(config['ais_csv'])
    scenes = glob.glob(os.path.join(config['sar_dir'], '*.tif'))
    all_results = []
    for s in scenes:
        all_results.extend(process_scene(s, ais_df, config))

    out_df = pd.DataFrame(all_results)
    os.makedirs(config['output_dir'], exist_ok=True)
    out_df.to_csv(os.path.join(config['output_dir'], 'dark_candidates.csv'), index=False)
    print(f"Saved {len(out_df)} candidates")

if __name__ == '__main__':
    run_all(CONFIG)
