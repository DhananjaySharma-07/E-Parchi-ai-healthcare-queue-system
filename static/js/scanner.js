const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const resultElement = document.getElementById('result');
const scanBtn = document.getElementById('scanBtn');
const startBtn = document.getElementById('startCameraBtn');

let stream = null;

async function startCamera() {
    // Guard: camera API requires HTTPS or localhost
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        resultElement.textContent = 'Camera access requires HTTPS or localhost. Use the manual hospital ID option below.';
        resultElement.className = 'text-danger';
        return;
    }

    try {
        stream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: { ideal: 'environment' } }
        });
        video.srcObject = stream;
        await video.play();
        resultElement.textContent = 'Camera started. Position the QR code in the frame, then click Scan.';
        resultElement.className = 'text-success';
    } catch (err) {
        console.error('Error accessing camera:', err);
        let msg = 'Camera access denied. Please allow camera permissions in your browser settings.';
        if (err.name === 'NotFoundError') {
            msg = 'No camera found on this device.';
        } else if (err.name === 'NotReadableError') {
            msg = 'Camera is already in use by another application.';
        }
        resultElement.textContent = msg;
        resultElement.className = 'text-danger';
    }
}

function stopCamera() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
}

// Start camera only when user explicitly clicks the button
if (startBtn) {
    startBtn.addEventListener('click', () => {
        startCamera();
    });
}

scanBtn.addEventListener('click', () => {
    if (!stream) {
        resultElement.textContent = 'Please start the camera first by clicking "Start Camera".';
        resultElement.className = 'text-warning';
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);

    if (code) {
        const data = code.data;
        resultElement.textContent = 'QR code detected!';
        resultElement.className = 'text-success';

        // Support both HOSPITAL_ID:N and ?hospital_id=N formats
        let hospitalId = null;
        if (data.toUpperCase().includes('HOSPITAL_ID:')) {
            const match = data.match(/HOSPITAL_ID\s*:\s*(\d+)/i);
            if (match) hospitalId = match[1];
        } else if (data.includes('hospital_id=')) {
            const match = data.match(/hospital_id=(\d+)/i);
            if (match) hospitalId = match[1];
        } else if (/^\d+$/.test(data.trim())) {
            hospitalId = data.trim();
        }

        if (hospitalId) {
            stopCamera();
            fetch(`/process_qr?hospital_id=${hospitalId}`)
                .then(response => response.json())
                .then(result => {
                    if (result.success) {
                        window.location.href = `/register_patient?hospital_id=${hospitalId}`;
                    } else {
                        resultElement.textContent = 'Hospital not found. Please verify the QR code.';
                        resultElement.className = 'text-danger';
                        startCamera();
                    }
                })
                .catch(() => {
                    resultElement.textContent = 'Error processing QR code. Please try again.';
                    resultElement.className = 'text-danger';
                    startCamera();
                });
        } else {
            resultElement.textContent = 'Invalid QR code format. Please scan a valid hospital QR code.';
            resultElement.className = 'text-danger';
        }
    } else {
        resultElement.textContent = 'No QR code detected. Ensure good lighting and hold steady.';
        resultElement.className = 'text-warning';
    }
});

// Release camera when navigating away
window.addEventListener('beforeunload', stopCamera);