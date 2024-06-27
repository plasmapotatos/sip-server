import cv2

# Replace with the actual URL of the RTSP stream
rtsp_url = "rtsp://your_raspberry_pi_ip:8081"

cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("Error: Couldn't open video stream")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    cv2.imshow('RTSP Stream', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
