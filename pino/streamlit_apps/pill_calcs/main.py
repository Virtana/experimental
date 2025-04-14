import math

import pandas as pd
import streamlit as st

# import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np


## Formula for FOV
# Source: I made it up (https://app.eraser.io/workspace/x2vFAMOvzTsvOIs9LqfS) but dw chatgpt said something similar
def fov_calc(working_distance, afov_deg):
    return 2 * working_distance * math.tan(math.radians(afov_deg / 2))


# Acceleration due to gravity (in metres per second squared)
g = 9.81

st.title("Vision-based pill verification system: experimental calcs")

# Im putting all my "inputs" in the sidebar
with st.sidebar:
    st.header("Physical setup")
    # Working distance (in millimetres), ie the distance from the camera to the pill (but let"s say distance to the back wall to be safe)
    working_distance_mm = st.slider(
        "Working distance (mm)", min_value=1, max_value=1000, value=250
    )
    # Pill size
    pill_size_mm = st.slider("Pill size (mm)", min_value=1, max_value=20, value=10)

    st.header("Camera sensor setup")
    # Angular FOV (in degrees) (horizontal, vertical)
    hor_afov_col, vert_afov_col = st.columns(2)
    with hor_afov_col:
        hor_afov = st.number_input(
            "Horizontal FOV (degrees)", min_value=1, max_value=360, value=69
        )
    with vert_afov_col:
        vert_afov = st.number_input(
            "Vertical FOV (degrees)", min_value=1, max_value=360, value=42
        )
    # Resolution of the image sensor (horizontal, vertical)
    # TODO: Is this supposed to be dimensions of image sensor? Or the output image? Doesn"t matter cause they"re roughly the same, but worth a thought
    resolutions = (
        (640, 480),
        (1280, 720),
        (1280, 800),
        (1920, 1080),
        (3840, 2160),
    )
    res = st.selectbox(
        "Resolution:",
        options=resolutions,
        index=3,
        format_func=lambda x: f"{x[0]}x{x[1]}",
    )
    # Exposure time (us)
    exposure_time_us = st.slider(
        "Exposure time (us)", min_value=1, max_value=1_000, value=50
    )
    # FPS
    fpss = (30, 60, 90, 120, 240, 25_000)
    fps = st.selectbox("FPS", options=fpss, index=1)

    ## Some calcs for options lower down
    fov = (
        fov_calc(working_distance_mm, hor_afov),
        fov_calc(working_distance_mm, vert_afov),
    )
    s = max(fov) / 1000
    t = math.sqrt((2 * s) / g)

    # Pick which velocity to use
    v_avg = s / t
    v_max = math.sqrt(2 * g * s)
    v = st.radio(
        "Which velocity to use for motion blur calc",
        options=(v_avg, v_max),
        index=1,
        format_func=lambda x: f"{x:.2f}",
        horizontal=True,
        captions=("Average", "Maximum"),
    )


basic_tab, graph_tab, lighting_tab = st.tabs(("Some Results", "Graph (I think this is broken)", "Lighting"))
with basic_tab:
    # FOV (in millimetres) (horizontal, vertical)
    st.write(f"FOV: {fov[0]:.2f}mm x {fov[1]:.2f}mm")
    # Pixels per mm and spatial resolution
    pixels_per_mm = res[0] / fov[0]
    spatial_resolution = 1 / pixels_per_mm
    st.write(f"Pixels per mm: {pixels_per_mm:.2f}")
    st.write(f"Spatial resolution (mm per pixel): {spatial_resolution:.2f}mm")
    st.divider()

    # Distance (in millimetres) the pills will be traveling, during which we get a chance to take pics
    # Im setting distance as the larger of the two FOV dimensions, based on the camera setup we chose. It"s fine to pick the horizontal dimension here, we"ll just turn the camera sideways
    st.write(
        f"Pill fall distance (just the bigger of the FOV dimensions): {s * 1000:.2f}mm"
    )
    # Time we have to take images of the pills
    st.write(f"Pill air time: {t:.2f}s")
    # Number of images we"ll get
    st.write(f"Number of frames we can grab in this time: {int(fps * t)}")
    st.divider()

    # Pill size (pixels)
    st.write(f"Pill size: {pill_size_mm / spatial_resolution:.2f} pixels")
    # Distance travelled during exposure (in millimetres)
    s_e_mm = v * (exposure_time_us / 1_000_000) * 1000
    st.write(f"Distance travelled by pill during exposure time: {s_e_mm:.2f}mm")
    # Pixels traversed during this exposure travel
    motion_blur = s_e_mm / spatial_resolution
    st.write(f"Motion blur: {motion_blur:.2f} pixels")
    st.divider()


@st.fragment
def graph():
    # Plot a graph of exposure time vs motion blur
    num_datapoints = 100

    # x axis: exposure times (us)
    exposure_time_np = np.linspace(start=0, stop=1000, num=num_datapoints)
    # Convert to s
    exposure_time_np_s = exposure_time_np / 1_000_000

    # y axis: spatial resolution (mm per pixel)
    # To keep things simple, just picking some values to plot here rather than calcing based on input
    spatial_resolution_np = np.linspace(start=0.01, stop=2.15, num=num_datapoints)
    # Convert to m
    spatial_resolution_np_m = spatial_resolution_np / 1000

    # idek what this does, like a cross product I think?
    X, Y = np.meshgrid(exposure_time_np_s, spatial_resolution_np_m)

    # z axis: motion blur
    Z = (v * X) / Y

    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale="viridis")])
    fig.update_layout(title="Interactive 3D Surface Plot", autosize=True)
    st.plotly_chart(fig)

    # The inferior matplotlib version
    # fig = plt.figure(figsize=(8, 6))
    # ax = fig.add_subplot(111, projection="3d")
    # ax.plot_surface(X, Y, Z, cmap="viridis", edgecolor="none")

    # ax.set_xlabel("Exposure Time (us)")
    # ax.set_ylabel("Spatial resolution (mm per pixel)")
    # ax.set_zlabel("Motion Blur")

    # st.pyplot(fig)

    # data = pd.DataFrame(
    #     {
    #         "exposure_time": exposure_time_np,
    #         "spatial_resolution": spatial_resolution_np,
    #         "motion_blur": (v * exposure_time_np_s) / spatial_resolution_np_m,
    #     }
    # )
    # st.table(data)


with graph_tab:
    graph()

with lighting_tab:
    st.write("Lighting")
