import cv2
import typing
import numpy as np
import glob
import subprocess
import os
import sys
import shutil

from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder, get_cer
from tqdm import tqdm
from mltu.configs import BaseModelConfigs
from WordDetectorModel.src.infer import main

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

def predict_handwriting(folder_path):
    configs = BaseModelConfigs.load("models/configs.yaml")
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    main(folder_path)
    
    # Load images
    image_paths = glob.glob(f"{folder_path}/isolated_words/*.png") 
    
    image_paths = sorted(image_paths, key=lambda path: int(os.path.splitext(os.path.basename(path))[0]))

    prediction_str = ""

    # Predict each image
    for image_path in tqdm(image_paths):
        image = cv2.imread(image_path)
        prediction_text = model.predict(image)

        prediction_str += prediction_text + " "
        print(prediction_text, end=" ")

    shutil.rmtree(f"{folder_path}/isolated_words")

    return prediction_str.strip()