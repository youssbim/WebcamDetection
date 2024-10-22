import glob
import os
import cv2
import time
from emailing import send_email
from threading import Thread


def clean_folder():
    images = glob.glob("images/*.png")
    for image in images:
        os.remove(image)


def process_video_frame(first_frame, frame):
    # Convert to grayscale and apply Gaussian blur
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    # If first frame is None, initialize it
    if first_frame is None:
        return gray_frame_gau, gray_frame_gau

    # Calculate difference between first frame and current frame
    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    # Apply threshold and dilate to reduce noise
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)

    return gray_frame_gau, dil_frame


def detect_motion(contours, frame):
    status = 0
    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        # Draw a rectangle around detected object
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

        if rectangle.any():
            status = 1

    return status, frame


def main():
    video = cv2.VideoCapture(1)
    time.sleep(1)  # Wait for the camera to load
    first_frame = None
    status_list = [0, 0]
    count = 1

    while True:
        status = 0
        check, frame = video.read()
        if not check:
            print("Failed to grab frame.")
            break

        # Process current frame
        first_frame, dil_frame = process_video_frame(first_frame, frame)

        # Find contours on the dilated frame
        contours, _ = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Detect motion and draw rectangles around moving objects
        status, frame = detect_motion(contours, frame)

        if status == 1:
            cv2.imwrite(f"images/{count}.png", frame)
            count += 1
            all_images = glob.glob("images/*.png")
            index = int(len(all_images) / 2)
            image_with_object = all_images[index]

        # Update status list to track motion changes
        status_list.append(status)
        status_list = status_list[-2:]

        # If motion stops, send email
        if status_list[0] == 1 and status_list[1] == 0:
            email_thread = Thread(target=send_email, args=(image_with_object,))
            email_thread.daemon = True
            email_thread.start()

        # Display the frames
        cv2.imshow("Gray Frame", first_frame)
        cv2.imshow("Delta Frame", dil_frame)
        cv2.imshow("Video", frame)

        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()

    # Clean the images folder after exiting the loop
    clean_thread = Thread(target=clean_folder)
    clean_thread.start()
    clean_thread.join()


if __name__ == "__main__":
    main()