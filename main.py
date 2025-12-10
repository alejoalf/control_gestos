import sys
import time

if sys.version_info.major == 3 and sys.version_info.minor > 11:
    print("Error: You are running Python 3.12+ which is not compatible with MediaPipe.")
    print("Please run this script with Python 3.11 using: py -3.11 main.py")
    sys.exit(1)

import cv2
import mediapipe as mp

import numpy as np
import pyautogui

class HandDetector:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPosition(self, img, handNo=0, draw=True):
        self.lmList = []
        if self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myHand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)
        return self.lmList

    def fingersUp(self):
        fingers = []
        # Thumb (Simple check: is tip to the right of IP joint? Assuming right hand/camera mirror)
        # For now, we focus on Index and Middle for modes, Thumb is used in distance checks.
        # We'll just check the 4 long fingers.
        
        tipIds = [8, 12, 16, 20]
        
        # Thumb
        if self.lmList[4][1] > self.lmList[3][1]: # Right hand specific, might need adjustment
             fingers.append(1)
        else:
             fingers.append(0)

        # 4 Fingers
        for id in range(4):
            if self.lmList[tipIds[id]][2] < self.lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

def main():
    wCam, hCam = 640, 480
    frameR = 0 # Frame Reduction Removed for full mapping
    smoothening = 3 # Reduced for faster response
    
    pTime = 0
    plocX, plocY = 0, 0
    clocX, clocY = 0, 0

    cap = None
    # Try different camera indices
    for i in range(4):
        print(f"Testing camera index {i}...")
        temp_cap = cv2.VideoCapture(i)
        if temp_cap.isOpened():
            print(f"Success: Camera found at index {i}")
            cap = temp_cap
            break
        temp_cap.release()

    if cap is None or not cap.isOpened():
        print("Error: Could not open any camera.")
        print("Please check your webcam connection and Windows Privacy settings (Settings > Privacy > Camera).")
        return

    cap.set(3, wCam)
    cap.set(4, hCam)

    print("Starting camera feed... Press 'q' to exit.")

    detector = HandDetector(maxHands=1)
    wScr, hScr = pyautogui.size()
    
    # State variables
    left_click_active = False
    right_click_active = False
    scroll_cooldown = 0

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera frame.")
            break

        img = detector.findHands(img)
        lmList = detector.findPosition(img, draw=False)
        
        if len(lmList) != 0:
            x1, y1 = lmList[8][1:] # Index finger tip
            x2, y2 = lmList[12][1:] # Middle finger tip
            
            fingers = detector.fingersUp()
            # print(fingers)

            # Draw Frame Reduction Box
            cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
            (255, 0, 255), 2)

            # Mode 1: Moving Mode (Index up, Middle down) OR Dragging (Index + Thumb pinched)
            # We allow movement if Index is up OR if we are currently dragging (left click active)
            if (fingers[1] == 1 and fingers[2] == 0) or left_click_active:
                # Convert Coordinates
                x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
                y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))
                
                # Smoothen Values
                clocX = plocX + (x3 - plocX) / smoothening
                clocY = plocY + (y3 - plocY) / smoothening
                
                # Move Mouse
                try:
                    pyautogui.moveTo(wScr - clocX, clocY)
                except pyautogui.FailSafeException:
                    pass 
                
                cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
                plocX, plocY = clocX, clocY

                # Left Click / Drag Check (Index + Thumb)
                x_thumb, y_thumb = lmList[4][1:]
                length = np.hypot(x_thumb - x1, y_thumb - y1)
                
                # Hysteresis for stability
                click_start_dist = 30
                click_release_dist = 45

                if not left_click_active:
                    if length < click_start_dist:
                        cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                        pyautogui.mouseDown()
                        left_click_active = True
                        print("Left Click Down")
                else:
                    # Keep drawing green while holding
                    cv2.circle(img, (x1, y1), 15, (0, 255, 0), cv2.FILLED)
                    if length > click_release_dist:
                        pyautogui.mouseUp()
                        left_click_active = False
                        print("Left Click Up")
            
            # Mode 2: Scrolling Mode (Index and Middle up)
            if fingers[1] == 1 and fingers[2] == 1:
                # Scroll Logic with simple rate limiting/cooldown if needed, 
                # but continuous scroll is usually better.
                # Just reduce sensitivity or amount.
                
                if y1 < hCam // 2 - 50:
                    pyautogui.scroll(20)
                    cv2.putText(img, "Scroll UP", (20, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
                elif y1 > hCam // 2 + 50:
                    pyautogui.scroll(-20)
                    cv2.putText(img, "Scroll DOWN", (20, 450), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)

            # Right Click Check (Middle + Thumb)
            # Only trigger on "rising edge" (when pinch starts)
            x_thumb, y_thumb = lmList[4][1:]
            length_right = np.hypot(x_thumb - x2, y_thumb - y2)
            
            if length_right < 40:
                 cv2.circle(img, (x2, y2), 15, (255, 0, 0), cv2.FILLED) # Blue for Right Click
                 if not right_click_active:
                     pyautogui.rightClick()
                     right_click_active = True
                     print("Right Click")
            else:
                right_click_active = False


        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
