document.addEventListener('DOMContentLoaded', function() {
    // Login form submission
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            const contact = document.getElementById('contact').value;
            
            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: `contact=${encodeURIComponent(contact)}`
                });
                
                const data = await response.json();
                if (data.success) {
                    location.reload();
                } else {
                    alert('Login failed');
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Login error occurred');
            }
        });
    }
    
    // Setup difficulty inputs when subjects change
    const subjectsInput = document.getElementById('subjects');
    if (subjectsInput) {
        subjectsInput.addEventListener('change', setupDifficultyInputs);
    }
    
    // Plan form submission
    const planForm = document.getElementById('planForm');
    if (planForm) {
        planForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Collect form data
            const subjects = document.getElementById('subjects').value.split(',').map(s => s.trim());
            
            // Collect difficulty data
            const difficulty = {};
            const difficultyInputs = document.querySelectorAll('.difficulty-input select');
            difficultyInputs.forEach(input => {
                const subject = input.getAttribute('data-subject');
                difficulty[subject] = input.value;
            });
            
            const planData = {
                subjects: subjects,
                hours_per_day: parseFloat(document.getElementById('hours_per_day').value),
                study_period: document.getElementById('study_period').value,
                equal_time: document.getElementById('equal_time').value,
                difficulty: difficulty,
                preference: document.getElementById('preference').value,
                exam_scheduled: document.getElementById('exam_scheduled').value,
                break_time: document.getElementById('break_time').value
            };
            
            try {
                const response = await fetch('/generate_plan', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(planData)
                });
                
                const data = await response.json();
                if (data.success) {
                    displayPlan(data.plan);
                } else {
                    alert('Error generating plan: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Error generating study plan');
            }
        });
    }
});

function setupDifficultyInputs() {
    const subjects = document.getElementById('subjects').value.split(',').map(s => s.trim());
    const container = document.getElementById('difficultyInputs');
    container.innerHTML = '';
    
    subjects.forEach(subject => {
        if (!subject) return;
        
        const div = document.createElement('div');
        div.className = 'difficulty-input';
        div.innerHTML = `
            <label style="display:inline-block;width:100px;">${subject}:</label>
            <select data-subject="${subject}">
                <option value="easy">Easy</option>
                <option value="medium" selected>Medium</option>
                <option value="hard">Hard</option>
            </select>
        `;
        container.appendChild(div);
    });
}

function displayPlan(plan) {
    const resultsSection = document.getElementById('resultsSection');
    const resultsDiv = document.getElementById('planResults');
    
    // Display subjects
    let html = `
        <div class="subject-details">
            <h3>Subjects:</h3>
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
        <h3>Daily Schedule:</h3>
    `;
    
       const daysToShow = Math.min(7, plan.total_days);
    for (let i = 0; i < daysToShow; i++) {
        const day = plan.schedule[i];
        html += `
            <div class="day-schedule">
                <h4>Day ${day.day}: ${day.date}</h4>
                ${day.slots.map(slot => `
                    <div class="time-slot ${slot.type === 'break' ? 'break-slot' : ''}">
                        <span><strong>${slot.start_time}</strong> - ${slot.subject || slot.activity}</span>
                        <span>${slot.duration}h</span>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    if (plan.total_days > 7) {
        html += `<p>... and ${plan.total_days - 7} more days</p>`;
    }
    
    resultsDiv.innerHTML = html;
    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

async function savePlan() {
      alert('Plan would be saved to your account. Implementation requires plan ID storage.');
}

async function viewPlan(planId) {
    try {
        const response = await fetch(`/get_plan/${planId}`);
        const data = await response.json();
        if (data.success) {
            displayPlan(data.plan.plan_data);
        }
    } catch (error) {
        console.error('Error:', error);
    }
}

function logout() {
    window.location.href = '/logout';
}