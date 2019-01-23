import requests
import json
import errno
import os
import cv2
import csv
import numpy as np
import time
from PIL import Image
from io import BytesIO

# Replace <Subscription Key> with your valid subscription key.
## ENTER VALID KEY ##
subscription_key = X
assert subscription_key

# You must use the same region in your REST call as you used to get your
# subscription keys. For example, if you got your subscription keys from
# westus, replace 'westcentralus' in the URI below with 'westus'.
#
# Free trial subscription keys are generated in the 'westus' region.
# If you use a free trial subscription key, you shouldn't need to change
# this region.
vision_base_url = 'https://westcentralus.api.cognitive.microsoft.com/vision/v2.0/'

detect_url = vision_base_url + 'detect'

## CHOOSE A DIRECTORY WITH IMAGES ##
directory = X
filenames = ['filename']
amounts = ['amount']

path = 'out/'
try:
    os.makedirs(path)
except OSError as exc:  # Python >2.5
    if exc.errno == errno.EEXIST and os.path.isdir(path):
        pass
    else:
        raise

req_counter = 0
for filename in os.listdir(directory):
    req_counter += 1
    if req_counter == 21:
        print('Pausing for 20 seconds...')
        time.sleep(20)
        req_counter = 0
    # Set image_path to the local path of an image that you want to analyze.
    image_path = os.path.join(directory, filename)

    # Read the image into a byte array
    image_data = open(image_path, 'rb').read()
    headers    = {'Ocp-Apim-Subscription-Key': subscription_key, 
                  'Content-Type': 'application/octet-stream'}
    response = requests.post(detect_url, headers=headers, data=image_data)
    response.raise_for_status()

    # The 'detect' object contains various fields that describe the image. The most
    # relevant caption for the image is obtained from the 'description' property.
    detect = response.json()
    #print(json.dumps(response.json()))
    response_dict = response.json()
    obj_amount = len(response_dict['objects'])

    # Display the image and overlay it with the caption.
    image = Image.open(BytesIO(image_data))
    im_arr = np.asarray(image)
    im_arr_bgr = cv2.cvtColor(im_arr, cv2.COLOR_RGB2BGR)

    count = 0
    for i in range(obj_amount):
        if detect['objects'][i]['object'] == 'person':
            x = detect['objects'][i]['rectangle']['x']
            y = detect['objects'][i]['rectangle']['y']
            w = detect['objects'][i]['rectangle']['w']
            h = detect['objects'][i]['rectangle']['h']
            # Draw a rectangle
            cv2.rectangle(im_arr_bgr, (x, y), (x + w, y + h), (0,255,255), 4)
            count += 1

    print('Detected amount of people: ', count)

    cv2.imwrite('out/' + filename, im_arr_bgr)
    filenames.append(filename)
    amounts.append(count)

curr_time = time.strftime("%Y-%m-%d_%H-%M-%S")

with open('out/results_' + curr_time + '.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(zip(filenames, amounts))