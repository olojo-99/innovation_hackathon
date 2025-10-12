const API_URL = 'http://localhost:8000';

document.getElementById('submissionForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const messageDiv = document.getElementById('message');
    const teamName = document.getElementById('teamName').value;
    const password = document.getElementById('password').value;
    const bitbucketUrl = document.getElementById('bitbucketUrl').value;

    messageDiv.innerHTML = '';

    try {
        const response = await fetch(`${API_URL}/api/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                team_name: teamName,
                password: password,
                bitbucket_url: bitbucketUrl
            })
        });

        const data = await response.json();

        if (response.ok) {
            messageDiv.innerHTML = `
                <div class="message success">
                    ✅ <strong>Final Submission Successful!</strong><br><br>
                    Your BitBucket URL has been recorded:<br>
                    <a href="${data.bitbucket_url}" target="_blank">${data.bitbucket_url}</a><br><br>
                    🎉 Congratulations on completing the Innovation Summit Hackathon!
                </div>
            `;
            document.getElementById('submissionForm').reset();
        } else {
            messageDiv.innerHTML = `
                <div class="message error">
                    ❌ ${data.detail || 'Submission failed'}
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
