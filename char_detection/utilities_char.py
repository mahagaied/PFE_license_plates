from imutils.object_detection import non_max_suppression
import numpy as np
import cv2
import pytesseract


pytesseract.pytesseract.tesseract_cmd = "C:\Program Files\Tesseract-OCR\\tesseract.exe"


def char_detect(image, net):
    orig = image
    (H, W) = image.shape[:2]

    (newW, newH) = (320, 320)
    rW = W / float(newW)
    rH = H / float(newH)

    image = cv2.resize(image, (newW, newH))
    (H, W) = image.shape[:2]

    layers = ["feature_fusion/Conv_7/Sigmoid", "feature_fusion/concat_3"]

    blob = cv2.dnn.blobFromImage(image, 1.0, (W, H), (123.68, 116.78, 103.94), swapRB=True, crop=False)
    net.setInput(blob)

    (scores, geometry) = net.forward(layers)
    (numRows, numCols) = scores.shape[2:4]

    rects = []
    confidences = []
    e_Xs = []
    s_Xs = []
    e_Ys = []
    s_Ys = []

    for y in range(0, numRows):

        scoresData = scores[0, 0, y]
        xData0 = geometry[0, 0, y]
        xData1 = geometry[0, 1, y]
        xData2 = geometry[0, 2, y]
        xData3 = geometry[0, 3, y]
        anglesData = geometry[0, 4, y]

        # loop over the number of columns
        for x in range(0, numCols):
            # if our score does not have sufficient probability, ignore it
            if scoresData[x] < 0.5:
                continue

            # compute the offset factor as our resulting feature maps will
            # be 4x smaller than the input image
            (offsetX, offsetY) = (x * 4.0, y * 4.0)

            # extract the rotation angle for the prediction and then
            # compute the sin and cosine
            angle = anglesData[x]
            cos = np.cos(angle)
            sin = np.sin(angle)

            # use the geometry volume to derive the width and height of
            # the bounding box
            h = xData0[x] + xData2[x]
            w = xData1[x] + xData3[x]

            # compute both the starting and ending (x, y)-coordinates for
            # the text prediction bounding box
            endX = int(offsetX + (cos * xData1[x]) + (sin * xData2[x]))
            endY = int(offsetY - (sin * xData1[x]) + (cos * xData2[x]))
            startX = int(endX - w)
            startY = int(endY - h)

            # add the bounding box coordinates and probability score to
            # our respective lists
            s_Xs.append(startX)
            e_Xs.append(endX)
            s_Ys.append(startY)
            e_Ys.append(endY)

            rects.append((startX, startY, endX, endY))
            confidences.append(scoresData[x])

    boxes = non_max_suppression(np.array(rects), probs=confidences)

    s_x = int(min(s_Xs) * rW)
    s_y = int(min(s_Ys) * rH)
    e_x = int(max(e_Xs) * rW)
    e_y = int(max(e_Ys) * rH)
    print(s_Xs)
    print(max(s_Xs))

    cv2.rectangle(orig, (s_x, s_y), (e_x, e_y), (0, 0, 255), 2)
    coord = s_x,s_y, e_x , e_y

    for (startX, startY, endX, endY) in boxes:
        startX = int(startX * rW)
        startY = int(startY * rH)
        endX = int(endX * rW)
        endY = int(endY * rH)

        cv2.rectangle(orig, (startX, startY), (endX, endY), (0, 255, 0), 2)


    return orig,coord


def crop_plate(img, coordinates):
    x, y, xe, ye = coordinates
    crop = img[y-10:ye+5, x:xe+20]
    return crop

def char_recognition(plate,detected,coord):
    height, width, _ = plate.shape
    grayscale = cv2.cvtColor(plate, cv2.COLOR_BGR2GRAY)
    (T, thresh) = cv2.threshold(grayscale, 120, 255, cv2.THRESH_BINARY_INV)
    #blur = cv2.GaussianBlur(grayscale, (5, 5), 0)
    cv2.imshow("threshPlate", thresh)
    cv2.waitKey(0)

    number_plate = pytesseract.image_to_string(thresh,
                                               config='-c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    print(f"Plate Number : {number_plate}")
    print(coord)
    img = cv2.putText(detected, number_plate, (coord[0], coord[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2,
                      cv2.LINE_AA)

    boxes = pytesseract.image_to_boxes(grayscale)
    for b in boxes.splitlines():
        b = b.split(' ')
        x, y, w, h = int(b[1]), int(b[2]), int(b[3]), int(b[4])
        cv2.rectangle(plate, (x, height - y), (w, height - h), (0, 0, 255), 1)
    cv2.imshow('boxes', plate)
    cv2.waitKey(0)

    return img
