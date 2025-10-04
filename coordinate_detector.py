import cv2
import mediapipe as mp
import math

mp_pose = mp.solutions.pose
LANDMARKS = mp_pose.PoseLandmark

from config import LOGS_DIR

# Your full MAPPING dictionary here (same as you shared)
# MAPPING = { ... }  # ← Paste your full location mapping here
# MAPPING = {
#     "FULL-BACK": {
#         "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
#         "method": "midpoint",
#         "y_offset": -50
#     },
#     "FULL-FRONT": {
#         "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
#         "method": "midpoint",
#         "y_offset": 170
#     },
#     "LEFT-BICEP": {
#         "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW"],
#         "method": "midpoint"
#     },
#     "RIGHT-BICEP": {
#         "landmarks": ["RIGHT_SHOULDER", "RIGHT_ELBOW"],
#         "method": "midpoint"
#     },
#     "LEFT-CHEST": {
#         "landmarks": ["LEFT_SHOULDER", "NOSE"],
#         "method": "weighted",
#         "alpha": 0.5,
#         "y_offset": 310
#     },
#     "RIGHT-CHEST": {
#         "landmarks": ["RIGHT_SHOULDER", "NOSE"],
#         "method": "weighted",
#         "alpha": 0.5,
#         "y_offset": 310
#     },
#     "LEFT-COLLAR": {
#         "landmarks": ["LEFT_SHOULDER"],
#         "method": "single",
#         "x_offset": -164,  # Shift left to match target x=743
#         "y_offset": -156  # Shift upward to match target y=490
#     },
#     "RIGHT-COLLAR": {
#         "landmarks": ["RIGHT_SHOULDER"],
#         "method": "single",
#         "x_offset": 173,  # Shift right to match target x=504
#         "y_offset": -116  # Shift upward to match target y=483
#     },
#     "LEFT-CUFF": {
#         "landmarks": ["LEFT_WRIST"],
#         "method": "single",
#         "x_offset": -10,  # Shift left to match target x=985
#         "y_offset": 2    # Shift to match target y=1545
#     },
#     "RIGHT-CUFF": {
#         "landmarks": ["RIGHT_WRIST"],
#         "method": "single",
#         "x_offset": -11,  # Shift left to match target x=219
#         "y_offset": -16   # Shift upward to match target y=1388
#     },
#     "LEFT-HIP": {
#         "landmarks": ["LEFT_HIP"],
#         "method": "single"
#     },
#     "RIGHT-HIP": {
#         "landmarks": ["RIGHT_HIP"],
#         "method": "single"
#     },
#     "LEFT-SLEEVE": {
#         "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW"],
#         "method": "weighted",
#         "alpha": 0.7,
#         "x_offset": 42,
#         "y_offset": -48
#     },
#     "RIGHT-SLEEVE": {
#         "landmarks": ["RIGHT_SHOULDER", "RIGHT_ELBOW"],
#         "method": "weighted",
#         "alpha": 0.7,
#         "x_offset": -9,
#         "y_offset": -46
#     },
#     "LEFT-THIGH-HIGH": {
#         "landmarks": ["LEFT_HIP", "LEFT_KNEE"],
#         "method": "weighted",
#         "alpha": 0.3
#     },
#     "RIGHT-THIGH-HIGH": {
#         "landmarks": ["RIGHT_HIP", "RIGHT_KNEE"],
#         "method": "weighted",
#         "alpha": 0.3
#     },
#     "ON-POCKET": {
#         "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
#         "method": "midpoint",
#         "x_offset": 220,
#         "y_offset": -634
#     },
#     "BACK-YOKE": {
#         "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
#         "method": "midpoint",
#         "x_offset": -21,
#         "y_offset": -87
#     },
#     "FRONT-CROWN": {
#         "landmarks": ["NOSE"],
#         "method": "single",
#         "y_offset": -100
#     },
#     "CAP-BACK": {
#         "landmarks": ["NOSE"],
#         "method": "single",
#         "y_offset": -150
#     },
#     "CAP-SIDE": {
#         "landmarks": ["LEFT_EAR"],
#         "method": "single",
#         "x_offset": 50
#     },
#     "CAP-FRONT-SIDE": {
#         "landmarks": ["LEFT_EYE"],
#         "method": "single",
#         "x_offset": 30,
#         "y_offset": -80
#     },
#     "LOWER-LEFT-CROWN": {
#         "landmarks": ["NOSE", "LEFT_EYE"],
#         "method": "weighted",
#         "alpha": 0.5,
#         "y_offset": -50
#     },
#     "LOWER-RIGHT-CROWN": {
#         "landmarks": ["NOSE", "RIGHT_EYE"],
#         "method": "weighted",
#         "alpha": 0.5,
#         "y_offset": -50
#     },
#     "Corner-Angled-Towel": {
#         "landmarks": ["LEFT_HIP"],
#         "method": "single",
#         "x_offset": 100,
#         "y_offset": 200
#     },
#     "FRONT_CENTER": {
#         "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
#         "method": "midpoint",
#         "y_offset": 200
#     },
#     "FRONT (ON BAG)": {
#         "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
#         "method": "midpoint",
#         "y_offset": 100
#     },
#     "ON POCKET (ON BAG)": {
#         "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
#         "method": "midpoint",
#         "y_offset": 200
#     }
# }

