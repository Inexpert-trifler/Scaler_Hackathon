let currentSessionId = null;

const els = {
    btnReset: document.getElementById('reset-btn'),
    btnStep: document.getElementById('step-btn'),
    selectDiff: document.getElementById('difficulty-select'),
    taskDesc: document.getElementById('task-desc'),
    inputData: document.getElementById('input-data'),
    stepCounter: document.getElementById('step-counter'),
    statDiff: document.getElementById('stat-diff'),
    statReward: document.getElementById('stat-reward'),
    promptInput: document.getElementById('prompt-input'),
    historyContainer: document.getElementById('history-container')
};

async function apiCall(endpoint, method, payload = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json'
        }
    };
    if (payload) {
        options.body = JSON.stringify(payload);
    }
    try {
        const res = await fetch(`/${endpoint}`, options);
        if (!res.ok) throw new Error('API Error');
        return await res.json();
    } catch (err) {
        console.error(err);
        alert('Action Failed. Ensure backend is running.');
        return null;
    }
}

els.btnReset.addEventListener('click', async () => {
    els.btnReset.disabled = true;
    els.btnReset.textContent = "Initializing...";
    
    const diff = els.selectDiff.value;
    const data = await apiCall('reset', 'POST', { difficulty: diff });
    
    if (data) {
        currentSessionId = data.session_id;
        
        // Update UI
        const obs = data.observation;
        els.taskDesc.textContent = obs.task_description;
        els.inputData.textContent = obs.input_data;
        els.statDiff.textContent = obs.difficulty.toUpperCase();
        els.stepCounter.textContent = `Step: 0`;
        els.statReward.textContent = "0.00";
        els.historyContainer.innerHTML = '';
        els.promptInput.value = '';
        
        els.promptInput.disabled = false;
        els.btnStep.disabled = false;
    }
    
    els.btnReset.textContent = "Initialize Environment";
    els.btnReset.disabled = false;
});

els.btnStep.addEventListener('click', async () => {
    const prompt = els.promptInput.value.trim();
    if (!prompt || !currentSessionId) return;
    
    els.btnStep.disabled = true;
    const data = await apiCall('step', 'POST', {
        session_id: currentSessionId,
        action: { prompt: prompt }
    });
    
    if (data) {
        const obs = data.observation;
        const reward = data.reward;
        
        // Update Panel
        els.stepCounter.textContent = `Step: ${obs.step}`;
        
        // Add to history
        const historyHtml = `
            <div class="history-item">
                <div class="history-prompt">${prompt}</div>
                <div class="history-result">
                    <span class="result-output">Output: ${obs.last_llm_output || '...'}</span>
                    <span class="result-score">Reward: ${reward.toFixed(2)}</span>
                </div>
            </div>
        `;
        els.historyContainer.insertAdjacentHTML('beforeend', historyHtml);
        els.historyContainer.scrollTop = els.historyContainer.scrollHeight;
        
        // Update reward
        els.statReward.textContent = reward.toFixed(2);
        els.promptInput.value = '';
        
        if (data.done) {
            els.promptInput.disabled = true;
            els.historyContainer.insertAdjacentHTML('beforeend', `<div style="color: #10b981; text-align: center; margin-top: 10px; font-weight: bold;">Episode Complete</div>`);
        } else {
            els.btnStep.disabled = false;
            els.promptInput.focus();
        }
    } else {
        els.btnStep.disabled = false;
    }
});
