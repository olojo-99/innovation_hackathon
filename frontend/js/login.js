const API_URL = 'http://localhost:8000';

// Handle form submission
document.getElementById('loginForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    await handleLogin();
});

// Handle Login
async function handleLogin() {
    const teamName = document.getElementById('teamName').value;
    const password = document.getElementById('password').value;

    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = '';

    // Validate required fields
    if (!teamName || !password) {
        messageDiv.innerHTML = `
            <div class="message error">
                ❌ Please enter your Team Name and Password
            </div>
        `;
        return;
    }

    try {
        const response = await fetch(`${API_URL}/teams/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ team_name: teamName, password: password, region: "EMEA" })  // Region ignored for login
        });

        const data = await response.json();

        if (response.ok) {
            // Store login data in sessionStorage
            sessionStorage.setItem('teamLoginData', JSON.stringify(data));

            let message = `✅ Welcome back, ${data.team_name}!<br><br>`;
            message += `📊 <strong>Your Progress:</strong> ${data.current_stage}/4 stages unlocked<br><br>`;

            if (data.challenge_open) {
                // Determine which stage PDF to show based on current_stage (stages_unlocked)
                // current_stage = stages_unlocked (0-4)
                // Stage PDFs available: stage1, stage2, stage3, stage4, stage5

                // Challenge is open - show download link for appropriate stage
                if (data.current_stage === 0) {
                    // Haven't started yet - show Stage 1 PDF download
                    message += `
                        📄 <strong>The challenge is now open!</strong><br>
                        Download Stage 1 PDF to begin:<br>
                        <a href="#" onclick="downloadStagePDF(1, '${teamName}', '${password}'); return false;" style="color: #155724; font-weight: 600; text-decoration: underline;">
                            Click here to download Stage 1 requirements
                        </a><br><br>
                        <small style="color: #666;">⏱️ Your timer will start when you download the PDF</small><br>
                    `;
                } else if (data.current_stage >= 4) {
                    // Completed all 4 stages - show Stage 5 PDF and final submission
                    message += `
                        🎉 <strong>Congratulations! All 4 stages completed!</strong><br><br>
                        Download Stage 5 PDF for accessibility requirements:<br>
                        <a href="${API_URL}/pdfs/stage5.pdf" target="_blank" style="color: #155724; font-weight: 600; text-decoration: underline;">
                            Click here to download Stage 5 PDF
                        </a><br><br>
                        After reviewing usability and accessibility requirements:<br>
                        <a href="/submit" style="color: #E31837; font-weight: 600; text-decoration: underline;">
                            📦 Submit your BitBucket repository URL
                        </a><br>
                    `;
                } else {
                    // In progress (1-3 stages unlocked)
                    // If stages_unlocked = 1, they have Stage 2 PDF (next is Stage 3)
                    // If stages_unlocked = 2, they have Stage 3 PDF (next is Stage 4)
                    // If stages_unlocked = 3, they have Stage 4 PDF (next is Stage 5)
                    const currentPDFStage = data.current_stage + 1; // PDF they currently have access to
                    const nextURLStage = data.current_stage + 2; // Next URL stage to submit

                    message += `
                        🚀 <strong>Keep going!</strong><br>
                        You've unlocked ${data.current_stage}/4 stages.<br><br>
                        📄 <strong>Current Challenge:</strong> Stage ${currentPDFStage}<br>
                        Download the PDF to continue:<br>
                        <a href="${API_URL}/pdfs/stage${currentPDFStage}.pdf" target="_blank" style="color: #155724; font-weight: 600; text-decoration: underline;">
                            Click here to download Stage ${currentPDFStage} requirements
                        </a><br><br>
                        <small style="color: #666;">
                            Complete Stage ${currentPDFStage} problems, then submit ERFT_stage${nextURLStage} URL to unlock the next stage.
                        </small><br>
                    `;
                }
            } else {
                // Challenge not yet open - show start time
                message += `
                    ⏰ <strong>Challenge not yet open in ${data.region}</strong><br><br>
                    The next challenge opens at:<br>
                    <strong style="color: #667eea; font-size: 18px;">${data.start_time}</strong><br><br>
                    Check back after the start time to download next stage PDF.
                `;
            }

            message += `<br><a href="/leaderboard" style="color: #667eea; font-weight: 600;">View Leaderboards</a>`;

            messageDiv.innerHTML = `<div class="message success">${message}</div>`;
        } else {
            messageDiv.innerHTML = `
                <div class="message error">
                    ❌ ${data.detail || 'Login failed. Please check your credentials.'}
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

// Download Stage PDF and start timer (only for Stage 1)
async function downloadStagePDF(stage, teamName, password) {
    try {
        // Only start timer for Stage 1 (first PDF download)
        if (stage === 1) {
            const response = await fetch(`${API_URL}/teams/start-timer`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ team_name: teamName, password: password, region: "EMEA" })
            });

            if (response.ok) {
                // Timer started successfully, now download the PDF
                window.open(`${API_URL}/pdfs/stage${stage}.pdf`, '_blank');
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
        window.open(`${API_URL}/pdfs/stage${stage}.pdf`, '_blank');
    }
}
