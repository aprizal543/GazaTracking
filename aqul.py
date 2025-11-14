import argparse
import json
import os

import cv2
from gaze_tracking import GazeTracking


def classify_gaze(gaze_analyzer):
    """Mirror the demo logic to determine cheating/non-cheating labels."""
    if gaze_analyzer.is_blinking():
        return "No Cheating"
    if gaze_analyzer.is_right() or gaze_analyzer.is_left():
        return "Cheating"
    if gaze_analyzer.is_center():
        return "No Cheating"
    return "Unknown"


def process_video(video_path):
    gaze = GazeTracking()
    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(f"Tidak bisa membuka video: {video_path}")

    frame_index = 0
    stats = {"cheating": 0, "tidak_cheating": 0, "unknown": 0}

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        frame_index += 1
        gaze.refresh(frame)
        label = classify_gaze(gaze)

        if label == "Cheating":
            stats["cheating"] += 1
        elif label == "No Cheating":
            stats["tidak_cheating"] += 1
        else:
            stats["unknown"] += 1

    capture.release()
    return frame_index, stats


def main():
    parser = argparse.ArgumentParser(description="Analisis video menggunakan GazeTracking.")
    parser.add_argument("--video", required=True, help="Path ke berkas video yang ingin diproses.")
    parser.add_argument("--output", default="hasil_gaze.json", help="Nama file output JSON.")
    args = parser.parse_args()

    video_path = args.video
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Berkas video tidak ditemukan: {video_path}")

    total_frames, stats = process_video(video_path)

    result = {
        "video": os.path.abspath(video_path),
        "total_frames": total_frames,
        "total_cheating": stats["cheating"],
        "total_tidak_cheating": stats["tidak_cheating"],
        "total_unknown": stats["unknown"],
    }

    with open(args.output, "w", encoding="utf-8") as json_file:
        json.dump(result, json_file, indent=2)

    print(f"Hasil disimpan di {args.output}")


if __name__ == "__main__":
    main()
