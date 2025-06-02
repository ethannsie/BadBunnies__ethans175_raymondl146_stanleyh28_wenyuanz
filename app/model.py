# Flask + Jinja
from flask import Flask, render_template, request, redirect, url_for, session, flash

# Password hashing
from werkzeug.security import generate_password_hash, check_password_hash

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

def preprocess_image_denoised(pil_img):
    img = np.array(pil_img.convert("L"))
    denoised = cv2.fastNlMeansDenoising(img, None, h=30, templateWindowSize=7, searchWindowSize=21)
    
    adaptive_thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    return adaptive_thresh

def remove_specks(binary_img):
    # Median blur smooths isolated specks
    median = cv2.medianBlur(binary_img, 3)
    
    # Remove tiny components
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(median, connectivity=8)
    result = np.zeros_like(binary_img)
    
    for i in range(1, num_labels):  # skip background
        area = stats[i, cv2.CC_STAT_AREA]
        if area >= 20:  # keep only real character-sized blobs
            result[labels == i] = 255
    return result

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
        area = w * h
        if 100 < area < 5000 and h > 10 and w > 3:
            bounding_boxes.append((x, y, w, h))

    bounding_boxes.sort(key=lambda box: (box[1] // 50, box[0]))
    return bounding_boxes

def draw_character_boxes(img, boxes, labels=None):
    img_copy = cv2.cvtColor(img.copy(), cv2.COLOR_GRAY2BGR)

    for i, (x, y, w, h) in enumerate(boxes):
        cv2.rectangle(img_copy, (x, y), (x + w, y + h), (0, 255, 0), 1)
        label = str(labels[i]) if labels and i < len(labels) else str(i)
        cv2.putText(img_copy, label, (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.2, (0, 255, 0), 1)

    plt.figure(figsize=(10, 12))
    plt.imshow(cv2.cvtColor(img_copy, cv2.COLOR_BGR2RGB))
    plt.title("Detected Characters")
    plt.axis("off")
    plt.show()

# === Main Pipeline ===
img_list = pdf_to_images('sample.pdf')
img = img_list[0]

# Preprocessing with denoising and speck removal
thresh_img = preprocess_image_denoised(img)
img_cleaned = remove_specks(thresh_img)

char_boxes = find_characters(img_cleaned)
draw_character_boxes(img_cleaned, char_boxes)