MAPPING = {
    "FULL-BACK": {
        "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
        "method": "midpoint",
        "x_offset": -7,     # move left
        "y_offset": 80     # move downward
    },
    "FULL-FRONT": {
        "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
        "method": "midpoint",
        "y_offset": 170
    },
    "LEFT-BICEP": {
        "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW"],
        "method": "midpoint",
        "x_offset": 42,    # shift right
        "y_offset": -35    # shift upward
    },
    "RIGHT-BICEP": {
        "landmarks": ["RIGHT_SHOULDER", "RIGHT_ELBOW"],
        "method": "midpoint",
        "x_offset": -71,   # shift left
        "y_offset": -13    # shift upward
    },
    "LEFT-CHEST": {
        "landmarks": ["LEFT_SHOULDER", "NOSE"],
        "method": "weighted",
        "alpha": 0.5,        # Keep midpoint between shoulder & nose
        "x_offset": 0,      # Push right
        "y_offset": 250      # Push upward
    },
    "RIGHT-CHEST": {
        "landmarks": ["RIGHT_SHOULDER", "NOSE"],
        "method": "weighted",
        "alpha": 0.5,
        "x_offset": -13,   # shift left
        "y_offset": 261    # 310 - 49 = 261 (shift upward)
    },
    "LEFT-COLLAR": {
        "landmarks": ["LEFT_SHOULDER"],
        "method": "single",
        "x_offset": -189,   # -164 - 25
        "y_offset": -100    # -156 + 5
    },
    "RIGHT-COLLAR": {
        "landmarks": ["RIGHT_SHOULDER"],
        "method": "single",
        "x_offset": 185,  # Shift right to match target x=504
        "y_offset": -110  # Shift upward to match target y=483
    },
    "LEFT-CUFF": {
        "landmarks": ["LEFT_WRIST"],
        "method": "single",
        "x_offset": -10,  # Shift left to match target x=985
        "y_offset": 2    # Shift to match target y=1545
    },
    "RIGHT-CUFF": {
        "landmarks": ["RIGHT_WRIST"],
        "method": "single",
        "x_offset": -11,  # Shift left to match target x=219
        "y_offset": -16   # Shift upward to match target y=1388
    },
    "LEFT-HIP": {
        "landmarks": ["LEFT_HIP"],
        "method": "single"
    },
    "RIGHT-HIP": {
        "landmarks": ["RIGHT_HIP"],
        "method": "single"
    },
    "LEFT-SLEEVE": {
        "landmarks": ["LEFT_SHOULDER", "LEFT_ELBOW"],
        "method": "weighted",
        "alpha": 0.7,
        "x_offset": 42,
        "y_offset": -48
    },
    "RIGHT-SLEEVE": {
        "landmarks": ["RIGHT_SHOULDER", "RIGHT_ELBOW"],
        "method": "weighted",
        "alpha": 0.7,
        "x_offset": -9,
        "y_offset": -46
    },
    "LEFT-THIGH-HIGH": {
        "landmarks": ["LEFT_HIP", "LEFT_KNEE"],
        "method": "weighted",
        "alpha": 0.2
    },
    "RIGHT-THIGH-HIGH": {
        "landmarks": ["RIGHT_HIP", "RIGHT_KNEE"],
        "method": "weighted",
        "alpha": 0.2
    },
    "ON-POCKET": {
        "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
        "method": "midpoint",
        "x_offset": 220,
        "y_offset": -634
    },
    "BACK-YOKE": {
        "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
        "method": "midpoint",
        "x_offset": -21,
        "y_offset": -87
    },
    "FRONT-CROWN": { #BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["NOSE"],
        "method": "single",
        "y_offset": -100
    },
    "CAP-BACK": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["NOSE"],
        "method": "single",
        "y_offset": -150
    },
    "CAP-SIDE": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_EAR"],
        "method": "single",
        "x_offset": 50
    },
    "CAP-FRONT-SIDE": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_EYE"],
        "method": "single",
        "x_offset": 30,
        "y_offset": -80
    },
    "LOWER-LEFT-CROWN": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["NOSE", "LEFT_EYE"],
        "method": "weighted",
        "alpha": 0.5,
        "y_offset": -50
    },
    "LOWER-RIGHT-CROWN": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["NOSE", "RIGHT_EYE"],
        "method": "weighted",
        "alpha": 0.5,
        "y_offset": -50
    },
    "Corner-Angled-Towel": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_HIP"],
        "method": "single",
        "x_offset": 100,
        "y_offset": 200
    },
    "FRONT_CENTER": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_SHOULDER", "RIGHT_SHOULDER"],
        "method": "midpoint",
        "y_offset": 200
    },
    "FRONT (ON BAG)": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
        "method": "midpoint",
        "y_offset": 100
    },
    "ON POCKET (ON BAG)": {#BAKIIIIIIIIIIIIIIIIIIII
        "landmarks": ["LEFT_HIP", "RIGHT_HIP"],
        "method": "midpoint",
        "y_offset": 200
    }
}

