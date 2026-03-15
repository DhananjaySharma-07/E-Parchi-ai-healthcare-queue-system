const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');
const resultElement = document.getElementById('result');
const scanBtn = document.getElementById('scanBtn');

navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } })
    .then(stream => {
        video.srcObject = stream;
        video.play();
    })
    .catch(err => console.error('Error accessing camera:', err));

scanBtn.addEventListener('click', () => {
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    const imageData = context.getImageData(0, 0, canvas.width, canvas.height);
    const code = jsQR(imageData.data, imageData.width, imageData.height);
    if (code) {
        const data = code.data;
        if (data.startsWith('HOSPITAL_ID:')) {
            const hospitalId = data.split(':')[1];
            fetch(`/process_qr?hospital_id=${hospitalId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = '/register_patient';
                    } else {
                        resultElement.textContent = 'Hospital not found';
                    }
                });
        } else {
            resultElement.textContent = 'Invalid QR code';
        }
    } else {
        resultElement.textContent = 'No QR code detected';
    }
});