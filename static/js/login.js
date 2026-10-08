const video = document.getElementById("video");
const canvas = document.getElementById("canvas");

const startCameraButton =
    document.getElementById("startCamera");

const authenticateButton =
    document.getElementById("authenticateButton");

const loginForm =
    document.getElementById("loginForm");

const cameraStatus =
    document.getElementById("cameraStatus");

const cameraOverlay =
    document.getElementById("cameraOverlay");

const messageBox =
    document.getElementById("loginMessage");


let cameraStream = null;


/* =========================================================
   MESSAGE
========================================================= */

function showMessage(message, type) {

    messageBox.textContent = message;

    messageBox.className =
        "message " + type;
}


/* =========================================================
   START CAMERA
========================================================= */

async function startCamera() {

    try {

        cameraStream =
            await navigator.mediaDevices.getUserMedia({

                video: {
                    width: {
                        ideal: 640
                    },

                    height: {
                        ideal: 480
                    },

                    facingMode: "user"
                },

                audio: false
            });


        video.srcObject =
            cameraStream;


        cameraStatus.textContent =
            "Camera active";


        cameraStatus.classList.add(
            "active"
        );


        cameraOverlay.style.display =
            "none";


        authenticateButton.disabled =
            false;


        startCameraButton.textContent =
            "Camera Active";


        startCameraButton.disabled =
            true;


        showMessage(
            "Camera started. Position your face clearly inside the frame.",
            "info"
        );


    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to access camera. Please allow camera permission.",
            "error"
        );

    }
}


/* =========================================================
   CAPTURE IMAGE
========================================================= */

function captureImage() {

    if (!cameraStream) {

        showMessage(
            "Please start the camera first.",
            "error"
        );

        return null;
    }


    if (
        video.videoWidth === 0 ||
        video.videoHeight === 0
    ) {

        showMessage(
            "Camera is not ready yet. Please wait.",
            "error"
        );

        return null;
    }


    const context =
        canvas.getContext("2d");


    canvas.width =
        video.videoWidth;

    canvas.height =
        video.videoHeight;


    context.drawImage(
        video,
        0,
        0,
        canvas.width,
        canvas.height
    );


    return canvas.toDataURL(
        "image/jpeg",
        0.90
    );
}


/* =========================================================
   SHOW AUTHENTICATION RESULT
========================================================= */

function showAuthenticationResult(
    success,
    name,
    score,
    message
) {

    const modal =
        document.getElementById(
            "resultModal"
        );

    const resultIcon =
        document.getElementById(
            "resultIcon"
        );

    const resultTitle =
        document.getElementById(
            "resultTitle"
        );

    const resultMessage =
        document.getElementById(
            "resultMessage"
        );

    const resultScore =
        document.getElementById(
            "resultScore"
        );

    const resultButton =
        document.getElementById(
            "resultButton"
        );


    if (success) {

        resultIcon.textContent =
            "✓";

        resultIcon.className =
            "result-icon success-icon";


        resultTitle.textContent =
            "Authentication Successful";


        resultMessage.textContent =
            `Welcome, ${name}`;


        resultScore.innerHTML =
            `Match Score: <strong>${score}%</strong>`;


        resultButton.textContent =
            "Continue to Dashboard";


        resultButton.className =
            "btn btn-primary";


        resultButton.onclick =
            function () {

                window.location.href =
                    "/dashboard";

            };

    } else {

        resultIcon.textContent =
            "✕";

        resultIcon.className =
            "result-icon failed-icon";


        resultTitle.textContent =
            "Authentication Failed";


        resultMessage.textContent =
            message ||
            "Face does not match the registered user.";


        resultScore.innerHTML =
            `Match Score: <strong>${score}%</strong>`;


        resultButton.textContent =
            "Try Again";


        resultButton.className =
            "btn btn-secondary";


        resultButton.onclick =
            function () {

                modal.classList.remove(
                    "show"
                );

                authenticateButton.disabled =
                    false;

            };

    }


    modal.classList.add(
        "show"
    );
}


/* =========================================================
   BIOMETRIC LOGIN
========================================================= */

async function authenticateUser(event) {

    event.preventDefault();


    const userId =
        document.getElementById(
            "userId"
        ).value.trim();


    if (!userId) {

        showMessage(
            "Please enter your User ID.",
            "error"
        );

        return;
    }


    const image =
        captureImage();


    if (!image) {
        return;
    }


    authenticateButton.disabled =
        true;


    authenticateButton.textContent =
        "Authenticating...";


    showMessage(
        "Analyzing your biometric data...",
        "info"
    );


    try {

        const response =
            await fetch(
                "/api/login",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        user_id: userId,

                        image: image

                    })
                }
            );


        const result =
            await response.json();


        if (result.success) {

            showAuthenticationResult(

                true,

                result.name,

                result.score,

                result.message

            );


        } else {

            showAuthenticationResult(

                false,

                "",

                result.score ?? 0,

                result.message

            );

        }


    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to connect to the authentication server.",
            "error"
        );


        authenticateButton.disabled =
            false;

    }


    authenticateButton.textContent =
        "Authenticate Face";
}


/* =========================================================
   CLOSE RESULT MODAL
========================================================= */

function closeResultModal() {

    const modal =
        document.getElementById(
            "resultModal"
        );

    modal.classList.remove(
        "show"
    );
}


/* =========================================================
   STOP CAMERA
========================================================= */

function stopCamera() {

    if (cameraStream) {

        cameraStream
            .getTracks()
            .forEach(
                track => track.stop()
            );

        cameraStream = null;
    }
}


/* =========================================================
   EVENTS
========================================================= */

startCameraButton.addEventListener(
    "click",
    startCamera
);


loginForm.addEventListener(
    "submit",
    authenticateUser
);


window.addEventListener(
    "beforeunload",
    stopCamera
);