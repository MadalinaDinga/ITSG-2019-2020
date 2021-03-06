from flask import Flask, request, Response, json
from flask_cors import CORS
from keras.models import load_model
import tensorflow as tf
import numpy as np
import pandas as pd
import flask
from PIL import Image
from sklearn.externals import joblib

app = Flask(__name__)
CORS(app)

cnn = load_model('pets_classification64pixels_15epochs.h5')
clf = joblib.load('pets_mlp.pkl')

@app.route('/cnnclassifier/predict', methods=['POST'])
def predict():
    data = request.get_json(force=True)
    pred_mlp = -1
    pred_cnn = -1
    
    if 'imgPath' in data: 
        # run CNN Prediction
        img_path = data['imgPath']
        img_path = 'D:/Master/Sem3/ITSG/' + img_path
        image = Image.open(img_path).convert('RGB')
        resized_image = image.resize((64, 64))
        resized_image = np.asarray(resized_image)
        resized_image.shape = (1, 64, 64, 3)

        # Required because of a bug in Keras when using tensorflow graph cross threads    
        pred_cnn = np.argmax(cnn.predict(resized_image))
        
    del data['imgPath']
        
    # run MLP Prediction
	# the clf model takes 55 parameters (55 pet features)
    i = 0
    if (len(data) > 0):
        clf_in = np.zeros((55))
        for col in data:
            clf_in[i] = data[col]
            i += 1
    
    # MLP classifier requires all the textual features as input (55 features)
    if (i==55):
        pred_mlp = clf.predict([clf_in])
    
    if (pred_mlp > 0 and pred_cnn > 0):
        # combine the model predictions
        prediction = int((pred_cnn+pred_mlp)/2)
    else:
        if (pred_mlp > 0):
            # return MLP classifier prediction
            prediction = int(pred_mlp)
        else:
            # return CNN classifier prediction
            prediction = int(pred_cnn)
    
    data = {'result': prediction}
    return Response(response=json.dumps(data), status=200, mimetype='application/json')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)