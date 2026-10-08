from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

import numpy as np

from config import (
    SECRET_KEY,
    FACE_MATCH_THRESHOLD
)

from database.db import (
    initialize_database,
    get_user,
    create_user,
    add_face_sample,
    get_face_samples,
    get_all_users,
    record_login,
    get_login_history,
    get_statistics
)

from biometric.face_service import (
    decode_base64_image,
    extract_face,
    face_to_bytes,
    bytes_to_face,
    create_lbph_recognizer,
    calculate_confidence
)


app = Flask(__name__)

app.config["SECRET_KEY"] = SECRET_KEY


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# REGISTER PAGE
# ============================================================

@app.route("/register")
def register_page():

    return render_template("register.html")


# ============================================================
# REGISTER USER
# ============================================================

@app.route("/api/register", methods=["POST"])
def register_user():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message": "No data received."
            }), 400


        user_id = data.get(
            "user_id",
            ""
        ).strip()

        name = data.get(
            "name",
            ""
        ).strip()

        images = data.get(
            "images",
            []
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not user_id:

            return jsonify({
                "success": False,
                "message": "User ID is required."
            }), 400


        if not name:

            return jsonify({
                "success": False,
                "message": "Name is required."
            }), 400


        if len(user_id) < 3:

            return jsonify({
                "success": False,
                "message":
                    "User ID must contain at least 3 characters."
            }), 400


        if len(name) < 2:

            return jsonify({
                "success": False,
                "message":
                    "Please enter a valid name."
            }), 400


        if not images:

            return jsonify({
                "success": False,
                "message":
                    "Please capture your face samples."
            }), 400


        if len(images) < 5:

            return jsonify({
                "success": False,
                "message":
                    "Please capture all 5 face samples."
            }), 400


        # ----------------------------------------------------
        # CHECK EXISTING USER
        # ----------------------------------------------------

        existing_user = get_user(user_id)


        if existing_user:

            return jsonify({
                "success": False,
                "message":
                    "This User ID is already registered."
            }), 409


        # ----------------------------------------------------
        # PROCESS FACE SAMPLES
        # ----------------------------------------------------

        processed_faces = []


        for index, image_data in enumerate(images):

            image = decode_base64_image(
                image_data
            )


            if image is None:

                return jsonify({
                    "success": False,
                    "message":
                        f"Unable to process face sample {index + 1}."
                }), 400


            face, error = extract_face(
                image
            )


            if error:

                return jsonify({
                    "success": False,
                    "message":
                        f"Sample {index + 1}: {error}"
                }), 400


            processed_faces.append(
                face
            )


        # ----------------------------------------------------
        # CREATE USER
        # ----------------------------------------------------

        create_user(
            user_id,
            name
        )


        # ----------------------------------------------------
        # STORE ALL FACE SAMPLES
        # ----------------------------------------------------

        for face in processed_faces:

            face_bytes = face_to_bytes(
                face
            )


            if face_bytes is None:

                return jsonify({
                    "success": False,
                    "message":
                        "Unable to save biometric data."
                }), 500


            add_face_sample(
                user_id,
                face_bytes
            )


        return jsonify({

            "success": True,

            "message":
                "Biometric registration completed successfully.",

            "user_id":
                user_id,

            "name":
                name,

            "samples":
                len(processed_faces)
        })


    except Exception as error:

        print(
            "Registration error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unexpected registration error."
        }), 500


# ============================================================
# LOGIN PAGE
# ============================================================

@app.route("/login")
def login_page():

    return render_template(
        "login.html"
    )


# ============================================================
# BIOMETRIC LOGIN
# ============================================================

