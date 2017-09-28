import cv2
import numpy as np

capture = cv2.VideoCapture(1)
subtractor = cv2.createBackgroundSubtractorMOG2()

while True:
    result, frame = capture.read()

    # process the image to subtract the background
    resized = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    fg = subtractor.apply(blur)
    ret, thresh = cv2.threshold(fg, 1, 255, cv2.THRESH_BINARY)

    # find the contour of the changed area
    img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        max = 0
        ind = 0
        for i in range(len(contours)):
            area = cv2.contourArea(contours[i])
            if area > max:
                max = area
                ind = i
        contour = contours[ind]
        print(max)
        hull = cv2.convexHull(contour)

        # draw the contour
        colored = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        if max > 10000:
            cv2.drawContours(colored, [contour], 0, (0, 255, 0), 2)
            cv2.drawContours(colored, [hull], 0, (0, 0, 255), 2)

        cv2.imshow('camera', colored)
    else:
        cv2.imshow('camera', img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
