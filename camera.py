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
        self.face_cascade = cv2.CascadeClassifier('xml\\haarcascade_frontalface_default.xml')

        self.present = False

        self.current_frame = None
        self.signal = False
        self.color = (250, 215, 155)

        self.last_rect = None
        self.left_move = 0
        self.right_move = 0
        self.command = ""
        self.locked = False

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
            self.current_frame = cv2.resize(frame, (WIDTH, HEIGHT))
            self.current_frame = cv2.flip(self.current_frame, 1)
            if not self.signal:
                processed_img = self.search_signal()
            else:
                processed_img = self.track_signal()

            self.detect_face()

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
                    #self.color = self.pick_color((x, y, w, h))
                    self.check_command((x, y, w, h))
            else:
                self.clear_history()

            cv2.imshow('camera', self.current_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.capture.release()
        cv2.destroyAllWindows()

    def search_signal(self):
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        fg = self.subtractor.apply(blur)
        ret, thresh = cv2.threshold(fg, 80, 255, cv2.THRESH_BINARY)
        return thresh

    def pick_color(self, coords):
        img = self.current_frame
        x, y, w, h = coords

        # coordinates for sample pixels
        x1 = int(x + w / 4) - 1
        y1 = int(y + h / 4) - 1
        x2 = int(x + w * 3 / 4) - 1
        y2 = int(y + h / 4) - 1
        x3 = int(x + w / 2) - 1
        y3 = int(y + h / 2) - 1
        x4 = int(x + w / 4) - 1
        y4 = int(y + h * 3 / 4) - 1
        x5 = int(x + w * 3 / 4) - 1
        y5 = int(y + h * 3 / 4) - 1

        color1 = img[y1, x1]
        color2 = img[y2, x2]
        color3 = img[y3, x3]
        color4 = img[y4, x4]
        color5 = img[y5, x5]
        colors = [color1, color2, color3, color4, color5]
        b = np.mean([color[0] for color in colors])
        g = np.mean([color[1] for color in colors])
        r = np.mean([color[2] for color in colors])
        return [b, g, r]

    def track_signal(self):
        lower = [0, 0, 0]
        upper = [75, 75, 85]
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")

        mask = cv2.inRange(self.current_frame, lower, upper)
        output = cv2.bitwise_and(self.current_frame, self.current_frame, mask=mask)
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(blur, 1, 255, cv2.THRESH_BINARY)
        cv2.imshow('color', output)
        return thresh

    def detect_face(self):
        gray = cv2.cvtColor(self.current_frame, cv2.COLOR_BGR2GRAY)
        # detect face from frame
        face = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face:
            cv2.rectangle(self.current_frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # determine whether the user is present
        if len(face):
            self.absent_count = 0
            self.present = True
        else:
            self.absent_count += 1

        if self.absent_count == 60:
            self.present = False
            self.absent_count = 0

    def check_command(self, rect):
        if self.last_rect is None:
            self.last_rect = rect
            return

        current_pos = rect[0] + rect[2] / 2
        last_pos = self.last_rect[0] + self.last_rect[2] / 2

        # determined the direction of movement
        if current_pos < last_pos - 200:
            self.left_move += 1
            self.right_move = 0
        elif current_pos > last_pos + 200:
            self.right_move += 1
            self.left_move = 0
        else:
            self.right_move = 0
            self.left_move = 0

        # 3 consecutive movements will determine the command
        if self.left_move == 3 and not self.locked:
            self.command = "left"
            self.clear_history()
            self.lock()
        elif self.right_move == 3 and not self.locked:
            self.command = "right"
            self.clear_history()
            self.lock()

    def clear_history(self):
        self.last_rect = None
        self.left_move = 0
        self.right_move = 0

    def lock(self):
        lock_thread = LockThread(self)
        lock_thread.daemon = True
        lock_thread.start()


class LockThread(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)

        self.parent = parent

    def run(self):
        self.parent.locked = True
        time.sleep(1)
        self.parent.locked = False
