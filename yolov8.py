import cv2
import streamlit as st
from ultralytics import YOLO

def detect_cars(image_path, model_path='best (2).pt'):
    # Load custom YOLOv8 model
    model = YOLO(model_path)

    # Load the image
    frame = cv2.imread(image_path)
    if frame is None:
        st.error("Image not found or path is incorrect.")
        return None

    # Perform detection with a lower confidence threshold
    results = model(frame, conf=0.15)  # Lowered threshold for more detections

    # Initialize vehicle count
    vehicle_count = 0

    # Define the class indices for vehicle classes
    vehicle_classes = [0, 3, 4, 5, 6]  # Adjust these indices based on your dataset.yaml
    class_names = ['Car', 'Two Wheeler', 'Auto', 'Bus', 'Truck']  # Names for display

    # Iterate over each detected object in results
    for result in results:
        for box in result.boxes:
            # Extract the bounding box coordinates
            x1, y1, x2, y2 = map(int, box.xyxy[0])  # Convert coordinates to integers
            # Extract confidence and class ID
            conf = box.conf.item() if box.conf is not None else None
            cls = int(box.cls.item()) if box.cls is not None else None
            
            # Debugging: Print out the class ID and confidence of each detection
            print(f"Detected class ID: {cls}, confidence: {conf}")

            # Check if the class ID is in the vehicle_classes list
            if cls in vehicle_classes:
                vehicle_count += 1
                class_name = class_names[vehicle_classes.index(cls)]  # Get class name for display

                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                cv2.putText(frame, f'{class_name}: {conf:.2f}', (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

    # Display vehicle count on the image
    cv2.putText(frame, f'Total Vehicles: {vehicle_count}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Convert BGR to RGB for Streamlit display
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Use Streamlit to display the image
    st.image(frame_rgb, caption=f'Detected Vehicles: {vehicle_count}', use_column_width=True)

    return vehicle_count  # Return only the vehicle count
