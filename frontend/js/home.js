const API_URL = 'http://localhost:8000';

// Handle form submission
document.getElementById('teamForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleRegister();
});

// Handle Register button click
async function handleRegister() {
    const teamName = document.getElementById('teamName').value;
    const password = document.getElementById('password').value;
    const region = document.getElementById('region').value;

    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = '';

    // Validate required fields
    if (!teamName || !password || !region) {
        messageDiv.innerHTML = `
            <div class="message error">
                ❌ Please fill in all required fields (Team Name, Password, and Region)
            </div>
        `;
        return;
    }

    try {
        const response = await fetch(`${API_URL}/teams/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ team_name: teamName, password: password, region: region })
        });

        const data = await response.json();

        if (response.ok) {
            let message = `✅ Team "${data.team_name}" registered successfully for ${data.region}!<br><br>`;

            if (data.challenge_open) {
                // Challenge is open - show download links for PDF and CSV with timer start
                message += `
                    📄 <strong>The challenge is now open!</strong><br>
                    Download Stage 1 materials to begin:<br><br>
                    <a href="#" onclick="downloadStageFile('pdf', 1, '${teamName}', '${password}'); return false;" style="color: #155724; font-weight: 600; text-decoration: underline;">
                        📄 Click here to download Stage 1 requirements (PDF)
                    </a><br><br>
                    <a href="#" onclick="downloadStageFile('csv', 1, '${teamName}', '${password}'); return false;" style="color: #155724; font-weight: 600; text-decoration: underline;">
                        📊 Click here to download Dataset (CSV)
                    </a><br><br>
                    <small style="color: #666;">⏱️ Your timer will start when you download either file</small><br><br>
                    Read the PDF and start solving the challenge!<br><br>
                `;
            } else {
                // Challenge not yet open - show start time
                message += `
                    ⏰ <strong>Challenge not yet open in ${data.region}</strong><br><br>
                    The next challenge opens at:<br>
                    <strong style="color: #667eea; font-size: 18px;">${data.start_time}</strong><br><br>
                    You're registered! Check back after the start time to download next stage PDF.
                `;
            }

            message += `<br><a href="/leaderboard" style="color: #667eea; font-weight: 600;">View Leaderboards</a>`;

            messageDiv.innerHTML = `<div class="message success">${message}</div>`;
            document.getElementById('teamForm').reset();
        } else {
            messageDiv.innerHTML = `
                <div class="message error">
                    ❌ ${data.detail || 'Failed to create team'}
                </div>
            `;
        }
    } catch (error) {
        messageDiv.innerHTML = `
            <div class="message error">
                ❌ Error: ${error.message}. Make sure the API server is running.
            </div>
        `;
    }
}

// Download Stage file (PDF or CSV) and start timer (only for Stage 1)
async function downloadStageFile(fileType, stage, teamName, password) {
    try {
        // Only start timer for Stage 1 materials (first download)
        if (stage === 1) {
            const response = await fetch(`${API_URL}/teams/start-timer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ team_name: teamName, password: password, region: "EMEA" })
            });

            if (response.ok) {
                // Timer started successfully, now download the file
                if (fileType === 'pdf') {
                    window.open(`${API_URL}/pdfs/stage${stage}.pdf`, '_blank');
                } else if (fileType === 'csv') {
                    window.open(`${API_URL}/data/hackathon_fraud_payment.csv`, '_blank');
                }
            } else {
                alert('Failed to start timer. Please try again.');
            }
        } else {
            // For other stages, just download the PDF
            window.open(`${API_URL}/pdfs/stage${stage}.pdf`, '_blank');
        }
    } catch (error) {
        console.error('Error:', error);
        // Still allow download even if there's an error
        if (fileType === 'pdf') {
            window.open(`${API_URL}/pdfs/stage${stage}.pdf`, '_blank');
        } else if (fileType === 'csv') {
            window.open(`${API_URL}/data/hackathon_fraud_payment.csv`, '_blank');
        }
    }
}

