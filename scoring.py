import math

def score_match(dist_m, dt_s, observed_length_m, reported_length_m, params):
    # distance score (0..1)
    sigma_d = max(50.0, params['max_dist_m'] / 3.0)
    s_dist = math.exp(-(dist_m**2) / (2 * sigma_d**2))

    # time score
    sigma_t = max(60.0, params['time_window_s'] / 3.0)
    s_time = math.exp(-(dt_s**2) / (2 * sigma_t**2))

    # size similarity (if reported_length_m available)
    if reported_length_m is None or reported_length_m <= 0:
        s_size = 0.5
    else:
        ratio = min(observed_length_m / reported_length_m, reported_length_m / observed_length_m)
        s_size = ratio

    score = params['w_dist'] * s_dist + params['w_time'] * s_time + params['w_size'] * s_size
    return score
