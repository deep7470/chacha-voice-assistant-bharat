# interactive_object_detection.py
# ----------------------------------------------------------
# Interactive object detection for Chacha (on-demand + live mode)
# - Camera starts only on demand (start_camera_background)
# - ask_and_describe(): one-shot analyze current view
# - start_continuous_inspect(): run continuous live descriptions until stopped
# ----------------------------------------------------------

import threading
import time
import cv2
import numpy as np
from ultralytics import YOLO
import os
from voice import say
import traceback

# optional Gemini shorthand
try:
    import gemini_ai
except Exception:
    gemini_ai = None

# CONFIG
MODEL_PATH = "yolov8n.pt"
CAMERA_INDEX = 0
MAX_FRAME_AGE = 2.0         # seconds
UPSCALE_FACTOR = 2
CONF_THRESHOLD = 0.25
SMALL_OBJ_CONF = 0.20
IN_HAND_IOU = 0.15
MIN_CONF_FOR_DESCRIPTION = 0.35
CONTINUOUS_INTERVAL = 2.0   # seconds between spoken updates in continuous mode
REPEAT_COOLDOWN = 6.0       # seconds to avoid repeating same object

# Globals
_latest_frame = None
_latest_frame_ts = 0.0
_capture_thread = None
_capture_running = False
_capture_lock = threading.Lock()

_inspect_thread = None
_inspect_running = False
_inspect_lock = threading.Lock()
_last_spoken_object = None
_last_spoken_ts = 0.0

yolo_model = None

# Load model
try:
    yolo_model = YOLO(MODEL_PATH)
    print("✅ Interactive YOLO model loaded.")
except Exception as e:
    print("❌ Could not load YOLO model:", e)
    yolo_model = None


def _camera_loop():
    global _latest_frame, _latest_frame_ts, _capture_running
    try:
        cap = cv2.VideoCapture(CAMERA_INDEX)
        if not cap.isOpened():
            say("Camera accessible nahi hai.")
            _capture_running = False
            return
        _capture_running = True
        while _capture_running:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.03)
                continue
            with _capture_lock:
                _latest_frame = frame.copy()
                _latest_frame_ts = time.time()
            time.sleep(0.02)
    except Exception as e:
        print("Camera loop error:", e)
        traceback.print_exc()
    finally:
        try:
            cap.release()
        except Exception:
            pass
        _capture_running = False


def start_camera_background():
    """Start camera in background (safe to call multiple times)."""
    global _capture_thread, _capture_running
    if _capture_running:
        return
    _capture_thread = threading.Thread(target=_camera_loop, daemon=True)
    _capture_thread.start()
    # warm-up little
    t0 = time.time()
    while time.time() - t0 < 1.0 and _latest_frame is None:
        time.sleep(0.05)


def stop_camera_background():
    global _capture_running
    _capture_running = False


def _get_latest_frame():
    global _latest_frame, _latest_frame_ts
    with _capture_lock:
        if _latest_frame is None:
            return None
        if time.time() - _latest_frame_ts > MAX_FRAME_AGE:
            return None
        return _latest_frame.copy()


def _detect_on_image(img, imgsz=640, conf=CONF_THRESHOLD):
    results = []
    if yolo_model is None:
        return results
    try:
        res = yolo_model(img, imgsz=imgsz, conf=conf, verbose=False)
        r = res[0]
        boxes = getattr(r, "boxes", None)
        names = getattr(r, "names", {})
        if boxes is None:
            return results
        for b in boxes:
            try:
                conf_score = float(b.conf[0])
                cls_id = int(b.cls[0])
                label = names.get(cls_id, str(cls_id))
                x1, y1, x2, y2 = map(int, b.xyxy[0].tolist())
                area = max(1, (x2 - x1) * (y2 - y1))
                results.append({
                    "name": label,
                    "conf": conf_score,
                    "bbox": (x1, y1, x2, y2),
                    "area": area
                })
            except Exception:
                continue
    except Exception as e:
        print("YOLO error:", e)
    return results


def _multi_scale_detect(frame):
    detections = _detect_on_image(frame, imgsz=640, conf=CONF_THRESHOLD)
    try:
        h, w = frame.shape[:2]
        up = cv2.resize(frame, (w * UPSCALE_FACTOR, h * UPSCALE_FACTOR), interpolation=cv2.INTER_LINEAR)
        small_dets = _detect_on_image(up, imgsz=1024, conf=SMALL_OBJ_CONF)
        for d in small_dets:
            x1, y1, x2, y2 = d["bbox"]
            d["bbox"] = (int(x1 / UPSCALE_FACTOR), int(y1 / UPSCALE_FACTOR),
                         int(x2 / UPSCALE_FACTOR), int(y2 / UPSCALE_FACTOR))
        detections.extend(small_dets)
    except Exception as e:
        pass

    # dedupe by IoU, keep highest conf
    merged = []
    detections_sorted = sorted(detections, key=lambda x: -x["conf"])
    for d in detections_sorted:
        x1, y1, x2, y2 = d["bbox"]
        area = d["area"]
        keep = True
        for m in merged:
            mx1, my1, mx2, my2 = m["bbox"]
            ix1 = max(x1, mx1); iy1 = max(y1, my1)
            ix2 = min(x2, mx2); iy2 = min(y2, my2)
            iw = max(0, ix2 - ix1); ih = max(0, iy2 - iy1)
            inter = iw * ih
            union = area + m["area"] - inter
            iou = inter / union if union > 0 else 0
            if iou > 0.45:
                keep = False
                break
        if keep:
            merged.append(d)
    return merged


