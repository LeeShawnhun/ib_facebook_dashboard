let currentTeam = 'team1';
let editingCell = null;
        
document.addEventListener('DOMContentLoaded', () => {
    loadTeamData('team1');
    updateLastUpdateTime();
    document.querySelector('.nav-link[href="/"]').classList.add('active');
    document.querySelector('.nav-link[href="/statistics"]').classList.remove('active');
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
            console.log('Processing ad:', ad);
            console.log('Planner comment:', ad.planner_comment);
            console.log('Executor comment:', ad.executor_comment);
            
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${ad.account_name || ''}</td>
                <td>${ad.campaign || ''}</td>
                <td>${ad.adgroup || ''}</td>
                <td>${ad.ad_name || ''}</td>
                <td>${ad.reject_reason || ''}</td>
                <td>${new Date(ad.last_modified).toLocaleString('ko-KR')}</td>
                <td class="comment-cell">
                    <div class="comment-display">
                        <span class="comment-text">${ad.planner_comment || ''}</span>
                        <button class="edit-button" onclick="startEditing('${ad.ad_id}', 'planner')">
                            ✏️
                        </button>
                    </div>
                    <div class="comment-edit" style="display: none;">
                        <textarea class="comment-input planner-comment" data-ad-id="${ad.ad_id}">${ad.planner_comment || ''}</textarea>
                        <div class="edit-buttons">
                            <button class="save-button" onclick="saveComments('${ad.ad_id}')">저장</button>
                            <button class="cancel-button" onclick="cancelEditing('${ad.ad_id}', 'planner')">취소</button>
                        </div>
                    </div>
                </td>
                <td class="comment-cell">
                    <div class="comment-display">
                        <span class="comment-text">${ad.executor_comment || ''}</span>
                        <button class="edit-button" onclick="startEditing('${ad.ad_id}', 'executor')">
                            ✏️
                        </button>
                    </div>
                    <div class="comment-edit" style="display: none;">
                        <textarea class="comment-input executor-comment" data-ad-id="${ad.ad_id}">${ad.executor_comment || ''}</textarea>
                        <div class="edit-buttons">
                            <button class="save-button" onclick="saveComments('${ad.ad_id}')">저장</button>
                            <button class="cancel-button" onclick="cancelEditing('${ad.ad_id}', 'executor')">취소</button>
                        </div>
                    </div>
                </td>
            `;
            tableBody.appendChild(row);
        });

    } catch (error) {
        console.error('Error details:', error);
        console.error('Error response:', error.response);
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" style="text-align: center; color: #e74c3c;">
                    데이터를 불러오는 중 오류가 발생했습니다.
                </td>
            </tr>
        `;
    } finally {
        loading.style.display = 'none';
    }
}

function startEditing(adId, type) {
    const cell = document.querySelector(`td.comment-cell .${type}-comment[data-ad-id="${adId}"]`).closest('.comment-cell');
    const displayDiv = cell.querySelector('.comment-display');
    const editDiv = cell.querySelector('.comment-edit');
    
    displayDiv.style.display = 'none';
    editDiv.style.display = 'block';
    
    const textarea = editDiv.querySelector('textarea');
    textarea.focus();
    editingCell = { adId, type };
}

function cancelEditing(adId, type) {
    const cell = document.querySelector(`td.comment-cell .${type}-comment[data-ad-id="${adId}"]`).closest('.comment-cell');
    const displayDiv = cell.querySelector('.comment-display');
    const editDiv = cell.querySelector('.comment-edit');
    
    displayDiv.style.display = 'flex';
    editDiv.style.display = 'none';
    editingCell = null;
}

async function saveComments(adId) {
    const plannerComment = document.querySelector(`.planner-comment[data-ad-id="${adId}"]`).value;
    const executorComment = document.querySelector(`.executor-comment[data-ad-id="${adId}"]`).value;
    
    try {
        await axios.put(`/ads/${adId}/comments`, {
            planner_comment: plannerComment,
            executor_comment: executorComment
        });
        
        // Update the displayed text
        const plannerDisplay = document.querySelector(`.planner-comment[data-ad-id="${adId}"]`)
            .closest('.comment-cell')
            .querySelector('.comment-text');
        const executorDisplay = document.querySelector(`.executor-comment[data-ad-id="${adId}"]`)
            .closest('.comment-cell')
            .querySelector('.comment-text');
            
        plannerDisplay.textContent = plannerComment;
        executorDisplay.textContent = executorComment;
        
        // Hide edit mode
        if (editingCell && editingCell.adId === adId) {
            cancelEditing(adId, editingCell.type);
        }
        
        alert('의견이 저장되었습니다.');
    } catch (error) {
        console.error('Error saving comments:', error);
        alert('의견 저장에 실패했습니다.');
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