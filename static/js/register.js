const video =
    document.getElementById("video");

const canvas =
    document.getElementById("canvas");

const startCameraButton =
    document.getElementById("startCamera");

const captureButton =
    document.getElementById("captureFace");

const registerButton =
    document.getElementById("registerButton");

const registerForm =
    document.getElementById("registerForm");

const cameraStatus =
    document.getElementById("cameraStatus");

const cameraOverlay =
    document.getElementById("cameraOverlay");

const messageBox =
    document.getElementById("registerMessage");

const sampleCounter =
    document.getElementById("sampleCounter");

const progressBar =
    document.getElementById("sampleProgress");

const sampleInstruction =
    document.getElementById("sampleInstruction");


let cameraStream = null;

let capturedSamples = [];

const TOTAL_SAMPLES = 5;


/* =========================================================
   MESSAGE
========================================================= */

function showMessage(message, type) {

    messageBox.textContent = message;

    messageBox.className =
        "message " + type;
}


/* =========================================================
   UPDATE PROGRESS
========================================================= */

function updateProgress() {

    const count =
        capturedSamples.length;


    sampleCounter.textContent =
        `${count}/${TOTAL_SAMPLES}`;


    const percentage =
        (count / TOTAL_SAMPLES) * 100;


    progressBar.style.width =
        `${percentage}%`;


    if (count === 0) {

        sampleInstruction.textContent =
            "Look directly at the camera.";

    }
    else if (count === 1) {

        sampleInstruction.textContent =
            "Turn your face slightly to the left.";

    }
    else if (count === 2) {

        sampleInstruction.textContent =
            "Turn your face slightly to the right.";

    }
    else if (count === 3) {

        sampleInstruction.textContent =
            "Move your face slightly upward.";

    }
    else if (count === 4) {

        sampleInstruction.textContent =
            "Look directly at the camera again.";

    }
    else {

        sampleInstruction.textContent =
            "All face samples captured.";

    }
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


        captureButton.disabled =
            false;


        startCameraButton.textContent =
            "Camera Active";


        startCameraButton.disabled =
            true;


        showMessage(
            "Camera started. Follow the instructions and capture 5 samples.",
            "info"
        );


        updateProgress();


    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to access camera. Please allow camera permission.",
            "error"
        );

    }
}


/* =========================================================
   CAPTURE ONE SAMPLE
========================================================= */

function captureSingleSample() {

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
   CAPTURE 5 SAMPLES
========================================================= */

async function captureSamples() {

    if (!cameraStream) {

        showMessage(
            "Please start the camera first.",
            "error"
        );

        return;
    }


    if (
        capturedSamples.length >=
        TOTAL_SAMPLES
    ) {

        return;
    }


    captureButton.disabled =
        true;


    startCameraButton.disabled =
        true;


    showMessage(
        "Capturing face sample...",
        "info"
    );


    const image =
        captureSingleSample();


    if (!image) {

        captureButton.disabled =
            false;

        return;
    }


    capturedSamples.push(
        image
    );


    updateProgress();


    const count =
        capturedSamples.length;


    if (count < TOTAL_SAMPLES) {

        showMessage(
            `Sample ${count} captured. ${TOTAL_SAMPLES - count} more required.`,
            "success"
        );


        /*
         * Give the user time to change
         * their face position before
         * the next capture.
         */

        setTimeout(
            () => {

                captureButton.disabled =
                    false;

                showMessage(
                    `Ready for sample ${count + 1}. Follow the instruction above.`,
                    "info"
                );

            },
            1200
        );


    } else {

        captureButton.textContent =
            "✓ 5 Samples Captured";


        captureButton.classList.add(
            "captured"
        );


        registerButton.disabled =
            false;


        showMessage(
            "All 5 face samples captured successfully. You can now register.",
            "success"
        );
    }
}


/* =========================================================
   REGISTER USER
========================================================= */

async function registerUser(event) {

    event.preventDefault();


    const name =
        document.getElementById(
            "name"
        ).value.trim();


    const userId =
        document.getElementById(
            "userId"
        ).value.trim();


    if (!name) {

        showMessage(
            "Please enter your name.",
            "error"
        );

        return;
    }


    if (!userId) {

        showMessage(
            "Please enter your User ID.",
            "error"
        );

        return;
    }


    if (
        capturedSamples.length <
        TOTAL_SAMPLES
    ) {

        showMessage(
            "Please capture all 5 face samples first.",
            "error"
        );

        return;
    }


    registerButton.disabled =
        true;


    captureButton.disabled =
        true;


    registerButton.textContent =
        "Registering biometric data...";


    try {

        const response =
            await fetch(
                "/api/register",
                {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        name: name,

                        user_id: userId,

                        images:
                            capturedSamples
                    })
                }
            );


        const result =
            await response.json();


        if (result.success) {

            showMessage(
                `Registration successful! ${result.samples} biometric samples stored.`,
                "success"
            );


            stopCamera();


            setTimeout(
                () => {

                    window.location.href =
                        "/login";

                },
                1800
            );


        } else {

            showMessage(
                result.message,
                "error"
            );


            registerButton.disabled =
                false;


            captureButton.disabled =
                false;


            registerButton.textContent =
                "Register Biometric Profile";
        }


    } catch (error) {

        console.error(error);

        showMessage(
            "Unable to connect to the server.",
            "error"
        );


        registerButton.disabled =
            false;


        registerButton.textContent =
            "Register Biometric Profile";
    }
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


captureButton.addEventListener(
    "click",
    captureSamples
);


registerForm.addEventListener(
    "submit",
    registerUser
);


window.addEventListener(
    "beforeunload",
    stopCamera
);


/* =========================================================
   INITIAL STATE
========================================================= */

updateProgress();