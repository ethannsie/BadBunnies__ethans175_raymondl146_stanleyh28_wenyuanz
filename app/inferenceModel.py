import cv2
import typing
import numpy as np
import glob
import subprocess
import os
import sys

from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer

class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list: typing.Union[str, list], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image: np.ndarray):
        image = cv2.resize(image, self.input_shapes[0][1:3][::-1])

        image_pred = np.expand_dims(image, axis=0).astype(np.float32)

        preds = self.model.run(self.output_names, {self.input_names[0]: image_pred})[0]

        text = ctc_decoder(preds, self.char_list)[0]

        return text
    
def segment_and_save_words(image_or_path, output_dir="segmented_words", boxed_output_path="boxed_preview.jpg"):
    """
    Segments words from an image, saves them in output_dir as 0.jpg, 1.jpg, ...,
    and saves a version of the image with boxes drawn around each word.
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Load image if given path
    if isinstance(image_or_path, str):
        image = cv2.imread(image_or_path)
    else:
        image = image_or_path

    image_copy = image.copy()  # for drawing boxes
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Binarize
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                   cv2.THRESH_BINARY_INV, blockSize=15, C=11)

    # After thresholding, add top/bottom padding to reduce line merging
    padded_thresh = cv2.copyMakeBorder(
        thresh,
        top=10, bottom=10, left=0, right=0,
        borderType=cv2.BORDER_CONSTANT,
        value=0  # black padding
    )

    # Then do dilation
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    dilated = cv2.dilate(thresh, kernel, iterations=1)

    # Contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=lambda c: (cv2.boundingRect(c)[1], cv2.boundingRect(c)[0]))
    rows = {}
    row_idx = 0
    for box in contours:
        find_row = False
        x1, y1, w1, h1 = cv2.boundingRect(box)
        mid_y1 = y1+h1/2
        for key in sorted(rows.keys()):
            x2, y2, w2, h2 = cv2.boundingRect(rows[key][0])
            mid_y2 = y2+h2/2
            if abs(mid_y1-mid_y2) < (h1+h2)/2*0.8:
                rows[key].append(box)
                find_row = True
                break
        if find_row == False:
            rows[row_idx] = [box]
            row_idx += 1
            
    sorted_contours = []
    for i in range(row_idx):
        sorted_row = sorted(rows[i], key=lambda c: cv2.boundingRect(c)[0])
        sorted_contours.append(sorted_row)
        
    flat_contours = [c for row in sorted_contours for c in row]

    count = 0
    for cnt in flat_contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Filter out small regions (noise)
        if w < 40 or h < 20:
            continue

        word_img = image[y:y+h, x:x+w]
        file_path = os.path.join(output_dir, f"{count}.jpg")
        cv2.imwrite(file_path, word_img)

        # Draw bounding box
        cv2.rectangle(image_copy, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cv2.putText(image_copy, str(count), (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

        count += 1

    # Save the preview image with boxes
    cv2.imwrite(boxed_output_path, image_copy)
    print(f"Saved {count} word images to '{output_dir}'")
    # print(f"Boxed preview saved to '{boxed_output_path}'")

if __name__ == "__main__":
    from tqdm import tqdm
    from mltu.configs import BaseModelConfigs

    configs = BaseModelConfigs.load("Models/03_handwriting_recognition/202301111911/configs.yaml")

    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
    else:
        image_path = '3nkfIT7.jpg'
        
    segment_and_save_words(image_path)
    
    # 1. Load all your own test images from a folder (adjust path as needed)
    image_paths = glob.glob("segmented_words/*.jpg")  # or *.jpg, etc.
    
    image_paths = sorted(image_paths, key=lambda path: int(os.path.splitext(os.path.basename(path))[0]))

    # 2. Optional: if you have ground truth labels, define them here
    # Example: {"my_images/img1.png": "hello", ...}
    ground_truth = {}  # Leave empty if you're just testing

    accum_cer = []

    for image_path in tqdm(image_paths):
        image = cv2.imread(image_path)
        prediction_text = model.predict(image)

        label = ground_truth.get(image_path, "[N/A]")  # fallback if no label
        cer = get_cer(prediction_text, label) if label != "[N/A]" else None

        # print(f"Image: {image_path}, Prediction: {prediction_text}, CER: {cer}")
        print(prediction_text, end=" ")

        if cer is not None:
            accum_cer.append(cer)

        # # Optional: show image
        # image = cv2.resize(image, (image.shape[1] * 4, image.shape[0] * 4))
        # cv2.imshow("Image", image)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

    if accum_cer:
        print(f"Average CER: {np.average(accum_cer)}")

    subprocess.run(["rm", "-r", "segmented_words"])