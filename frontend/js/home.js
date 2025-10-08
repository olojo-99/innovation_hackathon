const API_URL = 'http://localhost:8000';

document.getElementById('teamForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const teamName = document.getElementById('teamName').value;
    const password = document.getElementById('password').value;
    const region = document.getElementById('region').value;

    const messageDiv = document.getElementById('message');
    messageDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/teams/create`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                team_name: teamName,
                password: password,
                region: region
            })
        });

        const data = await response.json();

        if (response.ok) {
            messageDiv.innerHTML = `
                <div class="message success">
                    ✅ Team "${data.team_name}" created successfully in ${data.region}!<br><br>
                    📄 <strong>Download Stage 1 Challenge:</strong><br>
                    <a href="${API_URL}${data.stage1_pdf_url}" download style="color: #155724; font-weight: 600; text-decoration: underline;">
                        Click here to download Stage 1 requirements
                    </a><br><br>
                    Read the PDF and start solving the challenge!
                </div>
            `;
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
});