@app.route("/api/login", methods=["POST"])
def biometric_login():

    try:

        data = request.get_json()

        if not data:

            return jsonify({
                "success": False,
                "message":
                    "No data received."
            }), 400


        user_id = data.get(
            "user_id",
            ""
        ).strip()

        image_data = data.get(
            "image",
            ""
        )


        # ----------------------------------------------------
        # VALIDATION
        # ----------------------------------------------------

        if not user_id:

            return jsonify({
                "success": False,
                "message":
                    "User ID is required."
            }), 400


        if not image_data:

            return jsonify({
                "success": False,
                "message":
                    "Face image is required."
            }), 400


        # ----------------------------------------------------
        # FIND USER
        # ----------------------------------------------------

        user = get_user(
            user_id
        )


        if not user:

            record_login(
                user_id,
                "FAILED",
                0
            )

            return jsonify({
                "success": False,
                "message":
                    "User ID is not registered."
            }), 404


        # ----------------------------------------------------
        # DECODE LIVE IMAGE
        # ----------------------------------------------------

        image = decode_base64_image(
            image_data
        )


        if image is None:

            return jsonify({
                "success": False,
                "message":
                    "Unable to process camera image."
            }), 400


        # ----------------------------------------------------
        # EXTRACT LIVE FACE
        # ----------------------------------------------------

        live_face, error = extract_face(
            image
        )


        if error:

            record_login(
                user_id,
                "FAILED",
                0
            )

            return jsonify({
                "success": False,
                "message": error
            }), 400


        # ----------------------------------------------------
        # GET REGISTERED FACE SAMPLES
        # ----------------------------------------------------

        samples = get_face_samples(
            user_id
        )


        if not samples:

            return jsonify({
                "success": False,
                "message":
                    "No biometric data found for this user."
            }), 404


        # ----------------------------------------------------
        # PREPARE TRAINING DATA
        # ----------------------------------------------------

        training_faces = []

        training_labels = []


        for sample in samples:

            stored_face = bytes_to_face(
                sample["face_image"]
            )


            if stored_face is not None:

                training_faces.append(
                    stored_face
                )

                training_labels.append(
                    1
                )


        if not training_faces:

            return jsonify({
                "success": False,
                "message":
                    "Stored biometric data is invalid."
            }), 500


        # ----------------------------------------------------
        # TRAIN LBPH MODEL
        # ----------------------------------------------------

        recognizer = create_lbph_recognizer()


        recognizer.train(
            training_faces,
            np.array(
                training_labels
            )
        )


        # ----------------------------------------------------
        # PREDICT LIVE FACE
        # ----------------------------------------------------

        label, distance = recognizer.predict(
            live_face
        )


        match_score = calculate_confidence(
            distance
        )


        # ----------------------------------------------------
        # AUTHENTICATION
        # ----------------------------------------------------

        if (
            label == 1
            and
            distance <= FACE_MATCH_THRESHOLD
        ):

            record_login(
                user_id,
                "SUCCESS",
                match_score
            )


            session["user_id"] = (
                user["user_id"]
            )

            session["name"] = (
                user["name"]
            )


            return jsonify({

                "success": True,

                "message":
                    "Biometric authentication successful.",

                "name":
                    user["name"],

                "score":
                    match_score,

                "redirect":
                    url_for("dashboard")
            })


        # ----------------------------------------------------
        # FAILED AUTHENTICATION
        # ----------------------------------------------------

        record_login(
            user_id,
            "FAILED",
            match_score
        )


        return jsonify({

            "success": False,

            "message":
                "Face does not match the registered user.",

            "score":
                match_score

        }), 401


    except Exception as error:

        print(
            "Login error:",
            error
        )

        return jsonify({
            "success": False,
            "message":
                "Unexpected authentication error."
        }), 500


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(
            url_for("login_page")
        )


    statistics = get_statistics()

    history = get_login_history(
        20
    )

    users = get_all_users()


    return render_template(
        "dashboard.html",

        statistics=statistics,

        history=history,

        users=users,

        current_user=session.get(
            "name"
        )
    )


# ============================================================
# LOGOUT
# ============================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(
        url_for("home")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )