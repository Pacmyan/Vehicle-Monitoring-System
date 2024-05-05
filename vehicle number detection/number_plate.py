import cv2
import pytesseract
import re
import requests
import json
from requests.auth import HTTPBasicAuth
from selenium import webdriver
from selenium.webdriver.common.by import By
#import keras_ocr
#import matplotlib.pyplot as plt

#pipeline = keras_ocr.pipeline.Pipeline()



pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

harcascade = "model/haarcascade_russian_plate_number.xml"


driver = webdriver.Chrome()
driver.get("http://127.0.0.1:5000/login")
username = driver.find_element(By.ID, "Username")
username.send_keys("security")
password = driver.find_element(By.ID, "password")
password.send_keys("security")

buttons = driver.find_elements(By.TAG_NAME, "button")
for button in buttons:
    if button.text == "submit":
        button.click()
        break
    

cap = cv2.VideoCapture(0)

cap.set(3, 640) 
cap.set(4, 480) 

min_area = 500
count = 0

username = 'security'
password = 'security'

plate_format_regex = re.compile(r'\b[A-Z]{2}\d{2}[A-Z]{2}\d{4}\b')

web_app_url = "http://127.0.0.1:5000"
login_url = web_app_url + "/login"
security_url = web_app_url + "/security"

while True:
    success, img = cap.read()

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y:y + h, x:x + w]
            # Convert ROI to the format expected by Keras-OCR
            #roi_pil = keras_ocr.tools.read(cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB))
            
            text = pytesseract.image_to_string(img_roi, config='--psm 11')
            #print("Extracted text:", text)

            match = plate_format_regex.search(text)
            if match:
                plate_number = match.group()
                
                print("License Plate Number:", plate_number)
                
                driver.get("http://127.0.0.1:5000/search_registration?plate_number="+plate_number)
                # Send the license plate number to the web application
                payload = {'plate_number': plate_number}
                headers = {'Content-Type': 'application/json; charset=UTF-8'}  # Set Content-Type header
                
                # Create a session to persist cookies
                session = requests.Session()

                # Authenticate with the login endpoint to obtain session cookie
                login_data = {'Username': username, 'password': password,'plate_number': plate_number}
                response = session.post(login_url, data=login_data)

                # Check if login was successful
                if response.status_code == 200:
                    print("Login successful")
                else:
                    print("Login failed")
                    continue  # Skip sending data if login failed
                
                # Send POST request to security endpoint with session cookie for authentication
                response = session.post(security_url, data=json.dumps(payload), headers=headers)

                # Check the response
                if response.status_code == 200:
                    print("Data sent successfully")
                else:
                    print("Error:", response.text)

            cv2.imshow("ROI", img_roi)

    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('s'):
        cv2.imwrite("plates/scaned_img_" + str(count) + ".jpg", img_roi)
        cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, "Plate Saved", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
        cv2.imshow("Results", img)
        cv2.waitKey(500)
        count += 1