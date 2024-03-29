import cv2
import utilities_yolo

if __name__ == '__main__':
    # YOLO init
    path_weights = 'yolov3_training_final.weights'
    path_cfg = 'yolov3_testing.cfg'
    path_classes = 'classes.txt'

    net = cv2.dnn.readNet(path_weights, path_cfg)
    classes = []
    with open(path_classes, 'r') as f:
        classes = f.read().splitlines()

    # Detect
    path = "../license_images/10.png"
    #path = "Data_labels/1.png"
    coord, lp_image = utilities_yolo.detection(path, net, classes)

    cv2.imshow("detect", lp_image)

    # crop LP
    img = cv2.imread(path)
    LP = utilities_yolo.crop_plate(img, coord)

    cv2.imshow("plate", LP)
    cv2.waitKey(0)

    text = utilities_yolo.recognition(LP, lp_image, coord)
    cv2.imshow("recognition", text)
    cv2.waitKey(0)

    cv2.destroyAllWindows()

    """ Free and open source libraries for deep neural networks """
# 14 feb apre midi