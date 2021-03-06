# USAGE
# python extract_embeddings.py --dataset dataset --embeddings output/embeddings.pickle \
#    --detector face_detection_model --embedding-model openface_nn4.small2.v1.t7

# import the necessary packages
from imutils import paths
import numpy as np
import argparse
import imutils
import pickle
import cv2
import os

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--dataset", required=True, # dataset
    help="path to input directory of faces + images")
ap.add_argument("-e", "--embeddings", required=True, # 設定存檔路徑 --> output e.g 三人 ---> 產出三人 128D 人臉特徵
    help="path to output serialized db of facial embeddings")
ap.add_argument("-d", "--detector", required=True, # 
    help="path to OpenCV's deep learning face detector")
ap.add_argument("-m", "--embedding-model", required=True,
    help="path to OpenCV's deep learning face embedding model") # OpenFace model ---> 取得人臉 128D 特徵 
    # 想法來自 SIFT(三百萬張臉訓練的人臉特徵)
ap.add_argument("-c", "--confidence", type=float, default=0.5,
    help="minimum probability to filter weak detections")
args = vars(ap.parse_args())

# load our serialized face detector from disk
print("[INFO] loading face detector...")
protoPath = os.path.sep.join([args["detector"], "deploy.prototxt"]) # 載入 model
modelPath = os.path.sep.join([args["detector"],"res10_300x300_ssd_iter_140000_fp16.caffemodel"])
detector = cv2.dnn.readNetFromCaffe(protoPath, modelPath) 

# load our serialized face embedding model from disk
print("[INFO] loading face recognizer...")
embedder = cv2.dnn.readNetFromTorch(args["embedding_model"]) # cv2.dnn.readNetFromTorch 古老的Torch
# cv2.readNetFromONNX 新的PyTorch
# grab the paths to the input images in our dataset
print("[INFO] quantifying faces...")
imagePaths = list(paths.list_images(args["dataset"]))

# initialize our lists of extracted facial embeddings and
# corresponding people names
knownEmbeddings = []
knownNames = []

# initialize the total number of faces processed
total = 0

# loop over the image paths
for (i, imagePath) in enumerate(imagePaths):
    # extract the person name from the image path
    print("[INFO] processing image {}/{}".format(i + 1,
        len(imagePaths)))
    name = imagePath.split(os.path.sep)[-2]

    # load the image, resize it to have a width of 600 pixels (while
    # maintaining the aspect ratio), and then grab the image
    # dimensions
    image = cv2.imread(imagePath)
    image = imutils.resize(image, width=600) # resize width=600 方便與 300 換算
    (h, w) = image.shape[:2] # (y高,x寬,(color-channel)) NP buildin function --> shape
    #print(image)

    # construct a blob from the image
    imageBlob = cv2.dnn.blobFromImage( # 圖形預處理
        cv2.resize(image, (300, 300)), 1.0, (300, 300),
        (104.0, 177.0, 123.0), swapRB=False, crop=False)
    # 開始偵測
    # apply OpenCV's deep learning-based face detector to localize
    # faces in the input image
    detector.setInput(imageBlob)
    detections = detector.forward()

    # ensure at least one face was found
    if len(detections) > 0:
        # we're making the assumption that each image has only ONE
        # face, so find the bounding box with the largest probability
        i = np.argmax(detections[0, 0, :, 2]) # 排除其他人的臉, 設定精確度避免認錯臉
        confidence = detections[0, 0, i, 2]

        # ensure that the detection with the largest probability also
        # means our minimum probability test (thus helping filter out
        # weak detections)
        if confidence > args["confidence"]:
            # compute the (x, y)-coordinates of the bounding box for
            # the face
            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            (startX, startY, endX, endY) = box.astype("int")

            # extract the face ROI and grab the ROI dimensions
            face = image[startY:endY, startX:endX] # np slicing 切出臉
            (fH, fW) = face.shape[:2]

            # ensure the face width and height are sufficiently large
            if fW < 20 or fH < 20: # 切出的臉太小排除
                continue

            # construct a blob for the face ROI, then pass the blob
            # through our face embedding model to obtain the 128-d
            # quantification of the face
            faceBlob = cv2.dnn.blobFromImage(face, 1.0 / 255, # 正規化 by 1.0 / 255
                (96, 96), (0, 0, 0), swapRB=True, crop=False) # (96, 96) 訓練時大小, 所以解析度高會找不到臉
            embedder.setInput(faceBlob)
            vec = embedder.forward()

            # add the name of the person + corresponding face
            # embedding to their respective lists
            knownNames.append(name) # 臉 + 名字
            knownEmbeddings.append(vec.flatten())
            total += 1

# dump the facial embeddings + names to disk
print("[INFO] serializing {} encodings...".format(total))
data = {"embeddings": knownEmbeddings, "names": knownNames} # 存為字典
f = open(args["embeddings"], "wb")
f.write(pickle.dumps(data)) # memory serialization 方式存起來 ---> 記憶體原封不動的寫到硬碟內
# model 存檔方式: np.save() ---> np.load()
# model 存檔方式: pickle.dumps() ---> pickle.load() # memory serialization 方式存起來 ---> 記憶體原封不動的寫到硬碟內
f.close()
