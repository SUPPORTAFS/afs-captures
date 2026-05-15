import cv2
import os
import numpy as np

# -------------------------
# PARAMÈTRES
# -------------------------

video_path = "video.mp4"

output_folder = "captures"

interval_seconds = 3

blur_threshold = 200

difference_threshold = 15

# -------------------------
# DOSSIER
# -------------------------

os.makedirs(output_folder, exist_ok=True)

# -------------------------
# OUVERTURE VIDÉO
# -------------------------

video = cv2.VideoCapture(video_path)

if not video.isOpened():
    print("Erreur ouverture vidéo")
    exit()

fps = video.get(cv2.CAP_PROP_FPS)

frame_interval = int(fps * interval_seconds)

frame_count = 0
capture_count = 0

last_saved_gray = None

# -------------------------
# ANALYSE
# -------------------------

while True:

    success, frame = video.read()

    if not success:
        break

    if frame_count % frame_interval == 0:

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        # -------------------------
        # TEST NETTETÉ
        # -------------------------

        sharpness = cv2.Laplacian(
            gray,
            cv2.CV_64F
        ).var()

        print(f"Netteté : {sharpness}")

        if sharpness < blur_threshold:

            print("Image floue ignorée")

            frame_count += 1
            continue

        # -------------------------
        # TEST DIFFÉRENCE
        # -------------------------

        if last_saved_gray is not None:

            difference = cv2.absdiff(
                gray,
                last_saved_gray
            )

            mean_difference = np.mean(difference)

            print(f"Différence : {mean_difference}")

            if mean_difference < difference_threshold:

                print("Image trop similaire ignorée")

                frame_count += 1
                continue

        # -------------------------
        # SAUVEGARDE
        # -------------------------

        image_path = os.path.join(
            output_folder,
            f"capture_{capture_count}.jpg"
        )

        cv2.imwrite(image_path, frame)

        print(f"Capture enregistrée : {image_path}")

        last_saved_gray = gray

        capture_count += 1

    frame_count += 1

# -------------------------
# FIN
# -------------------------

video.release()

print("Analyse terminée")