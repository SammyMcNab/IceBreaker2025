import numpy as np
from scipy.ndimage import uniform_filter
from skimage.measure import label, regionprops


def ca_cfar(image_db, guard=2, train=10, pfa=1e-6):
    """
    Simplified 2D Cell-Averaging CFAR operating on dB image.
    Returns a boolean detection map of same shape.
    Note: this is a pragmatic implementation for prototyping, not high-performance.
    """
    # convert to linear scale for averaging
    img_lin = 10.0 ** (image_db / 10.0)

    # window sizes
    g = guard
    t = train
    kernel_size = 2*(g+t)+1

    # sum over neighborhood
    local_sum = uniform_filter(img_lin, size=kernel_size, mode='reflect') * (kernel_size**2)
    # sum over guard+cell region (we'll subtract later)
    inner_size = 2*g+1
    inner_sum = uniform_filter(img_lin, size=inner_size, mode='reflect') * (inner_size**2)

    # estimate background by subtracting inner_sum from local_sum, divide by number of training cells
    n_total = kernel_size**2
    n_inner = inner_size**2
    n_train = n_total - n_inner
    # avoid division by zero
    n_train = max(1, n_train)

    bg_mean = (local_sum - inner_sum) / n_train

    # threshold factor (simplified: CFAR factor approximate)
    # For CA-CFAR on gaussian background the threshold multiplier = alpha (depends on Pfa and num train cells)
    # We'll use approximate alpha = n_train * (pfa ** (-1.0 / n_train) - 1)
    alpha = n_train * (pfa ** (-1.0 / n_train) - 1.0)
    threshold = alpha * bg_mean

    # detection: compare CUT (cell under test) linear value to threshold
    detections = img_lin > threshold
    return detections


def extract_bboxes(detection_map, min_area=3):
    lbl = label(detection_map)
    props = regionprops(lbl)
    bboxes = []
    for p in props:
        if p.area >= min_area:
            minr, minc, maxr, maxc = p.bbox
            bboxes.append({'minr': minr, 'minc': minc, 'maxr': maxr, 'maxc': maxc, 'area': p.area, 'centroid': p.centroid})
    return bboxes
