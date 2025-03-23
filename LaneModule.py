import cv2
import numpy as np
import utlis
from picamera2 import Picamera2  # Import Picamera2 for real-time capture

curveList = []
avgVal = 10

def getLaneCurve(img, display=0):
    if img is None:
        print("Error: getLaneCurve received NoneType image.")
        return 0

    print(f"Original image shape: {img.shape}")  # Debugging line

    # Convert to 3-channel image if needed
    if img.shape[-1] == 4:
        img = img[:, :, :3]  # Remove alpha channel

    imgCopy = img.copy()
    imgResult = img.copy()

    #### STEP 1: Thresholding
    imgThres = utlis.thresholding(img)

    #### STEP 2: Perspective Transformation
    hT, wT, c = img.shape
    intialTrackBarVals = [70, 82, 20, 200]
    utlis.initializeTrackbars(intialTrackBarVals)
    points = utlis.valTrackbars()
    imgWarp = utlis.warpImg(imgThres, points, wT, hT)
    imgWarpPoints = utlis.drawPoints(imgCopy, points)

    #### STEP 3: Lane Detection
    middlePoint, imgHist = utlis.getHistogram(imgWarp, display=True, minPer=0.5, region=4)
    curveAveragePoint, imgHist = utlis.getHistogram(imgWarp, display=True, minPer=0.9)
    curveRaw = curveAveragePoint - middlePoint

    #### STEP 4: Smoothing Curve Values
    curveList.append(curveRaw)
    if len(curveList) > avgVal:
        curveList.pop(0)
    curve = int(sum(curveList) / len(curveList))

    #### STEP 5: Display Results
    if display != 0:
        imgInvWarp = utlis.warpImg(imgWarp, points, wT, hT, inv=True)
        imgInvWarp = cv2.cvtColor(imgInvWarp, cv2.COLOR_GRAY2BGR)
        imgInvWarp[0:hT // 3, 0:wT] = 0, 0, 0
        imgLaneColor = np.zeros_like(img)
        imgLaneColor[:] = 0, 255, 0
        imgLaneColor = cv2.bitwise_and(imgInvWarp, imgLaneColor)
        imgResult = cv2.addWeighted(imgResult, 1, imgLaneColor, 1, 0)

        midY = 450
        cv2.putText(imgResult, str(curve), (wT // 2 - 80, 85), cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 255), 3)
        cv2.line(imgResult, (wT // 2, midY), (wT // 2 + (curve * 3), midY), (255, 0, 255), 5)
        cv2.line(imgResult, ((wT // 2 + (curve * 3)), midY - 25), (wT // 2 + (curve * 3), midY + 25), (0, 255, 0), 5)

        if display == 2:
            imgStacked = utlis.stackImages(0.7, ([img, imgWarpPoints, imgWarp], [imgHist, imgLaneColor, imgResult]))
            cv2.imshow('ImageStack', imgStacked)
        elif display == 1:
            cv2.imshow('Result', imgResult)

    #### NORMALIZATION
    curve = curve / 100
    curve = max(min(curve, 1), -1)  # Limit curve between -1 and 1

    return curve

if __name__ == '__main__':
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (480, 240)  # Set resolution
    picam2.preview_configuration.main.format = "RGB888"  # Set color format
    picam2.configure("preview")
    picam2.start()

    utlis.initializeTrackbars([102, 80, 20, 214])

    while True:
        img = picam2.capture_array()  # Capture frame from Pi Camera
        img = cv2.resize(img, (480, 240))  # Resize to match processing
        curve = getLaneCurve(img, display=2)  # Process and display lane detection
        print(curve)

        if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
            break

    picam2.stop()
    cv2.destroyAllWindows()

