function trackToken(tokenId) {
    // Show loading
    const modal = new bootstrap.Modal(document.getElementById('trackModal'));
    const modalBody = document.getElementById('track-content');
    modalBody.innerHTML = '<div class="text-center"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Loading...</span></div></div>';

    modal.show();

    // Fetch queue status
    fetch('/api/queue_status')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                modalBody.innerHTML = '<p class="text-danger">Unable to load queue status.</p>';
                return;
            }

            const breakMessage = data.is_paused ? `
                <div class="alert alert-warning text-center">
                    <i class="fas fa-pause-circle me-2"></i>
                    <strong>Queue paused:</strong> ${data.paused_reason || 'The doctor is currently on a short break. The queue will resume shortly.'}
                </div>
            ` : '';

            modalBody.innerHTML = `
                <div class="text-center mb-4">
                    <h5>Your Token: <span class="badge bg-primary fs-4">${data.your_token}</span></h5>
                </div>
                ${breakMessage}
                <div class="row g-3">
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-user-md fa-2x text-success mb-2"></i>
                                <h6>Current Serving</h6>
                                <span class="badge bg-success fs-5">${data.current_token}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-users fa-2x text-warning mb-2"></i>
                                <h6>Patients Ahead</h6>
                                <span class="badge bg-warning fs-5">${data.patients_ahead}</span>
                            </div>
                        </div>
                    </div>
                    <div class="col-md-4">
                        <div class="card text-center">
                            <div class="card-body">
                                <i class="fas fa-clock fa-2x text-info mb-2"></i>
                                <h6>Est. Wait Time</h6>
                                <span class="badge bg-info fs-5">${data.est_wait_time} min</span>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="mt-4">
                    <div class="progress" style="height: 20px;">
                        <div class="progress-bar bg-primary" role="progressbar" style="width: ${Math.max(10, 100 - (data.patients_ahead * 10))}%">
                            ${data.patients_ahead} ahead
                        </div>
                    </div>
                </div>
            `;
        })
        .catch(error => {
            modalBody.innerHTML = '<p class="text-danger">Error loading queue status.</p>';
        });
}