def _choose_relevant_object(detections, frame):
    if not detections:
        return None
    persons = [d for d in detections if d["name"].lower() == "person"]
    others = [d for d in detections if d["name"].lower() != "person"]
    if not others:
        return max(persons, key=lambda x: x["conf"]) if persons else None
    def score(o):
        return o["conf"] * (1 + (o["area"] / (frame.shape[0] * frame.shape[1])) * 5)
    chosen = max(others, key=score)
    if persons:
        p = persons[0]
        px1, py1, px2, py2 = p["bbox"]
        ox1, oy1, ox2, oy2 = chosen["bbox"]
        ix1 = max(px1, ox1); iy1 = max(py1, oy1)
        ix2 = min(px2, ox2); iy2 = min(py2, oy2)
        iw = max(0, ix2 - ix1); ih = max(0, iy2 - iy1)
        inter = iw * ih
        obj_area = (ox2 - ox1) * (oy2 - oy1)
        overlap_frac = inter / obj_area if obj_area > 0 else 0
        chosen["in_person_region"] = overlap_frac > IN_HAND_IOU
    else:
        chosen["in_person_region"] = False
    return chosen


def _describe_with_gemini(name):
    if gemini_ai and hasattr(gemini_ai, "get_gemini_response"):
        try:
            prompt = f"Briefly describe what a {name} is and one common use in one short sentence."
            resp = gemini_ai.get_gemini_response(prompt, speak=False)
            if resp and resp != "error":
                return resp
        except Exception as e:
            pass
    return f"A {name}."


def ask_and_describe():
    frame = _get_latest_frame()
    if frame is None:
        say("Camera ready nahi hai. Kripya 'camera on' karke fir se kaho.")
        return
    say("Theek hai, dekh raha hoon.")
    time.sleep(0.4)
    # gather detections from a few frames to be robust
    candidates = []
    for _ in range(3):
        f = _get_latest_frame()
        if f is None:
            continue
        dets = _multi_scale_detect(f)
        candidates.extend(dets)
        time.sleep(0.15)
    # choose best from aggregated list
    merged = {}
    for d in candidates:
        key = (d["name"], d["bbox"])
        if key not in merged or d["conf"] > merged[key]["conf"]:
            merged[key] = d
    detections = list(merged.values())
    chosen = _choose_relevant_object(detections, frame)
    if not chosen:
        say("Mujhe kuch clearly nazar nahi aaya. Thoda paas laakar dikhaiye.")
        return
    name = chosen["name"]
    conf = chosen["conf"]
    in_hand = chosen.get("in_person_region", False)
    if conf < MIN_CONF_FOR_DESCRIPTION:
        say(f"Mujhe pura pakka nahi lag raha (confidence {int(conf*100)}%). Kripya thoda paas laake dikhaiye.")
        return
    if in_hand:
        lead = f"Yeh aapke haath mein lagta hai. Yeh {name} hai."
    else:
        lead = f"Yeh yahan nazar aa raha hai. Yeh {name} hai."
    desc = _describe_with_gemini(name)
    say(f"{lead} {desc}")
    # update last spoken
    global _last_spoken_object, _last_spoken_ts
    _last_spoken_object = name
    _last_spoken_ts = time.time()


def _continuous_inspect_loop():
    global _inspect_running, _last_spoken_object, _last_spoken_ts
    _inspect_running = True
    say("Continuous detect mode shuru kar diya. Mujhe 'band karo' bolo rokne ke liye.")
    try:
        while _inspect_running:
            frame = _get_latest_frame()
            if frame is None:
                time.sleep(0.5)
                continue
            dets = _multi_scale_detect(frame)
            chosen = _choose_relevant_object(dets, frame)
            if chosen:
                name = chosen["name"]
                conf = chosen["conf"]
                now = time.time()
                should_speak = False
                if conf >= MIN_CONF_FOR_DESCRIPTION:
                    if _last_spoken_object != name:
                        should_speak = True
                    else:
                        if now - _last_spoken_ts > REPEAT_COOLDOWN:
                            should_speak = True
                if should_speak:
                    in_hand = chosen.get("in_person_region", False)
                    if in_hand:
                        lead = f"Yeh aapke haath mein lagta hai. Yeh {name} hai."
                    else:
                        lead = f"Yeh yahan nazar aa raha hai. Yeh {name} hai."
                    desc = _describe_with_gemini(name)
                    say(f"{lead} {desc}")
                    _last_spoken_object = name
                    _last_spoken_ts = now
            time.sleep(CONTINUOUS_INTERVAL)
    except Exception as e:
        print("Inspect loop error:", e)
    finally:
        _inspect_running = False
        say("Continuous detect mode band kar diya.")


def start_continuous_inspect():
    global _inspect_thread, _inspect_running
    if _inspect_running:
        say("Continuous detect pehle se chal raha hai.")
        return
    start_camera_background()
    _inspect_thread = threading.Thread(target=_continuous_inspect_loop, daemon=True)
    _inspect_thread.start()


def stop_continuous_inspect():
    global _inspect_running
    _inspect_running = False


# small demo support if run directly
if __name__ == "__main__":
    start_camera_background()
    say("Interactive detection ready. Bolo 'Chacha, ye kya hai' ya 'continue detecting' shuru karne ke liye.")
    try:
        while True:
            time.sleep(0.2)
    except KeyboardInterrupt:
        stop_camera_background()
        stop_continuous_inspect()
        say("Interactive detection stopped.")
