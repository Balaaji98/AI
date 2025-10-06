import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from math import sqrt
from datetime import datetime

# ---------------------------
# Helper Functions
# ---------------------------
def euclidean(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def ewma_forecast(series, alpha=0.3):
    s = None
    for v in series:
        s = v if s is None else alpha*v + (1-alpha)*s
    return float(s) if s is not None else 0.0

def simulate_path(order_lines, coord_map):
    """Simulate total picker distance using nearest neighbor heuristic"""
    total = 0.0
    pack = (0,0)
    orders = order_lines.groupby('order_id')
    paths = []
    for oid, lines in orders:
        skus = lines['sku_id'].tolist()
        points = [coord_map[s] for s in skus if s in coord_map]
        if not points:
            continue
        seq = []
        cur = pack
        remaining = points.copy()
        while remaining:
            dists = [euclidean(cur,p) for p in remaining]
            idx = int(np.argmin(dists))
            cur = remaining.pop(idx)
            seq.append(cur)
        dist = sum([euclidean(pack, seq[0])] + [euclidean(seq[i], seq[i+1]) for i in range(len(seq)-1)] + [euclidean(seq[-1], pack)]) if seq else 0
        total += dist
        paths.append(seq)
    return total, paths

# ---------------------------
# Streamlit Page Config
# ---------------------------
st.set_page_config(page_title="Mini Slotting Optimizer", layout="wide")
st.title("⚡ Mini Slotting Optimizer — Optimizer & Simulation")

# ---------------------------
# Sidebar Options
# ---------------------------
view_option = st.sidebar.radio("Choose View", ["Optimizer", "Simulation"])
#st.sidebar.markdown("Data: Demo (5 SKUs, 10 locations, 1000 orders)")

# ---------------------------
# Generate Minimal Demo Data
# ---------------------------
np.random.seed(42)
# 5 SKUs
skus = [f"SKU{i}" for i in range(1,6)]
sizes = ['S','M','L','M','S']
sku_master = pd.DataFrame({
    'sku_id': skus,
    'size': sizes,
    'weight_kg': np.round(np.random.uniform(0.1,5.0,5),2),
    'fragile': [0,1,0,1,0]
})

# 10 Locations
locs = []
for i in range(1,11):
    locs.append({'location_id':f"L{i}", 'x':i, 'y':i%3, 'max_size':'L'})
location_master = pd.DataFrame(locs)

# 1000 Orders
orders = []
order_id = 1000
for _ in range(1000):
    order_id += 1
    chosen = np.random.choice(skus, size=np.random.randint(1,3), replace=False)
    for sku in chosen:
        orders.append({'order_id':order_id, 'order_date':datetime.now(), 'sku_id':sku, 'qty':1})
order_history = pd.DataFrame(orders)

# ---------------------------
# Step 1: Forecast Velocity
# ---------------------------
order_history['week'] = order_history['order_date'].dt.to_period('W').apply(lambda r:r.start_time)
weekly = order_history.groupby(['sku_id','week']).qty.sum().reset_index()
sku_week = weekly.pivot(index='sku_id', columns='week', values='qty').fillna(0)
velocities = [ewma_forecast(sku_week.loc[sku].values) if sku in sku_week.index else 0 for sku in skus]
sku_master['weekly_velocity'] = velocities

# ---------------------------
# Step 2: Slotting Optimization
# ---------------------------
location_master['dist_to_pack'] = location_master.apply(lambda r:euclidean((0,0),(r['x'],r['y'])),axis=1)
golden_bins = location_master.sort_values('dist_to_pack').head(3)

np.random.seed(1)
sku_master['current_location'] = np.random.choice(location_master['location_id'], len(sku_master))

assignments = []
used_bins = set()
for sku in sku_master.sort_values('weekly_velocity', ascending=False)['sku_id']:
    available = golden_bins[~golden_bins['location_id'].isin(used_bins)]
    chosen = available.sample(1)['location_id'].values[0] if not available.empty else location_master.sample(1)['location_id'].values[0]
    used_bins.add(chosen)
    assignments.append({'sku_id':sku, 'recommended_location':chosen})
sku_master = sku_master.merge(pd.DataFrame(assignments), on='sku_id', how='left')

# Coordinate maps
coord_map_current = {row['sku_id']: (location_master.loc[location_master['location_id']==row['current_location'],'x'].values[0],
                                     location_master.loc[location_master['location_id']==row['current_location'],'y'].values[0])
                     for idx,row in sku_master.iterrows()}
coord_map_recom = {row['sku_id']: (location_master.loc[location_master['location_id']==row['recommended_location'],'x'].values[0],
                                   location_master.loc[location_master['location_id']==row['recommended_location'],'y'].values[0])
                   for idx,row in sku_master.iterrows()}

# ---------------------------
# Step 3: Compute Distance Savings KPI
# ---------------------------
total_current, paths_current = simulate_path(order_history, coord_map_current)
total_recom, paths_recom = simulate_path(order_history, coord_map_recom)
pct_saving = 100*(total_current - total_recom)/total_current

# ---------------------------
# View: Optimizer
# ---------------------------
if view_option=="Optimizer":
    st.subheader("🏆 Slotting Optimization & KPI")
    col1,col2,col3 = st.columns(3)
    col1.metric("Current Distance (m)", f"{total_current:.0f}")
    col2.metric("Optimized Distance (m)", f"{total_recom:.0f}")
    col3.metric("Distance Savings (%)", f"{pct_saving:.1f}%")
    
    st.subheader("📄 GenAI Recommendations")
    for idx,row in sku_master.sort_values('weekly_velocity', ascending=False).head(5).iterrows():
        st.markdown(f"- Move **{row['sku_id']}** (velocity: {row['weekly_velocity']:.1f}) "
                    f"from `{row['current_location']}` → `{row['recommended_location']}` "
                    f"to reduce picker travel.")
    
    st.subheader("📊 Top SKU Recommendations Table")
    st.dataframe(sku_master[['sku_id','weekly_velocity','current_location','recommended_location']], use_container_width=True)
    st.download_button("⬇ Download Full Recommendations CSV", sku_master.to_csv(index=False), "slotting_plan.csv")

# ---------------------------
# View: Simulation (SKU-Level)
# ---------------------------
else:
    st.subheader("🚶 SKU-Level Movement Simulation")
    st.markdown("Select a SKU to see **Current vs Optimized path** and distance/time savings.")

    # SKU selector
    selected_sku = st.selectbox("Choose SKU", sku_master['sku_id'])

    row = sku_master[sku_master['sku_id']==selected_sku].iloc[0]
    start_label = "Start"
    dispatch_label = "Dispatch"
    current_loc_id = row['current_location']
    recom_loc_id = row['recommended_location']

    # Map Location IDs to X positions (categorical)
    locations = list(location_master['location_id'])
    x_positions = {loc: idx+1 for idx,loc in enumerate(locations)}

    # Compute distance as steps (index difference)
    #dist_current = abs(x_positions[current_loc_id]-0) + abs(x_positions[dispatch_label] if dispatch_label in x_positions else len(locations)+1 - x_positions[current_loc_id])
    #dist_optimized = abs(x_positions[recom_loc_id]-0) + abs(x_positions[dispatch_label] if dispatch_label in x_positions else len(locations)+1 - x_positions[recom_loc_id])

#    pct_saving_sku = 100*(dist_current - dist_optimized)/dist_current if dist_current>0 else 0
 #   avg_speed = 1.0  # unit/sec
  #  time_current = dist_current/avg_speed
   # time_optimized = dist_optimized/avg_speed

    # Get coordinates for current and recommended locations
    start_point = (0,0)
    dispatch_point = (0,0)  # treating dispatch as same as pack station
    current_coords = coord_map_current[selected_sku]
    recom_coords = coord_map_recom[selected_sku]

    # Distances (round trip: start -> location -> dispatch)
    dist_current = euclidean(start_point, current_coords) + euclidean(current_coords, dispatch_point)
    dist_optimized = euclidean(start_point, recom_coords) + euclidean(recom_coords, dispatch_point)

    pct_saving_sku = 100*(dist_current - dist_optimized)/dist_current if dist_current > 0 else 0
    avg_speed = 1.0  # unit/sec
    time_current = dist_current/avg_speed
    time_optimized = dist_optimized/avg_speed


    # KPIs
    col1,col2,col3,col4 = st.columns(4)
    col1.metric("Current Distance (steps)", f"{dist_current:.1f}")
    col2.metric("Optimized Distance (steps)", f"{dist_optimized:.1f}")
    col3.metric("Distance Savings (%)", f"{pct_saving_sku:.1f}%")
    col4.metric("Time Saved (s)", f"{time_current-time_optimized:.1f}")

    # GenAI-style recommendation
    st.markdown(f"**Recommendation:** Move **{selected_sku}** from `{current_loc_id}` → `{recom_loc_id}` "
                f"to reduce picker travel by ~{pct_saving_sku:.1f}%.")

    # Plot simulation using Location IDs on X-axis
    fig = go.Figure()

    # Current Path
    fig.add_trace(go.Scatter(
        x=[start_label, current_loc_id, dispatch_label],
        y=[0, 1, 2],
        mode="lines+markers+text",
        name="Current",
        line=dict(color="blue", width=3),
        marker=dict(size=12, color="blue"),
        text=[start_label, current_loc_id, dispatch_label],
        textposition="top center"
    ))

    # Optimized Path
    fig.add_trace(go.Scatter(
        x=[start_label, recom_loc_id, dispatch_label],
        y=[0, 1, 2],
        mode="lines+markers+text",
        name="Optimized",
        line=dict(color="green", width=3),
        marker=dict(size=12, color="green"),
        text=[start_label, recom_loc_id, dispatch_label],
        textposition="bottom center"
    ))

    fig.update_layout(
        title=f"Picker Movement for {selected_sku}",
        xaxis=dict(title="Location ID", type="category"),
        yaxis=dict(title="Path Stage", tickvals=[0,1,2], ticktext=["Start","Location","Dispatch"]),
        plot_bgcolor="#111",
        paper_bgcolor="#111",
        font_color="white",
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Blue:** Current Path | **Green:** Optimized Path")