def get_logo_scale(image_path, location_name, base_logo_size=(200, 100)):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found!")

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            raise ValueError("No person detected!")

        landmarks = results.pose_landmarks.landmark
        h, w, _ = image.shape

        if location_name in ["LEFT-BICEP", "RIGHT-BICEP", "LEFT-SLEEVE", "RIGHT-SLEEVE"]:
            if "LEFT" in location_name:
                p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
                p2 = landmarks[LANDMARKS.LEFT_ELBOW]
            else:
                p1 = landmarks[LANDMARKS.RIGHT_SHOULDER]
                p2 = landmarks[LANDMARKS.RIGHT_ELBOW]
        elif location_name in ["LEFT-CHEST", "RIGHT-CHEST"]:
            p1 = landmarks[LANDMARKS.NOSE]
            p2 = landmarks[LANDMARKS.LEFT_SHOULDER if "LEFT" in location_name else LANDMARKS.RIGHT_SHOULDER]
        elif location_name in ["FULL-FRONT", "FULL-BACK"]:
            p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
            p2 = landmarks[LANDMARKS.RIGHT_SHOULDER]
        else:
            return base_logo_size  # Default fallback

        dx = (p2.x - p1.x) * w
        dy = (p2.y - p1.y) * h
        distance = (dx**2 + dy**2)**0.5

        # Scale logo width to 60% of landmark distance, height proportionally
        scale_factor = distance / base_logo_size[0]
        new_width = int(base_logo_size[0] * scale_factor * 0.6)
        new_height = int(base_logo_size[1] * scale_factor * 0.6)
        return (new_width, new_height)


