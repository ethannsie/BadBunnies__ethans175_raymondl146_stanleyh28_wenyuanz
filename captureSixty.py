import cv2
import os

save_dir = r'save my frames'

if not os.path.exists(save_dir):
    os.makedirs(save_dir)

cam = cv2.VideoCapture('http://100.118.139.202:4747/mjpegfeed')

num_frames = 60

for i in range(num_frames):
    result, image = cam.read()
    if result:
        filename = f"frame_{i+1:02d}.png"
        save_path = os.path.join(save_dir, filename)
        cv2.imwrite(save_path, image)
        print(f"Saved {save_path}")
    else:
        print(f"Failed to capture frame {i+1}")

cam.release()
print("Done capturing frames.")

