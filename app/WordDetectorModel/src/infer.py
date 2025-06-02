import argparse
from path import Path
import torch
import cv2

from WordDetectorModel.src.dataloader import DataLoaderImgFile
from WordDetectorModel.src.eval import evaluate
from WordDetectorModel.src.net import WordDetectorNet
from WordDetectorModel.src.visualization import visualize


def enlarge_box(aabb, padding, img_shape):
    h, w = img_shape
    xmin = max(int(aabb.xmin) - padding, 0)
    xmax = min(int(aabb.xmax) + padding, w)
    ymin = max(int(aabb.ymin) - padding, 0)
    ymax = min(int(aabb.ymax) + padding, h)
    return (xmin, xmax, ymin, ymax)

def sort_aabbs_into_rows(aabbs, row_threshold=0.8):
    """
    Sort AABBs into rows (top to bottom) and then left-to-right within each row.
    """
    rows = {}
    row_idx = 0

    def center_y(aabb): return (aabb.ymin + aabb.ymax) / 2
    def center_x(aabb): return (aabb.xmin + aabb.xmax) / 2
    def height(aabb): return aabb.ymax - aabb.ymin

    for box in sorted(aabbs, key=lambda b: center_y(b)):
        mid_y1 = center_y(box)
        h1 = height(box)
        found_row = False

        for key in sorted(rows.keys()):
            mid_y2 = center_y(rows[key][0])
            h2 = height(rows[key][0])
            if abs(mid_y1 - mid_y2) < (h1 + h2) / 2 * row_threshold:
                rows[key].append(box)
                found_row = True
                break

        if not found_row:
            rows[row_idx] = [box]
            row_idx += 1

    sorted_rows = []
    for i in range(row_idx):
        sorted_row = sorted(rows[i], key=lambda b: center_x(b))
        sorted_rows.extend(sorted_row)

    return sorted_rows


def main(folder_path):
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', choices=['cpu', 'cuda'], default='cpu')
    args = parser.parse_args()

    net = WordDetectorNet()
    net.load_state_dict(torch.load('WordDetectorModel/model/weights', map_location=args.device))
    net.eval()
    net.to(args.device)

    loader = DataLoaderImgFile(Path(folder_path), net.input_size, args.device)
    res = evaluate(net, loader, max_aabbs=1000)

    crop_output_dir = Path(f'{folder_path}/isolated_words')
    crop_output_dir.makedirs_p()

    word_counter = 0

    for i, (img, aabbs) in enumerate(zip(res.batch_imgs, res.batch_aabbs)):
        scale = loader.get_scale_factor(i)
        aabbs = [aabb.scale(1 / scale, 1 / scale) for aabb in aabbs]
        img = loader.get_original_img(i)

        # Sort AABBs into reading order
        sorted_aabbs = sort_aabbs_into_rows(aabbs)

        # Save each word with padding
        for aabb in sorted_aabbs:
            xmin, xmax, ymin, ymax = enlarge_box(aabb, padding=5, img_shape=img.shape)
            cropped = ((img + 0.5) * 255).astype('uint8')[ymin:ymax, xmin:xmax]
            cv2.imwrite(str(crop_output_dir / f'{word_counter}.png'), cropped)
            word_counter += 1
