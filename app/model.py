# Flask + Jinja
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Password hashing
from werkzeug.security import generate_password_hash, check_password_hash
# OR: from argon2 import PasswordHasher

# File + time utils
import os
import hashlib
from datetime import datetime

# Image processing
from PIL import Image
import cv2
import fitz  # PyMuPDF

# Machine learning
import torch
import torchvision.transforms as transforms
from sklearn.model_selection import train_test_split

# Hugging Face transformers + LoRA
from transformers import TrOCRProcessor, VisionEncoderDecoderModel
from peft import get_peft_model, LoraConfig, TaskType

import numpy as np
import matplotlib.pyplot as plt

def pdf_to_images(pdf_path):
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        pix = page.get_pixmap()
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    return images

def preprocess_image(pil_img):
    img = np.array(pil_img.convert("L"))  # Convert to grayscale (0-255)
    _, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return thresh  # binary image: text = white (255), background = black (0)

def show_image(img, title="Image", cmap="gray"):
    plt.figure(figsize=(8, 10))
    plt.imshow(img, cmap=cmap)
    plt.title(title)
    plt.axis("off")
    plt.show()
    
def find_characters(img):
    contours, _ = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    bounding_boxes = []

    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        if h > 1 and w > 1:  # Filter noise
            bounding_boxes.append((x, y, w, h))

    # Sort: top-to-bottom, then left-to-right
    bounding_boxes.sort(key=lambda box: (box[1] // 50, box[0]))
    return bounding_boxes

def draw_character_boxes(img, boxes, labels=None):
    img_copy = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)  # Convert to color for drawing

    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 1)  # Green box
        label = str(labels[i]) if labels and i < len(labels) else str(i)
        cv2.putText(img_copy, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 255, 0), 1)

    plt.figure(figsize=(10, 12))
    plt.imshow(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
    plt.title("Detected Characters")
    plt.axis("off")
    plt.show()

img_list = pdf_to_images('sample.pdf')
img = img_list[0]
new_img = preprocess_image(img)
char_boxes = find_characters(new_img)
draw_character_boxes(new_img, char_boxes)