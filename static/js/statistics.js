let currentTeam = 'team1';

async function loadTeamData(team) {
    currentTeam = team;
    document.getElementById('currentTeam').textContent = `${getTeamDisplayName(team)} 리젝 통계`;
    
    try {
        const response = await axios.get(`/ads/history?team=${team}&limit=1000`);
        updateTable(response.data);
        highlightSelectedTeam(team);
    } catch (error) {
        console.error('Error fetching data:', error);
        alert('데이터 로딩 중 오류가 발생했습니다.');
    }
}

function getTeamDisplayName(team) {
    const teamNames = {
        'team1': '1팀',
        'team2A': '2팀A',
        'team2B': '2팀B',
        'team3': '3팀',
        'team4': '4팀',
        'teamOverseas': '해외진출'
    };
    return teamNames[team] || team;
}

function updateTable(ads) {
    const tbody = document.getElementById('adsTable');
    tbody.innerHTML = '';
    
    ads.forEach(ad => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${ad.account_name}</td>
            <td>${ad.campaign}</td>
            <td>${ad.adgroup}</td>
            <td>${ad.ad_name}</td>
            <td>${ad.reject_reason}</td>
            <td>${formatDate(ad.last_modified)}</td>
            <td>${ad.planner_comment || ''}</td>
            <td>${ad.executor_comment || ''}</td>
        `;
        tbody.appendChild(row);
    });
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function highlightSelectedTeam(selectedTeam) {
    document.querySelectorAll('.team-button').forEach(button => {
        if (button.dataset.team === selectedTeam) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// 페이지 로드 시 초기 데이터 로딩
document.addEventListener('DOMContentLoaded', () => {
    loadTeamData('team1');
    document.querySelector('.nav-link[href="/statistics"]').classList.add('active');
    document.querySelector('.nav-link[href="/"]').classList.remove('active');
}); 

async function downloadCurrentTableAsCSV() {
    const team = currentTeam;  // 현재 선택된 팀
    
    try {
        // API 호출하여 CSV 다운로드
        const response = await axios.get(`/ads/export?team=${team}`, {
            responseType: 'blob'
        });
        
        // 파일 다운로드
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', `ads_report_${team}_${new Date().toISOString().split('T')[0]}.csv`);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
    } catch (error) {
        console.error('Error downloading CSV:', error);
        alert('CSV 다운로드 중 오류가 발생했습니다.');
    }
}