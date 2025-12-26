document.addEventListener('DOMContentLoaded', async function () {
    // Always check login on load
    await checkLoginStatus();
});

// ================= LOGIN =================

async function handleLogin(event) {
    event.preventDefault();

    const contact = document.getElementById('contact').value.trim();
    if (!contact) {
        alert('Please enter email or phone');
        return;
    }

    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ contact })
        });

        const data = await response.json();

        if (data.success) {
            currentUser = {
                id: data.user_id,
                contact: data.contact
            };
            showDashboard();   // ❗ NO reload
        } else {
            alert(data.error || 'Login failed');
        }

    } catch (error) {
        console.error('Login Error:', error);
        alert('Login error occurred');
    }
}

// ================= DASHBOARD =================

function setupEventListeners() {

    const subjectsInput = document.getElementById('subjects');
    if (subjectsInput) {
        subjectsInput.addEventListener('input', setupDifficultyInputs);
    }

    const planForm = document.getElementById('planForm');
    if (planForm) {
        planForm.addEventListener('submit', handlePlanGeneration);
    }
}

// ================= PLAN GENERATION =================

async function handlePlanGeneration(event) {
    event.preventDefault();

    const subjects = document.getElementById('subjects')
        .value.split(',')
        .map(s => s.trim())
        .filter(Boolean);

    const difficulty = {};
    document.querySelectorAll('.difficulty-input select').forEach(input => {
        difficulty[input.dataset.subject] = input.value;
    });

    const planData = {
        subjects: subjects.join(','),
        hours_per_day: parseFloat(document.getElementById('hours_per_day').value),
        study_period: document.getElementById('study_period').value,
        equal_time: document.getElementById('equal_time').value,
        difficulty: difficulty,
        preference: document.getElementById('preference').value,
        exam_scheduled: document.getElementById('exam_scheduled').value,
        break_time: document.getElementById('break_time').value
    };

    try {
        const response = await fetch('/api/generate_plan', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(planData)
        });

        const data = await response.json();

        if (data.success) {
            displayPlan(data.plan);
        } else {
            alert(data.error || 'Plan generation failed');
        }

    } catch (error) {
        console.error('Plan Error:', error);
        alert('Error generating study plan');
    }
}

// ================= UI HELPERS =================

function setupDifficultyInputs() {
    const subjects = document.getElementById('subjects')
        .value.split(',')
        .map(s => s.trim())
        .filter(Boolean);

    const container = document.getElementById('difficultyInputs');
    container.innerHTML = '';

    subjects.forEach(subject => {
        container.innerHTML += `
            <div class="difficulty-input">
                <label style="width:100px;">${subject}</label>
                <select data-subject="${subject}">
                    <option value="easy">Easy</option>
                    <option value="medium" selected>Medium</option>
                    <option value="hard">Hard</option>
                </select>
            </div>
        `;
    });
}

function displayPlan(plan) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsDiv = document.getElementById('planResults');

    let html = `
        <div class="subject-details">
            <h3>Subjects</h3>
            ${plan.subjects.map(s => `
                <div class="subject-tag">
                    ${s.name} (${s.difficulty}, ${s.daily_hours}h/day)
                </div>
            `).join('')}
        </div>

        <div class="plan-summary">
            <p><strong>Total Days:</strong> ${plan.total_days}</p>
            <p><strong>Daily Hours:</strong> ${plan.daily_hours}</p>
        </div>
    `;

    resultsDiv.innerHTML = html;
    resultsSection.style.display = 'block';
}

// ================= LOGOUT =================

function logout() {
    fetch('/api/logout', { method: 'POST' })
        .then(() => showLoginForm());
}
