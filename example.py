"""
Pemrosesan video menggunakan GazeTracking.
Script ini menjaga logika demo asli namun membaca dari berkas video dan
menuliskan ringkasan hasil ke file JSON.
"""

import argparse
import json
import os

import cv2
from gaze_tracking import GazeTracking


def classify_frame(gaze):
    """Terapkan logika demo: blinking = tidak curang, kiri/kanan = curang."""
    if gaze.is_blinking():
        return "No Cheating"
    if gaze.is_right() or gaze.is_left():
        return "Cheating"
    if gaze.is_center():
        return "No Cheating"


def process_video(video_path):
    gaze = GazeTracking()
    capture = cv2.VideoCapture(video_path)

    if not capture.isOpened():
        raise ValueError(f"Tidak dapat membuka video: {video_path}")

    stats = {"cheating": 0, "tidak_cheating": 0}
    total_frames = 0

    while True:
        grabbed, frame = capture.read()
        if not grabbed:
            break

        total_frames += 1
        gaze.refresh(frame)
        label = classify_frame(gaze)

        if label == "Cheating":
            stats["cheating"] += 1
        elif label == "No Cheating":
            stats["tidak_cheating"] += 1


    capture.release()
    return total_frames, stats


def _default_video_path():
    """Cari video pertama di folder video_demo bila argumen tidak diberikan."""
    base_dir = os.path.join(os.path.dirname(__file__), "video_demo")
    if not os.path.isdir(base_dir):
        raise FileNotFoundError("Folder video_demo tidak ditemukan.")

    for filename in os.listdir(base_dir):
        if filename.lower().endswith((".mp4", ".webm", ".avi", ".mov", ".mkv")):
            return os.path.join(base_dir, filename)
    raise FileNotFoundError("Tidak ada berkas video di folder video_demo.")


def main():
    parser = argparse.ArgumentParser(description="Analisis video GazeTracking.")
    parser.add_argument(
        "--video",
        help="Path ke berkas video. Jika tidak diberikan, diambil otomatis dari folder video_demo.",
    )
    parser.add_argument(
        "--output",
        default="hasil_eye_cheating_detection.json",
        help="Nama file output JSON (default: hasil_gaze.json).",
    )
    args = parser.parse_args()

    video_path = args.video or _default_video_path()
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Berkas video tidak ditemukan: {video_path}")

    total_frames, stats = process_video(video_path)

    def _percent(count):
        return round((count / total_frames) * 100, 2) if total_frames else 0.0

    cheating_detected = stats["cheating"] > stats["tidak_cheating"]

    hasil = {
        "video": os.path.abspath(video_path),
        "total_frames": total_frames,
        "total_cheating": stats["cheating"],
        #"persen_cheating": _percent(stats["cheating"]),
        "total_tidak_cheating": stats["tidak_cheating"],
        #"persen_tidak_cheating": _percent(stats["tidak_cheating"]),
        "cheating_detected": cheating_detected,
    }

    with open(args.output, "w", encoding="utf-8") as output_file:
        json.dump(hasil, output_file, indent=2)

    print(f"Analisis selesai.")
    print(f"Ringkasan tersimpan di {args.output}.")


if __name__ == "__main__":
    main()
