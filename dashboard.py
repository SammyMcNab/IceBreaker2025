import dashboard as st
import pandas as pd
from PIL import Image

st.set_page_config(layout='wide')
st.title('Dark Vessel — MVP Alerts')

candidates_csv = 'output/dark_candidates.csv'
try:
    df = pd.read_csv(candidates_csv, parse_dates=['scene_time'])
except Exception as e:
    st.error(f'Could not open candidates CSV: {e}')
    st.stop()

st.sidebar.header('Filters')
min_score = st.sidebar.slider('Min score', 0.0, 1.0, 0.35)
region = st.sidebar.text_input('Region filter (e.g. bbox minlon,minlat,maxlon,maxlat)')

filtered = df[df.score >= min_score]
if region:
    vals = [float(x) for x in region.split(',')]
    minlon, minlat, maxlon, maxlat = vals
    filtered = filtered[(filtered.lon >= minlon) & (filtered.lon <= maxlon) & (filtered.lat >= minlat) & (filtered.lat <= maxlat)]

st.write(f'Found {len(filtered)} candidate(s)')

for idx, row in filtered.iterrows():
    cols = st.columns([1,2,2])
    with cols[0]:
        st.markdown(f"**ID:** {row['id']}  \n**Score:** {row['score']:.2f}  \n**Scene:** {row['scene']}  \n**Time:** {row['scene_time']}")
        if not pd.isna(row.get('patch_path')):
            try:
                img = Image.open(row['patch_path'])
                st.image(img, use_column_width=True)
            except Exception:
                st.text('patch not available')
    with cols[1]:
        st.markdown('**AIS Match**')
        if pd.notna(row.get('matched_mmsi')):
            st.write(f"MMSI: {int(row['matched_mmsi'])}  \nDist: {row['matched_dist_m']:.0f} m\nDT: {row['matched_dt_s']} s")
        else:
            st.write('No AIS match — dark candidate')
    with cols[2]:
        st.markdown('**Actions**')
        st.button(f'Flag {row['id']} for review')
        st.button(f'Export {row['id']}')
