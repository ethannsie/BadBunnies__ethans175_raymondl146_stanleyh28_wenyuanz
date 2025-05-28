"""
Train a YOLOv8 detector+classifier for handwritten characters.
Author: Bad Bunnies – Cipher project
"""

from ultralytics import YOLO
import string
import argparse
from pathlib import Path

CHAR_CLASSES = list(string.digits + string.ascii_lowercase + string.ascii_uppercase)  # 62

def main(data_yaml: str, epochs: int = 50, img_size: int = 640, batch: int = 16):
    """Train and export a YOLOv8 model on handwritten characters."""
    # 1. load a small YOLOv8 backbone (n = nano, s = small, m = medium …)
    model = YOLO("runs/cipher/yolov8n-80ep19/weights/last.pt") # you can swap for yolov8s.pt for higher accuracy
    # model = YOLO("runs/cipher/yolov8n-80ep16/weights/last.pt")  # resume         

    # 2. train
    results = model.train(
        data=data_yaml,      # e.g. "handwriting.yaml"
        imgsz=img_size,
        epochs=epochs,
        batch=batch,
        workers=8,
        degrees=10,         # Random rotation between -10 to 10 degrees
        perspective=0.001,  # Slight perspective warping (optional)
        project="runs/cipher",
        name=f"yolov8n-{epochs}ep",
        resume=True,
        device="cpu"
    )

    # 3. best weights path
    best = Path(results.save_dir) / "weights" / "best.pt"
    print(f"\n✅ Training done! Best weights saved to: {best.resolve()}\n")

    # 4. (optional) run quick test inference
    sample = Path(model.train_args.data).parent / "images" / "test"
    sample_img = next(sample.glob("*.*"), None)
    if sample_img:
        results = model(str(best))(str(sample_img), conf=0.25)
        results[0].show()
        print("Predicted boxes / classes:", results[0].boxes)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="handwriting.yaml", help="Path to dataset YAML")
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--batch", type=int, default=16)
    args = parser.parse_args()
    main(args.data, args.epochs, args.imgsz, args.batch)
