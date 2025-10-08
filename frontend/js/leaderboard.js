const API_URL = 'http://localhost:8000';
let currentRegion = 'global';
let refreshInterval;

// Load leaderboard on page load
window.addEventListener('DOMContentLoaded', () => {
    loadLeaderboard('global');
});

async function loadLeaderboard(region) {
    currentRegion = region;

    // Update active tab
    document.querySelectorAll('.tab').forEach((tab, index) => {
        tab.classList.remove('active');
        // Add active class based on region
        if ((region === 'global' && index === 0) ||
            (region === 'EMEA' && index === 1) ||
            (region === 'AMRS' && index === 2) ||
            (region === 'APAC' && index === 3)) {
            tab.classList.add('active');
        }
    });

    const messageDiv = document.getElementById('message');
    const tbody = document.getElementById('leaderboard-body');
    messageDiv.innerHTML = '';

    try {
        const endpoint = region === 'global'
            ? '/leaderboard/global'
            : `/leaderboard/regional/${region}`;

        const response = await fetch(`${API_URL}${endpoint}`);
        const data = await response.json();

        if (response.ok) {
            if (data.length === 0) {
                tbody.innerHTML = `
                    <tr>
                        <td colspan="5" style="text-align: center; padding: 30px; color: #666;">
                            No teams have completed any stages yet.
                        </td>
                    </tr>
                `;
            } else {
                tbody.innerHTML = data.map(team => `
                    <tr>
                        <td><strong>${team.rank}</strong></td>
                        <td>${team.team_name}</td>
                        <td>${team.region}</td>
                        <td>${team.stages_completed}/5</td>
                        <td>${team.total_time}</td>
                    </tr>
                `).join('');
            }

            // Start auto-refresh (every 30 seconds)
            startAutoRefresh();
        } else {
            messageDiv.innerHTML = `
                <div class="message error">
                    ❌ ${data.detail || 'Failed to load leaderboard'}
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

function startAutoRefresh() {
    // Clear any existing interval
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }

    // Refresh every 30 seconds
    refreshInterval = setInterval(() => {
        loadLeaderboard(currentRegion);
    }, 30000);
}

// Clean up interval when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden && refreshInterval) {
        clearInterval(refreshInterval);
    } else if (!document.hidden) {
        startAutoRefresh();
    }
});
