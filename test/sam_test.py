import requests
import base64
import numpy as np
import cv2

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

# URL of the endpoint
url = 'http://127.0.0.1:5000/api/inference'

# Paths to the input image and mask
image_path = 'room.png'

# Encode the images
image_str = encode_image(image_path)

# Data to be sent in the POST request
data = {
    'image': image_str,
    'annotation_mode': ['Mark', 'Polygon'],
    'mask_alpha': 0.05
}

# Send a POST request
response = requests.post(url, json=data)

# Print the response from the server
response_data = response.json()
if 'error' in response_data:
    print("Error:", response_data['error'])
else:
    result_image_str = response_data['result_image']
    result_image_data = base64.b64decode(result_image_str)
    
    # Convert base64 to image
    nparr = np.frombuffer(result_image_data, np.uint8)
    result_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Save the result image
    cv2.imwrite('result_image.jpg', result_image)
    print("Result image saved as result_image.jpg")
