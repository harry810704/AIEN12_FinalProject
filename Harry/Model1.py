#!/usr/bin/env python
# coding: utf-8

# In[1]:


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing.image import ImageDataGenerator, load_img
import warnings

import matplotlib.pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import sys
import json

def predict_image(filename):
    img = load_img(filename, target_size=(224, 224))
    image = keras.preprocessing.image.img_to_array(img)
    image = image / 255.0
    image = image.reshape(1,224,224,3)
    model = tf.keras.models.load_model('./pneumonia_model.h5')
    prediction = model.predict(image)
    prediction = prediction.tolist()
    print(f'Possibility of covid {prediction[0][0]}')
    print(f'Possibility of normal {prediction[0][1]}')
    print(f'Possibility of pneumonia {prediction[0][2]}')
    print(f'Possibility of Tuberculosis {prediction[0][3]}')
    plt.imshow(img)
    return {'Covid': prediction[0][0], 'Normal': prediction[0][1], 'Pneumonia': prediction[0][2], 'Tuberculosis': prediction[0][3]}

# Read image path from node js
path = './public/images/' + sys.argv[1]
result = predict_image(path)
keys = list(result.keys())
for i in range(3):
    result[keys[i]] = round(result[keys[i]]*100, 2)
print(result)

# Return values to node js
json = json.dumps(result)

print(str(json))
sys.stdout.flush()