def get_arm_rotation_angle(image_path, location_name):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found!")

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            raise ValueError("No person detected!")

        landmarks = results.pose_landmarks.landmark

        if location_name == "LEFT-BICEP":
            p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
            p2 = landmarks[LANDMARKS.LEFT_ELBOW]
        elif location_name == "RIGHT-BICEP":
            p1 = landmarks[LANDMARKS.RIGHT_SHOULDER]
            p2 = landmarks[LANDMARKS.RIGHT_ELBOW]
        elif location_name == "LEFT-SLEEVE":
            p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
            p2 = landmarks[LANDMARKS.LEFT_ELBOW]
        elif location_name == "RIGHT-SLEEVE":
            p1 = landmarks[LANDMARKS.RIGHT_SHOULDER]
            p2 = landmarks[LANDMARKS.RIGHT_ELBOW]
        else:
            return 0  # No rotation needed

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        angle_rad = math.atan2(dy, dx)
        return math.degrees(angle_rad)


def get_rotation_angle(image_path, location_name):
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image not found!")

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            raise ValueError("No person detected!")

        landmarks = results.pose_landmarks.landmark

        if location_name == "LEFT-BICEP":
            p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
            p2 = landmarks[LANDMARKS.LEFT_ELBOW]
        elif location_name == "RIGHT-BICEP":
            p1 = landmarks[LANDMARKS.RIGHT_SHOULDER]
            p2 = landmarks[LANDMARKS.RIGHT_ELBOW]
        elif location_name == "LEFT-SLEEVE":
            p1 = landmarks[LANDMARKS.LEFT_SHOULDER]
            p2 = landmarks[LANDMARKS.LEFT_ELBOW]
        elif location_name == "RIGHT-SLEEVE":
            p1 = landmarks[LANDMARKS.RIGHT_SHOULDER]
            p2 = landmarks[LANDMARKS.RIGHT_ELBOW]
        else:
            return 0  # No rotation needed

        dx = p2.x - p1.x
        dy = p2.y - p1.y
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)
        return angle_deg

def get_location_coordinates(image_path, location_name, debug=False):
    image = cv2.imread(image_path)

    location_name = str(location_name).replace(" ","-").upper()

    if image is None:
        raise ValueError(f"Image not found: {image_path}")

    with mp_pose.Pose(static_image_mode=True) as pose:
        results = pose.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        if not results.pose_landmarks:
            raise ValueError("No person detected!")

        landmarks = results.pose_landmarks.landmark

        if location_name not in MAPPING:
            raise ValueError(f"Location '{location_name}' not mapped!")

        config = MAPPING[location_name]
        landmark_names = config["landmarks"]
        method = config["method"]
        alpha = config.get("alpha", 0.5)
        x_offset = config.get("x_offset", 0)
        y_offset = config.get("y_offset", 0)

        lm_coords = [(landmarks[getattr(LANDMARKS, name)].x,
                      landmarks[getattr(LANDMARKS, name)].y) for name in landmark_names]

        h, w, _ = image.shape
        if method == "single":
            x, y = lm_coords[0]
            x = int(x * w) + x_offset
            y = int(y * h) + y_offset
        elif method == "midpoint":
            x = sum(coord[0] for coord in lm_coords) / len(lm_coords)
            y = sum(coord[1] for coord in lm_coords) / len(lm_coords)
            x = int(x * w) + x_offset
            y = int(y * h) + y_offset
        elif method == "weighted":
            x = lm_coords[0][0] + alpha * (lm_coords[1][0] - lm_coords[0][0])
            y = lm_coords[0][1] + alpha * (lm_coords[1][1] - lm_coords[0][1])
            x = int(x * w) + x_offset
            y = int(y * h) + y_offset
        elif method == "average":
            x = sum(coord[0] for coord in lm_coords) / len(lm_coords)
            y = sum(coord[1] for coord in lm_coords) / len(lm_coords)
            x = int(x * w) + x_offset
            y = int(y * h) + y_offset

        if debug:
            print(f"{location_name}: ({x}, {y})")
        print("DATA+++++++++++++++++++++image_path",image_path,"...................",(x, y),location_name)
        return (x, y)
