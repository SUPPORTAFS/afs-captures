import streamlit as st
import cv2
import os
import numpy as np

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    PageBreak
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4

# -------------------------
# FONCTION ANALYSE VIDÉO
# -------------------------

def analyse_video(video_path, output_folder, prefix):

    os.makedirs(output_folder, exist_ok=True)

    for file in os.listdir(output_folder):

        os.remove(
            os.path.join(output_folder, file)
        )

    interval_seconds = 3

    blur_threshold = 200

    difference_threshold = 15

    video = cv2.VideoCapture(video_path)

    fps = video.get(cv2.CAP_PROP_FPS)

    frame_interval = int(
        fps * interval_seconds
    )

    frame_count = 0

    capture_count = 0

    last_saved_gray = None

    while True:

        success, frame = video.read()

        if not success:
            break

        if frame_count % frame_interval == 0:

            gray = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2GRAY
            )

            sharpness = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            if sharpness < blur_threshold:

                frame_count += 1

                continue

            if last_saved_gray is not None:

                difference = cv2.absdiff(
                    gray,
                    last_saved_gray
                )

                mean_difference = np.mean(
                    difference
                )

                if mean_difference < difference_threshold:

                    frame_count += 1

                    continue

            image_path = os.path.join(
                output_folder,
                f"{prefix}_{capture_count}.jpg"
            )

            cv2.imwrite(
                image_path,
                frame
            )

            last_saved_gray = gray

            capture_count += 1

        frame_count += 1

    video.release()

    return capture_count


# -------------------------
# GÉNÉRATION PDF
# -------------------------

def generate_pdf(selected_before, selected_after):

    pdf_path = "rapport_client.pdf"

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=A4
    )

    styles = getSampleStyleSheet()

    elements = []

    # -------------------------
    # TITRE
    # -------------------------

    elements.append(
        Paragraph(
            "Rapport intervention AFS PLOMBERIE CVC",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    # -------------------------
    # AVANT
    # -------------------------

    elements.append(
        Paragraph(
            "Captures AVANT",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    for image_path in selected_before:

        img = Image(
            image_path,
            width=400,
            height=225
        )

        elements.append(img)

        elements.append(Spacer(1, 15))

    # -------------------------
    # APRÈS
    # -------------------------

    elements.append(
        PageBreak()
    )

    elements.append(
        Paragraph(
            "Captures APRÈS",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 10))

    for image_path in selected_after:

        img = Image(
            image_path,
            width=400,
            height=225
        )

        elements.append(img)

        elements.append(Spacer(1, 15))

    doc.build(elements)

    return pdf_path


# -------------------------
# CONFIG PAGE
# -------------------------

st.set_page_config(
    page_title="AFS PLOMBERIE CVC",
    layout="wide"
)

# -------------------------
# EN-TÊTE
# -------------------------

st.image(
    "logo.png",
    width=220
)

st.title(
    "Extraction de captures video"
)

st.write(
    "Extraction intelligente des meilleures captures avant/après intervention."
)

# -------------------------
# UPLOADS
# -------------------------

uploaded_video_before = st.file_uploader(
    "Vidéo AVANT intervention",
    type=["mp4"]
)

uploaded_video_after = st.file_uploader(
    "Vidéo APRÈS intervention",
    type=["mp4"]
)

# -------------------------
# ANALYSE
# -------------------------

if (
    uploaded_video_before is not None
    and uploaded_video_after is not None
):

    video_before_path = "video_avant.mp4"

    with open(video_before_path, "wb") as f:

        f.write(
            uploaded_video_before.read()
        )

    video_after_path = "video_apres.mp4"

    with open(video_after_path, "wb") as f:

        f.write(
            uploaded_video_after.read()
        )

    st.success("Vidéos chargées")

    if st.button("Analyser les vidéos"):

        with st.spinner("Analyse en cours..."):

            analyse_video(
                video_before_path,
                "captures_avant",
                "avant"
            )

            analyse_video(
                video_after_path,
                "captures_apres",
                "apres"
            )

        st.success("Analyse terminée")

# =========================
# AFFICHAGE AVANT
# =========================

selected_before = []

if os.path.exists("captures_avant"):

    st.subheader("Captures AVANT")

    files_before = sorted(
        os.listdir("captures_avant")
    )

    cols_before = st.columns(3)

    for index, file in enumerate(files_before):

        image_path = os.path.join(
            "captures_avant",
            file
        )

        with cols_before[index % 3]:

            st.image(
                image_path,
                use_container_width=True
            )

            selected = st.checkbox(
                "Sélectionner",
                key=f"before_{file}"
            )

            if selected:

                selected_before.append(
                    image_path
                )

# =========================
# AFFICHAGE APRÈS
# =========================

selected_after = []

if os.path.exists("captures_apres"):

    st.subheader("Captures APRÈS")

    files_after = sorted(
        os.listdir("captures_apres")
    )

    cols_after = st.columns(3)

    for index, file in enumerate(files_after):

        image_path = os.path.join(
            "captures_apres",
            file
        )

        with cols_after[index % 3]:

            st.image(
                image_path,
                use_container_width=True
            )

            selected = st.checkbox(
                "Sélectionner",
                key=f"after_{file}"
            )

            if selected:

                selected_after.append(
                    image_path
                )

# =========================
# EXPORT PDF
# =========================

if st.button("Générer le rapport PDF"):

    pdf_path = generate_pdf(
        selected_before,
        selected_after
    )

    st.success("Rapport généré")

    with open(pdf_path, "rb") as file:

        st.download_button(
            label="Télécharger le rapport PDF",
            data=file,
            file_name="rapport_client.pdf",
            mime="application/pdf"
        )