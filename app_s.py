import streamlit as st
import numpy as np
import cv2
import tempfile
from yolov8 import detect_cars
from algo import optimize_traffic

st.title("Adaptive Traffic Signal Timer System 🚦")

st.write(
    "Upload four images representing traffic from the North, South, West, and East directions."
)

uploaded_images = st.file_uploader(
    "Upload exactly four images (one for each direction)", accept_multiple_files=True, type=["jpg", "jpeg", "png"]
)

# List of direction names to assign to each uploaded image
directions = ["North", "South", "West", "East"]

# Check if exactly 4 images are uploaded
if uploaded_images and len(uploaded_images) == 4:
    image_paths = []
    car_counts = []

    st.write("Detecting vehicles in each image...")

    for i, (image_file, direction) in enumerate(zip(uploaded_images, directions)):
        # Save uploaded images to temporary files
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_image:
            temp_image.write(image_file.read())
            image_path = temp_image.name
            image_paths.append(image_path)
        
        # Detect cars in the image
        num_cars = detect_cars(image_path)  # Adjust detect_cars function to handle images
        st.write(f"{direction} Direction: Detected {num_cars} vehicles.")
        car_counts.append(num_cars)

    # Calculate optimized green light times
    st.write("Optimizing traffic signal timing...")
    results = optimize_traffic(car_counts)
    
    st.write("**Optimized Green Light Times and Vehicle Counts:**")
    for direction, count, time in zip(directions, car_counts, [results['north'], results['south'], results['west'], results['east']]):
        st.write(f"{direction}: {time} seconds (Vehicles: {count})")

else:
    st.warning("Please upload exactly four images for processing.")
