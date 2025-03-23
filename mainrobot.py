from MotorModule import Motor
from LaneModule import getLaneCurve
import WebcamModule

motor = Motor(2, 3, 4, 22, 17, 27)

def main():
    img = WebcamModule.getImg()
    
    if img is None:
        print("Skipping frame due to capture failure")
        return  # Skip processing if the image is None
    
    

    curveVal = getLaneCurve(img, 2)
    print('curve',curveVal)
    sen = 1.5  # SENSITIVITY
    maxVAl = 0.31 # MAX SPEED

    if curveVal > maxVAl:
        curveVal = maxVAl
    if curveVal < -maxVAl:
        curveVal = -maxVAl

    if curveVal > 0:
        sen = 2
        if curveVal < .06:
            curveVal = 0
    else:
        if curveVal > -.08:
            curveVal = 0

    motor.move(0.23, -curveVal * sen, 0.02)

if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("\nStopping the robot...")
            motor.stop()
            break  # Gracefully exit on Ctrl+C

