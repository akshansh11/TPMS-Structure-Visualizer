# -*- coding: utf-8 -*-
"""tpms app.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1C-LutAOzFuCF-gCFKLEA-pR2KND7ioZ7
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st
from stl import mesh
from skimage import measure

# Define TPMS equations with parameters
def gyroid(x, y, z, a, b):
    return a * (np.sin(x) * np.cos(y)) + b * (np.sin(y) * np.cos(z)) + np.sin(z) * np.cos(x)

def schwarz_d(x, y, z, a, b):
    return a * np.cos(x) + b * np.cos(y) + np.cos(z)

def schwarz_p(x, y, z, a, b):
    return a * np.cos(x) + b * np.cos(y) + np.cos(z) - 1

def neovius(x, y, z, a, b):
    return a * (np.cos(x) + np.cos(y) + np.cos(z)) + b * np.cos(x) * np.cos(y) * np.cos(z)

# Function to generate the mesh and compute volume fraction
def generate_tpms(tpms_type='Gyroid', resolution=50, iso_values=[0.0], a=1.0, b=1.0, transparency=0.5):
    x = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    y = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    z = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    x, y, z = np.meshgrid(x, y, z)

    if tpms_type == 'Gyroid':
        values = gyroid(x, y, z, a, b)
    elif tpms_type == 'Schwarz D':
        values = schwarz_d(x, y, z, a, b)
    elif tpms_type == 'Schwarz P':
        values = schwarz_p(x, y, z, a, b)
    elif tpms_type == 'Neovius':
        values = neovius(x, y, z, a, b)

    fig = go.Figure()
    for iso_value in iso_values:
        fig.add_trace(go.Isosurface(
            x=x.flatten(),
            y=y.flatten(),
            z=z.flatten(),
            value=values.flatten(),
            isomin=iso_value,
            isomax=iso_value,
            surface_count=1,
            colorscale='Viridis',
            opacity=transparency,
        ))

    fig.update_layout(scene=dict(
        xaxis=dict(title='X-axis'),
        yaxis=dict(title='Y-axis'),
        zaxis=dict(title='Z-axis'),
    ))

    # Accurate volume fraction calculation
    volume_fraction = calculate_volume_fraction(values, iso_values[0])
    return fig, volume_fraction

# Accurate volume fraction calculation by counting grid cells
def calculate_volume_fraction(values, iso_value):
    # Count how many values are below or above the iso_value
    volume_above_iso = np.sum(values >= iso_value)
    total_volume = values.size  # Total number of grid points
    
    # Calculate volume fraction as the ratio of grid cells above iso_value to the total volume
    volume_fraction = (volume_above_iso / total_volume) * 100
    return volume_fraction

# Function to export TPMS as STL
def export_stl(x, y, z, values, iso_value, filename='tpms.stl'):
    verts, faces, _, _ = measure.marching_cubes(values, level=iso_value)
    verts = verts / values.shape[0] * (x.max() - x.min()) + x.min()

    tpms_mesh = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
    for i, f in enumerate(faces):
        for j in range(3):
            tpms_mesh.vectors[i][j] = verts[f[j], :]

    tpms_mesh.save(filename)
    return filename

# Streamlit app
st.title("TPMS Structure Visualizer")
st.image("tpms app.jpg")

# UI for selecting TPMS type and parameters
tpms_type = st.selectbox("Select TPMS Type:", ["Gyroid", "Schwarz D", "Schwarz P", "Neovius"])
resolution = st.slider("Select Resolution:", min_value=20, max_value=200, value=50, step=10)
iso_values = st.multiselect("Select Iso Values:", [-0.5, 0.0, 0.5, 1.0], default=[0.0])
a = st.slider("Adjust Coefficient A:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
b = st.slider("Adjust Coefficient B:", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
transparency = st.slider("Set Transparency:", min_value=0.1, max_value=1.0, value=0.5, step=0.1)

fig, volume_fraction = generate_tpms(tpms_type, resolution, iso_values, a, b, transparency)

st.plotly_chart(fig)

st.write(f"**Volume Fraction:** {volume_fraction:.2f}%")

# Export functionality
if st.button("Export as STL"):
    x = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    y = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    z = np.linspace(-2 * np.pi, 2 * np.pi, resolution)
    x, y, z = np.meshgrid(x, y, z)
    if tpms_type == 'Gyroid':
        values = gyroid(x, y, z, a, b)
    elif tpms_type == 'Schwarz D':
        values = schwarz_d(x, y, z, a, b)
    elif tpms_type == 'Schwarz P':
        values = schwarz_p(x, y, z, a, b)
    elif tpms_type == 'Neovius':
        values = neovius(x, y, z, a, b)

    filepath = export_stl(x, y, z, values, iso_values[0])
    st.success(f"STL file exported: {filepath}")
