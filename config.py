CONFIG = {
    'sar_dir': 'data/sar_tiles/',
    'ais_csv': 'data/ais.csv',
    'output_dir': 'output/',


    # CFAR params
    'cfar_guard': 2,
    'cfar_train': 10,
    'cfar_pfa': 1e-6,


    # matching params
    'time_window_s': 600,
    'max_dist_m': 800,


    # scoring weights
    'w_dist': 0.6,
    'w_time': 0.2,
    'w_size': 0.2,
    'score_threshold': 0.35
}