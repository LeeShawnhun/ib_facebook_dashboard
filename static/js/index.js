let currentTeam = 'team1';
        
document.addEventListener('DOMContentLoaded', () => {
    loadTeamData('team1');
    updateLastUpdateTime();
});

function updateLastUpdateTime() {
    const updateTimeElement = document.getElementById('updateTime');
    const now = new Date();
    
    const lastUpdateTime = new Date(now);
    
    if (now.getMinutes() < 30) {
        lastUpdateTime.setHours(lastUpdateTime.getHours() - 1);
    }
    
    lastUpdateTime.setMinutes(30);
    lastUpdateTime.setSeconds(0);
    
    const formattedTime = lastUpdateTime.toLocaleString('ko-KR', { 
        year: 'numeric', 
        month: '2-digit', 
        day: '2-digit',
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
    });
    updateTimeElement.textContent = `마지막 업데이트: ${formattedTime}`;
}

function updateActiveButton(team) {
    document.querySelectorAll('.team-button').forEach(button => {
        if (button.getAttribute('data-team') === team) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

async function loadTeamData(team) {
    currentTeam = team;
    const tableBody = document.getElementById('adsTable');
    const loading = document.getElementById('loading');
    const currentTeamElement = document.getElementById('currentTeam');
    
    updateActiveButton(team);
    
    const teamNames = {
        'team1': '1팀',
        'team2A': '2팀A',
        'team2B': '2팀B',
        'team3': '3팀',
        'team4': '4팀',
        'teamOverseas': '해외진출'
    };
    currentTeamElement.textContent = `${teamNames[team]} 광고 현황`;

    loading.style.display = 'block';
    tableBody.innerHTML = '';

    try {
        const url = team === 'all' ? '/ads/' : `/ads/?team=${team}`;
        const response = await axios.get(url);
        const ads = response.data;

        ads.forEach(ad => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${ad.account_name}</td>
                <td>${ad.campaign}</td>
                <td>${ad.adgroup}</td>
                <td>${ad.ad_name}</td>
                <td>${ad.reject_reason}</td>
                <td>${new Date(ad.last_modified).toLocaleString('ko-KR')}</td>
            `;
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error fetching data:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" style="text-align: center; color: #e74c3c;">
                    데이터를 불러오는 중 오류가 발생했습니다.
                </td>
            </tr>
        `;
    } finally {
        loading.style.display = 'none';
    }
}

async function createBackup() {
    try {
        const response = await fetch('/admin/backup', {
            method: 'get',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        alert(data.message);
    } catch (error) {
        console.error('Error:', error);
        alert('백업 생성 중 오류가 발생했습니다: ' + error.message);
    }
}

async function downloadBackup() {
    try {
        const response = await fetch('/admin/download-backup');
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'database_backup.db';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading backup:', error);
    }
}