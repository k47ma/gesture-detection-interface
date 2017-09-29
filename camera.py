import cv2
import numpy as np
import time
import threading


WIDTH = 640
HEIGHT = 480


class Camera(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.done = False

        self.capture = cv2.VideoCapture(1)
        self.subtractor = cv2.createBackgroundSubtractorMOG2()
        self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

        self.current_frame = None
        self.last_rect = None
        self.left_move = 0
        self.right_move = 0
        self.command = ""

        self.position = None
        self.last_tick = time.time()
        self.fps = 0

        self.absent_count = 0

    def run(self):
        frame_count = 0

        while not self.done:
            frame_count += 1
            # calculate the fps
            tick = time.time()
            if tick - self.last_tick:
                fps = 1 / (tick - self.last_tick)
                self.last_tick = tick
            else:
                fps = 0
                self.fps = 0

            if frame_count == 10:
                frame_count = 0
                self.fps = fps

            result, frame = self.capture.read()

            # process the image to subtract the background
            processed_img = self.process_image(frame)

            # print fps to the image
            cv2.putText(self.current_frame, 'fps: %d.1' % self.fps, (10, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255), 2, cv2.LINE_AA)

            # find the contour of the changed area
            img, contours, hierarchy = cv2.findContours(processed_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            # foreground detected
            if bool(contours):
                max = 0
                ind = 0
                for i in range(len(contours)):
                    area = cv2.contourArea(contours[i])
                    if max < area < HEIGHT * WIDTH * 0.5:
                        max = area
                        ind = i
                contour = contours[ind]
                x, y, w, h = cv2.boundingRect(contour)

                # draw the contour if it's valid
                if max > 5000:
                    cv2.rectangle(self.current_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

                    self.check_command((x, y, w, h))
            else:
                self.clear_history()

            cv2.imshow('camera', self.current_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()

    def process_image(self, img):
        self.current_frame = cv2.resize(img, (WIDTH, HEIGHT))
        self.current_frame = cv2.flip(self.current_frame, 1)
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        fg = self.subtractor.apply(blur)
        ret, thresh = cv2.threshold(fg, 80, 255, cv2.THRESH_BINARY)
        self.detect_face(gray)
        return thresh

    def detect_face(self, img):
        # detect face from frame
        face = self.face_cascade.detectMultiScale(img, 1.3, 5)
        for (x, y, w, h) in face:
            cv2.rectangle(self.current_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # determine whether the user is present
        if len(face):
            self.absent_count = 0
        else:
            self.absent_count += 1

        if self.absent_count == 60:
            self.absent_count = 0

    def check_command(self, rect):
        if self.last_rect is None:
            self.last_rect = rect
            return

        current_pos = rect[0] + rect[2] / 2
        last_pos = self.last_rect[0] + self.last_rect[2] / 2

        # determined the direction of movement
        if current_pos < last_pos:
            self.left_move += 1
            self.right_move = 0
        else:
            self.right_move += 1
            self.left_move = 0

        # 3 consecutive movements will determine the command
        if self.left_move == 3:
            self.command = "left"
            self.clear_history()
        elif self.right_move == 3:
            self.command = "right"
            self.clear_history()

        # stop the camera to avoid redundant commands
        time.sleep(0.3)

    def clear_history(self):
        self.last_rect = None
        self.left_move = 0
        self.right_move = 0
