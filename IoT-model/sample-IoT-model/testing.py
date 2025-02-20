
import cv2
import pytesseract
import os
import numpy as np
import datetime as dt

# Set up Tesseract OCR path (change this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\shamb\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'

# Load the Haar Cascade for number plate detection
plateCascade = cv2.CascadeClassifier(r'C:\Users\shamb\Downloads\henaTena\IoT-model\Digital-Twin-Security-IoT\sample-IoT-model\haarcascade_russian_plate_number.xml')

# State codes mapping
states = {
    "AN": "Andaman and Nicobar Islands", "AP": "Andhra Pradesh", "AR": "Arunachal Pradesh",
    "AS": "Assam", "BR": "Bihar", "CG": "Chhattisgarh", "CH": "Chandigarh",
    "DD": "Daman and Diu", "DL": "Delhi", "GA": "Goa", "GJ": "Gujarat",
    "HR": "Haryana", "HP": "Himachal Pradesh", "JH": "Jharkhand",
    "JK": "Jammu and Kashmir", "KA": "Karnataka", "KL": "Kerala",
    "LD": "Lakshadweep", "MH": "Maharashtra", "MN": "Manipur",
    "MP": "Madhya Pradesh", "MZ": "Mizoram", "NL": "Nagaland",
    "OR": "Odisha", "PB": "Punjab", "PY": "Puducherry",
    "RJ": "Rajasthan", "SK": "Sikkim", "TN": "Tamil Nadu",
    "TR": "Tripura", "TS": "Telangana", "UK": "Uttarakhand",
    "UP": "Uttar Pradesh", "WB": "West Bengal"
}

# Set frame width and height
frameWidth = 1000   # Frame Width
frameHeight = 480   # Frame Height

minArea = 500  # Minimum area for a valid plate

# Create a directory for saving images if it doesn't exist
save_path = "IMAGES"
if not os.path.exists(save_path):
    os.makedirs(save_path)

# Open webcam
cap = cv2.VideoCapture(0)
cap.set(3, frameWidth)  # Set width
cap.set(4, frameHeight)  # Set height
cap.set(10, 150)  # Set brightness

count = 0  # Counter for saved images

while True:
    success, img = cap.read()
    if not success:
        print("Failed to capture image")
        break

    # Convert image to grayscale for better detection
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detect number plates
    numberPlates = plateCascade.detectMultiScale(imgGray, 1.1, 4)

    for (x, y, w, h) in numberPlates:
        area = w * h
        if area > minArea:
            # Draw rectangle around detected plate
            cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

            # Extract and preprocess plate image
            imgRoi = img[y:y + h, x:x + w]  # Region of Interest (ROI)
            
            # Image Processing for OCR
            imgRoiGray = cv2.cvtColor(imgRoi, cv2.COLOR_BGR2GRAY)
            imgRoiBlur = cv2.GaussianBlur(imgRoiGray, (5, 5), 0)
            _, imgRoiThresh = cv2.threshold(imgRoiBlur, 127, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Use Tesseract to extract text from the plate
            read = pytesseract.image_to_string(imgRoiThresh, config='--psm 6')
            read = "".join([c for c in read if c.isalnum()])  # Remove special characters
            # Extract state code properly

            state_code = read[:2].upper()
            # Check if the state code exists in the dictionary
            if state_code in states:
                state_name = states[state_code]
                print(f"Detected Plate: {read} | State: {state_name}")
            else:
                print(f"Warning: State code '{state_code}' not found in database")

            # Capture timestamp
            today_date = dt.date.today()
            date_time = dt.datetime.strp(date_time_string, '%Y-%m-%d %H:%M')

            # Print time safely (without Unicode error)
            print(f"Detected Plate: {read} | Time: {date_time}".encode('utf-8', 'ignore').decode())
            # Show the processed number plate
            cv2.imshow("Number Plate", imgRoiThresh)

    cv2.imshow("Result", img)

    # Save plate image when 'S' is pressed
    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        save_file = os.path.join(save_path, f"plate_{count}.jpg")
        cv2.imwrite(save_file, imgRoiThresh)
        print(f"📸 Saved: {save_file}")
        
        # Show "Saved" message
        cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, "Scan Saved", (15, 265), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)
        cv2.imshow("Result", img)
        cv2.waitKey(500)
        count += 1

    # Exit on pressing 'Q'
    if key == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
