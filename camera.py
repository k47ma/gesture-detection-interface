import cv2
import numpy as np
import time


class Camera(object):
    def __init__(self):
        object.__init__(self)

        self.capture = cv2.VideoCapture(1)
        self.subtractor = cv2.createBackgroundSubtractorMOG2()
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        self.position = None
        self.last_tick = time.time()
        self.fps = 0

        self.present = False
        self.absent_count = 0

        self.set_up()

    def set_up(self):
        count = 0
        while True:
            count += 1
            # calculate the fps
            tick = time.time()
            if tick - self.last_tick:
                fps = 1 / (tick - self.last_tick)
                self.last_tick = tick
            else:
                fps = 0
                self.fps = 0

            if count == 10:
                count = 0
                self.fps = fps

            result, frame = self.capture.read()

            # process the image to subtract the background
            resized = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            blur = cv2.GaussianBlur(gray, (5, 5), 0)
            fg = self.subtractor.apply(blur)
            ret, thresh = cv2.threshold(fg, 1, 255, cv2.THRESH_BINARY)

            # print fps to the image
            cv2.putText(resized, 'fps: %d.1' % self.fps, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # detect face from frame
            face = self.face_cascade.detectMultiScale(gray, 1.3, 5)
            for (x, y, w, h) in face:
                cv2.rectangle(resized, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # determine whether the user is present
            if len(face):
                self.present = True
                self.absent_count = 0
            else:
                self.absent_count += 1

            if self.absent_count == 60:
                self.absent_count = 0
                self.present = False

            # find the contour of the changed area
            img, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            if bool(contours) and self.present:
                max = 0
                ind = 0
                for i in range(len(contours)):
                    area = cv2.contourArea(contours[i])
                    if area > max:
                        max = area
                        ind = i
                contour = contours[ind]
                hull = cv2.convexHull(contour)

                # draw the contour
                if max > 5000:
                    cv2.drawContours(resized, [hull], 0, (0, 255, 0), 2)

            cv2.imshow('camera', resized)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()

camera = Camera()
camera.set_up()
