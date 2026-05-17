// Shared UI behavior for Axiom Planner

window.toggleSection = function(event) {
    const card = event.currentTarget.closest('div.border');
    if (!card) return;
    const details = card.querySelector('.section-details');
    if (!details) return;
    details.classList.toggle('hidden');
    const icon = card.querySelector('.material-symbols-outlined');
    if (icon) {
        icon.textContent = details.classList.contains('hidden') ? 'expand_more' : 'expand_less';
    }
};

function parseCalendarItems(items) {
    const completed = getStoredCompletedTasks();
    return Array.isArray(items) ? items.map(item => ({
        id: item.id,
        date: item.date,
        title: item.title,
        type: item.type,
    })).filter(item => !item.id || !completed[item.id]) : [];
}

function getStoredCompletedTasks() {
    try {
        return JSON.parse(localStorage.getItem('axiomCompletedTasks')) || {};
    } catch {
        return {};
    }
}

function formatMonthYear(date) {
    return date.toLocaleDateString('default', { month: 'long', year: 'numeric' });
}

function normalizeDate(value) {
    const parts = value.split('-');
    return new Date(parts[0], parts[1] - 1, parts[2]);
}

function datesMatch(a, b) {
    return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate();
}

function getDayType(date, items) {
    const found = items.filter(item => {
        if (!item || !item.date) return false;
        const itemDate = normalizeDate(item.date);
        return datesMatch(itemDate, date);
    });
    if (!found.length) return null;
    const title = found.map(item => item.title).join(' / ');
    if (found.some(item => item.type === 'exam')) {
        return { type: 'exam', title };
    }
    return { type: 'assignment', title };
}

function renderCalendar(date, items) {
    const monthLabel = document.getElementById('calendarMonth');
    const grid = document.getElementById('calendarGrid');
    if (!monthLabel || !grid) return;
    const month = date.getMonth();
    const year = date.getFullYear();
    monthLabel.textContent = formatMonthYear(date);
    const firstDay = new Date(year, month, 1);
    const startIndex = firstDay.getDay();
    const totalDays = new Date(year, month + 1, 0).getDate();

    grid.innerHTML = '';
    const itemsData = parseCalendarItems(items || []);
    for (let blank = 0; blank < startIndex; blank++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'calendar-cell rounded-2xl bg-surface p-sm';
        grid.appendChild(emptyCell);
    }
    for (let day = 1; day <= totalDays; day++) {
        const current = new Date(year, month, day);
        const dayType = getDayType(current, itemsData);
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'calendar-cell rounded-2xl p-md text-left transition-colors duration-200 border border-outline-variant/15';
        let label = `<span class="font-medium">${day}</span>`;
        if (dayType) {
            if (dayType.type === 'exam') {
                button.className += ' bg-primary text-on-primary border-transparent';
            } else {
                button.className += ' bg-secondary-container text-on-secondary-container border-transparent';
            }
            label += `<div class='mt-2 text-[11px] opacity-90'>${dayType.type === 'exam' ? 'Exam' : 'Assignment'}</div>`;
            label += `<div class='calendar-tooltip'>${dayType.title}</div>`;
        }
        button.innerHTML = label;
        grid.appendChild(button);
    }
}

function updateSidebarToggleIcon() {
    const wrapper = document.getElementById('sidebarWrapper');
    const toggle = document.querySelector('#sidebarToggle .material-symbols-outlined');
    if (!wrapper || !toggle) return;
    toggle.textContent = wrapper.classList.contains('collapsed') ? 'menu_open' : 'menu';
}

function initUploadFileName() {
    const fileInput = document.getElementById('pdf-upload');
    const uploadMessage = document.getElementById('uploadMessage');
    const uploadDescription = document.getElementById('uploadDescription');
    if (!fileInput || !uploadMessage || !uploadDescription) return;
    fileInput.addEventListener('change', () => {
        const file = fileInput.files && fileInput.files[0];
        if (file) {
            uploadMessage.textContent = `Selected file: ${file.name}`;
            uploadDescription.textContent = 'Ready to upload';
        } else {
            uploadMessage.textContent = 'Drag and drop your academic documents here';
            uploadDescription.textContent = 'PDF only, up to 25MB';
        }
    });
}

function initSidebar() {
    const wrapper = document.getElementById('sidebarWrapper');
    const toggle = document.getElementById('sidebarToggle');
    if (!wrapper || !toggle) return;
    toggle.addEventListener('click', () => {
        wrapper.classList.toggle('collapsed');
        updateSidebarToggleIcon();
    });
    updateSidebarToggleIcon();
}

function initProductivitySystem() {
    const completedKey = 'axiomCompletedTasks';
    const historyKey = 'axiomProductivityHistory';
    const stressHistoryKey = 'axiomStressHistory';
    const sessionsKey = 'axiomPlantPomodoroSessions';
    const taskCards = Array.from(document.querySelectorAll('.completable-task[data-task-id]'));
    const analytics = document.querySelector('.productivity-analytics');

    function formatLocalDateKey(date) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        return `${year}-${month}-${day}`;
    }

    function todayKey(offset = 0) {
        const date = new Date();
        date.setDate(date.getDate() + offset);
        return formatLocalDateKey(date);
    }

    function parseLocalDateKey(value) {
        if (!value) return null;
        const [year, month, day] = value.split('-').map(Number);
        if (!year || !month || !day) return null;
        return new Date(year, month - 1, day);
    }

    function daysFromToday(value) {
        const target = parseLocalDateKey(value);
        if (!target) return 999;
        const today = parseLocalDateKey(todayKey());
        return Math.round((target - today) / 86400000);
    }

    function readJson(key, fallback) {
        try {
            return JSON.parse(localStorage.getItem(key)) || fallback;
        } catch {
            return fallback;
        }
    }

    function writeJson(key, value) {
        localStorage.setItem(key, JSON.stringify(value));
    }

    function getCompletedTasks() {
        return readJson(completedKey, {});
    }

    function getHistory() {
        return readJson(historyKey, {});
    }

    function setHistoryCount(dateKey, count) {
        const history = getHistory();
        history[dateKey] = Math.max(0, count);
        writeJson(historyKey, history);
    }

    function countCompletedOn(dateKey) {
        const completed = getCompletedTasks();
        return Object.values(completed).filter(task => task.date === dateKey).length;
    }

    function syncTodayHistory() {
        setHistoryCount(todayKey(), countCompletedOn(todayKey()));
    }

    function updateRemainingAssignmentCount() {
        const counter = document.getElementById('remainingAssignmentsCount');
        if (!counter) return;
        const remaining = document.querySelectorAll('[data-task-id^="assignment-"][data-remove-on-complete="true"]:not([hidden])').length;
        animateNumber(counter, remaining);
    }

    function updateDueTodayCount() {
        const counter = document.getElementById('tasksDueTodayCount');
        if (!counter) return;
        const today = todayKey();
        const remainingDueToday = Array.from(document.querySelectorAll('[data-task-id^="assignment-"][data-remove-on-complete="true"]:not([hidden])'))
            .filter(card => card.dataset.deadline === today).length;
        animateNumber(counter, remainingDueToday);
    }

    function updateUpcomingExamCount() {
        const counter = document.getElementById('upcomingExamsCount');
        if (!counter) return;
        const remaining = document.querySelectorAll('[data-task-id^="exam-"][data-remove-on-complete="true"]:not([hidden])').length;
        animateNumber(counter, remaining);
    }

    function getRemainingWorkload() {
        return {
            assignments: document.querySelectorAll('[data-task-id^="assignment-"][data-remove-on-complete="true"]:not([hidden])').length,
            exams: document.querySelectorAll('[data-task-id^="exam-"][data-remove-on-complete="true"]:not([hidden])').length,
        };
    }

    function getDeadlineUrgency(daysLeft) {
        if (daysLeft < 0) return 35;
        if (daysLeft <= 1) return 50;
        if (daysLeft <= 3) return 30;
        if (daysLeft <= 7) return 15;
        if (daysLeft <= 14) return 8;
        return 5;
    }

    function getDifficultyWeight(value) {
        const difficulty = Number.parseInt(value || '1', 10);
        return { 1: 5, 2: 10, 3: 20, 4: 30 }[difficulty] || 10;
    }

    function getTaskType(card) {
        const title = (card.dataset.taskTitle || card.querySelector('.task-title')?.textContent || '').toLowerCase();
        const size = Number.parseInt(card.dataset.size || '1', 10);
        if (title.includes('quiz')) return { label: 'Quiz', weight: 5 };
        if (title.includes('project')) return { label: 'Project', weight: 35 };
        if (size >= 3) return { label: 'Large Assignment', weight: 25 };
        if (size === 2) return { label: 'Assignment', weight: 18 };
        return { label: 'Small Assignment', weight: 15 };
    }

    function getCompletionFactor(card) {
        const progress = Math.max(0, Math.min(100, Number.parseFloat(card.dataset.progress || '0') || 0));
        return Math.max(0.1, 1 - (progress / 100));
    }

    function classifyStress(score) {
        if (score >= 86) {
            return {
                level: 'Extreme',
                stat: 'Extreme',
                emoji: '😫',
                message: 'Extreme pressure detected — protect today for urgent deadlines first.',
                recommendation: 'Choose one exam or overdue task and start a focused session now.',
                tone: 'extreme',
            };
        }
        if (score >= 66) {
            return {
                level: 'High',
                stat: 'High',
                emoji: '😟',
                message: 'Heavy workload detected this week.',
                recommendation: 'Prioritize the closest exam or the hardest assignment today.',
                tone: 'high',
            };
        }
        if (score >= 41) {
            return {
                level: 'Medium',
                stat: 'Medium',
                emoji: '😐',
                message: 'Upcoming deadlines may require focus.',
                recommendation: 'Break large tasks into smaller sessions and keep steady momentum.',
                tone: 'medium',
            };
        }
        if (score >= 21) {
            return {
                level: 'Low',
                stat: 'Low',
                emoji: '🙂',
                message: 'Your workload is present, but still manageable.',
                recommendation: 'Start early and keep one calm study block on the calendar.',
                tone: 'low',
            };
        }
        return {
            level: 'Very Low',
            stat: 'Very Low',
            emoji: '😌',
            message: 'You’re in a calm study zone today.',
            recommendation: 'Maintain the rhythm with a light review or planning session.',
            tone: 'very-low',
        };
    }

    function getStressState(assignments, exams) {
        const assignmentCards = Array.from(document.querySelectorAll('[data-task-id^="assignment-"][data-remove-on-complete="true"]:not([hidden])'));
        const examCards = Array.from(document.querySelectorAll('[data-task-id^="exam-"][data-remove-on-complete="true"]:not([hidden])'));
        let rawScore = 0;
        const datedItems = [];

        assignmentCards.forEach(card => {
            const daysLeft = daysFromToday(card.dataset.deadline);
            const taskType = getTaskType(card);
            const itemScore = (
                getDeadlineUrgency(daysLeft)
                + taskType.weight
                + getDifficultyWeight(card.dataset.difficulty)
            ) * getCompletionFactor(card);
            rawScore += itemScore;
            datedItems.push({ type: 'assignment', daysLeft });
        });

        examCards.forEach(card => {
            const daysLeft = daysFromToday(card.dataset.examDate);
            rawScore += getDeadlineUrgency(daysLeft) + 40 + 20;
            datedItems.push({ type: 'exam', daysLeft });
        });

        const closeItems = datedItems.filter(item => item.daysLeft >= 0 && item.daysLeft <= 3);
        if (closeItems.length >= 2) rawScore += 20;
        const hasCloseExam = datedItems.some(item => item.type === 'exam' && item.daysLeft >= 0 && item.daysLeft <= 2);
        const hasCloseAssignment = datedItems.some(item => item.type === 'assignment' && item.daysLeft >= 0 && item.daysLeft <= 2);
        if (hasCloseExam && hasCloseAssignment) rawScore += 20;

        if (assignments + exams === 0) {
            return { ...classifyStress(0), score: 0 };
        }
        const score = Math.min(100, Math.round(rawScore));
        return { ...classifyStress(score), score };
    }

    function renderStressHistory(score) {
        const chart = document.getElementById('stressHistoryChart');
        const history = readJson(stressHistoryKey, {});
        history[todayKey()] = score;
        writeJson(stressHistoryKey, history);
        if (!chart) return;

        const days = getLastSevenDays();
        chart.innerHTML = days.map(day => {
            const value = Math.max(4, history[day.key] || 0);
            return `<span style="height: ${value}%"></span>`;
        }).join('');
    }

    function updateStressAndInsights() {
        const workload = getRemainingWorkload();
        const state = getStressState(workload.assignments, workload.exams);
        const stressCard = document.getElementById('dashboardStressCard');
        const dashboardStress = document.getElementById('dashboardStressLevel');
        const dashboardStressBadge = document.getElementById('dashboardStressBadge');
        const dashboardStressBar = document.getElementById('dashboardStressBar');
        const dashboardStressScore = document.getElementById('dashboardStressScore');
        const insightStressLevel = document.getElementById('insightStressLevel');
        const insightStressEmoji = document.getElementById('insightStressEmoji');
        const insightStressMessage = document.getElementById('insightStressMessage');
        const insightStressRecommendation = document.getElementById('insightStressRecommendation');
        if (stressCard) {
            stressCard.dataset.stressLevel = state.level;
            stressCard.dataset.stressTone = state.tone;
            stressCard.dataset.stressScore = `${state.score}`;
        }
        if (dashboardStress) dashboardStress.textContent = state.stat;
        if (dashboardStressBadge) {
            dashboardStressBadge.textContent = state.level;
            dashboardStressBadge.dataset.stressLevel = state.level;
        }
        if (dashboardStressBar) dashboardStressBar.style.width = `${state.score}%`;
        if (dashboardStressScore) dashboardStressScore.textContent = `${state.score}/100`;
        if (insightStressLevel) insightStressLevel.textContent = state.level;
        if (insightStressEmoji) insightStressEmoji.textContent = state.emoji;
        if (insightStressMessage) insightStressMessage.textContent = state.message;
        if (insightStressRecommendation) insightStressRecommendation.textContent = state.recommendation;
        renderStressHistory(state.score);

        const insightsBody = document.getElementById('axiomInsightsBody');
        if (!insightsBody) return;

        insightsBody.querySelectorAll('.insight-alert').forEach(alert => alert.remove());
        let emptyMessage = document.getElementById('noActiveAlertsMessage');
        if (!emptyMessage) {
            emptyMessage = document.createElement('div');
            emptyMessage.id = 'noActiveAlertsMessage';
            emptyMessage.className = 'p-md bg-surface/50 rounded-lg';
            emptyMessage.innerHTML = '<p class="font-body-md text-on-surface-variant">No active alerts. You’re clear for the week unless new deadlines appear.</p>';
            insightsBody.insertBefore(emptyMessage, insightsBody.firstChild);
        }

        const alerts = [];
        document.querySelectorAll('[data-task-id^="assignment-"][data-remove-on-complete="true"]:not([hidden])').forEach(card => {
            const daysLeft = daysFromToday(card.dataset.deadline);
            const title = card.dataset.taskTitle || card.querySelector('.task-title')?.textContent?.trim() || 'Assignment';
            if (daysLeft < 0) {
                alerts.push(`Assignment '${title}' is overdue!`);
            } else if (daysLeft === 0) {
                alerts.push(`Assignment '${title}' is due today!`);
            } else if (daysLeft <= 3) {
                alerts.push(`Assignment '${title}' is due in ${daysLeft} day(s)!`);
            }
        });
        document.querySelectorAll('[data-task-id^="exam-"][data-remove-on-complete="true"]:not([hidden])').forEach(card => {
            const daysLeft = daysFromToday(card.dataset.examDate);
            const title = card.dataset.taskTitle || card.querySelector('.task-title')?.textContent?.trim() || 'Exam';
            if (daysLeft < 0) {
                alerts.push(`Exam '${title}' has passed.`);
            } else if (daysLeft === 0) {
                alerts.push(`Exam '${title}' is today!`);
            } else if (daysLeft <= 7) {
                alerts.push(`Exam '${title}' is in ${daysLeft} day(s)!`);
            }
        });

        emptyMessage.hidden = alerts.length > 0;
        alerts.reverse().forEach(alertText => {
            const alert = document.createElement('div');
            alert.className = 'insight-alert p-md bg-red-100 rounded-lg border-l-4 border-red-500';
            alert.innerHTML = `
                <p class="font-label-sm text-red-700 uppercase tracking-widest mb-xs">Alert</p>
                <p class="font-body-md text-red-800"></p>
            `;
            alert.querySelector('.font-body-md').textContent = alertText;
            insightsBody.insertBefore(alert, emptyMessage.nextSibling);
        });
    }

    function setTaskCompleted(card, completed) {
        const button = card.querySelector('.done-task-btn');
        const status = card.querySelector('.task-status');
        card.classList.toggle('task-completed', completed);
        card.hidden = completed;
        if (button) {
            button.classList.toggle('is-done', completed);
            button.setAttribute('aria-pressed', completed ? 'true' : 'false');
            button.innerHTML = completed
                ? '<span class="material-symbols-outlined">check_circle</span>Done'
                : '<span class="material-symbols-outlined">check</span>Done';
        }
        if (status) {
            status.textContent = completed ? 'Completed' : 'Pending';
        }
    }

    function hydrateTasks() {
        const completed = getCompletedTasks();
        taskCards.forEach(card => {
            setTaskCompleted(card, Boolean(completed[card.dataset.taskId]));
        });
    }

    function filterCompletedOptions() {
        const completed = getCompletedTasks();
        document.querySelectorAll('option[data-task-id]').forEach(option => {
            if (completed[option.dataset.taskId]) {
                option.remove();
            }
        });
    }

    function animateNumber(element, nextValue, suffix = '') {
        if (!element) return;
        const current = Number.parseInt(element.textContent, 10) || 0;
        const start = performance.now();
        const duration = 650;
        function tick(now) {
            const progress = Math.min(1, (now - start) / duration);
            const eased = 1 - Math.pow(1 - progress, 3);
            const value = Math.round(current + (nextValue - current) * eased);
            element.textContent = `${value}${suffix}`;
            if (progress < 1) {
                window.requestAnimationFrame(tick);
            }
        }
        window.requestAnimationFrame(tick);
    }

    function getLastSevenDays() {
        return Array.from({ length: 7 }, (_, index) => {
            const offset = index - 6;
            const date = new Date();
            date.setDate(date.getDate() + offset);
            return {
                key: formatLocalDateKey(date),
                label: date.toLocaleDateString('en-US', { weekday: 'short' }),
            };
        });
    }

    function calculateStreak(history) {
        let streak = 0;
        for (let offset = 0; offset > -365; offset--) {
            const count = history[todayKey(offset)] || 0;
            if (count <= 0) break;
            streak += 1;
        }
        return streak;
    }

    function getMotivation(completedToday, productivityPercent, streak) {
        if (completedToday === 0) return 'Deep work in progress.';
        if (productivityPercent >= 80) return 'Excellent consistency today.';
        if (streak >= 3) return 'You are building a steady study rhythm.';
        if (completedToday >= 2) return 'You are building momentum.';
        return 'A calm productive session.';
    }

    function renderChart(days, history) {
        const chart = document.getElementById('productivityChart');
        if (!chart) return;
        const values = days.map(day => history[day.key] || 0);
        const max = Math.max(1, ...values);
        chart.innerHTML = days.map((day, index) => {
            const value = values[index];
            const height = Math.max(8, Math.round((value / max) * 100));
            return `
                <div class="chart-day" title="${value} completed">
                    <div class="chart-bar-track">
                        <div class="chart-bar" style="height: ${height}%"></div>
                    </div>
                    <span>${day.label}</span>
                </div>
            `;
        }).join('');
    }

    function updateAnalytics() {
        updateRemainingAssignmentCount();
        updateDueTodayCount();
        updateUpcomingExamCount();
        updateStressAndInsights();
        if (!analytics) return;
        syncTodayHistory();
        const history = getHistory();
        const days = getLastSevenDays();
        const completedToday = history[todayKey()] || 0;
        const focusSessions = Number.parseInt(localStorage.getItem(sessionsKey) || '0', 10);
        const totalTasks = Math.max(Number.parseInt(analytics.dataset.totalTasks || `${taskCards.length}`, 10), taskCards.length, 1);
        const productivityPercent = Math.min(100, Math.round((completedToday / totalTasks) * 100));
        const activeDays = days.filter(day => (history[day.key] || 0) > 0).length;
        const weeklyConsistency = Math.round((activeDays / 7) * 100);
        const streak = calculateStreak(history);

        animateNumber(document.querySelector('[data-analytics-value="completedToday"]'), completedToday);
        animateNumber(document.querySelector('[data-analytics-value="focusSessions"]'), focusSessions);
        animateNumber(document.querySelector('[data-analytics-value="productivityPercent"]'), productivityPercent, '%');
        animateNumber(document.querySelector('[data-analytics-value="weeklyConsistency"]'), weeklyConsistency, '%');
        animateNumber(document.querySelector('[data-analytics-value="studyStreak"]'), streak);

        const message = document.getElementById('productivityMessage');
        if (message) {
            message.textContent = getMotivation(completedToday, productivityPercent, streak);
        }
        renderChart(days, history);
    }

    taskCards.forEach(card => {
        const button = card.querySelector('.done-task-btn');
        if (!button) return;
        button.addEventListener('click', () => {
            const completed = getCompletedTasks();
            const id = card.dataset.taskId;
            if (completed[id]) {
                delete completed[id];
            } else {
                completed[id] = {
                    title: card.dataset.taskTitle || card.querySelector('.task-title')?.textContent?.trim() || 'Task',
                    date: todayKey(),
                    completedAt: new Date().toISOString(),
                };
                button.classList.add('done-pop');
                window.setTimeout(() => button.classList.remove('done-pop'), 700);
            }
            writeJson(completedKey, completed);
            const isDone = Boolean(completed[id]);
            setTaskCompleted(card, isDone);
            updateAnalytics();
            renderCalendar(new Date(), window.calendarItems || []);
            
            // Sync with backend so AI study planner knows it's done
            fetch('/api/toggle_status', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ item_id: id, is_done: isDone })
            }).catch(e => console.error('Failed to sync status:', e));
        });
    });

    hydrateTasks();
    filterCompletedOptions();
    updateAnalytics();
    window.setInterval(updateAnalytics, 60000);
}

function initPlantPomodoro() {
    const card = document.querySelector('.plant-pomodoro-card');
    const display = document.getElementById('timerDisplay');
    const timerMode = document.getElementById('timerMode');
    const message = document.getElementById('focusMessage');
    const completionMessage = document.getElementById('completionMessage');
    const sessionCount = document.getElementById('sessionCount');
    const startButton = document.getElementById('startTimer');
    const pauseButton = document.getElementById('pauseTimer');
    const resetButton = document.getElementById('resetTimer');
    const modeButtons = document.querySelectorAll('.mode-btn');
    const progressRing = document.querySelector('.ring-progress');

    if (!card || !display || !timerMode || !message || !completionMessage || !sessionCount || !startButton || !pauseButton || !resetButton || !progressRing) {
        return;
    }

    const STORAGE_KEY = 'axiomPlantPomodoroSessions';
    const BUDDY_NAME_KEY = 'axiomBuddyName';
    const BLOOM_MESSAGE_KEY = 'axiomPlantLastBloomMessage';
    const radius = progressRing.r.baseVal.value;
    const circumference = 2 * Math.PI * radius;
    let activeMode = 'focus';
    let totalSeconds = 40 * 60;
    let remainingSeconds = totalSeconds;
    let timerId = null;
    let sessions = Number.parseInt(localStorage.getItem(STORAGE_KEY) || '0', 10);

    progressRing.style.strokeDasharray = `${circumference}`;

    const modeLabels = {
        focus: 'Focus Time',
        short: 'Short Break',
        long: 'Long Break',
    };

    const modeMessages = {
        focus: 'Let the room go quiet. Keep growing.',
        short: 'Step back into warmer light for a moment.',
        long: 'The plant has earned a deeper rest.',
    };

    function getUserName() {
        const savedName = localStorage.getItem(BUDDY_NAME_KEY);
        return savedName && savedName.trim() ? savedName.trim() : 'friend';
    }

    function getBloomMessage() {
        const name = getUserName();
        const messages = [
            `Thank you for letting me grow, ${name}. Your focus made this bloom possible.`,
            `I bloomed because you stayed, ${name}. Carry this calm into your next task.`,
            `You gave me time, ${name}, and I turned it into flowers. Your attention matters.`,
            `Look what your patience made, ${name}. A quiet bloom for a focused mind.`,
            `Thank you, ${name}. Every minute you protected became a petal.`,
            `You kept the promise, ${name}. Let this bloom remind you that steady work becomes beautiful.`,
        ];
        const lastIndex = Number.parseInt(localStorage.getItem(BLOOM_MESSAGE_KEY) || '-1', 10);
        let nextIndex = Math.floor(Math.random() * messages.length);
        if (messages.length > 1 && nextIndex === lastIndex) {
            nextIndex = (nextIndex + 1) % messages.length;
        }
        localStorage.setItem(BLOOM_MESSAGE_KEY, `${nextIndex}`);
        return messages[nextIndex];
    }

    function formatTime(seconds) {
        const minutes = Math.floor(seconds / 60).toString().padStart(2, '0');
        const rest = (seconds % 60).toString().padStart(2, '0');
        return `${minutes}:${rest}`;
    }

    function updateProgress() {
        const elapsed = totalSeconds - remainingSeconds;
        const ratio = totalSeconds > 0 ? elapsed / totalSeconds : 0;
        progressRing.style.strokeDashoffset = `${circumference - (ratio * circumference)}`;
    }

    function getPlantStage() {
        if (activeMode !== 'focus') {
            return sessions > 0 ? 5 : 0;
        }
        const elapsed = totalSeconds - remainingSeconds;
        const ratio = totalSeconds > 0 ? elapsed / totalSeconds : 0;
        if (ratio <= 0) return 0;
        if (ratio < 0.22) return 1;
        if (ratio < 0.44) return 2;
        if (ratio < 0.68) return 3;
        if (ratio < 0.78) return 4;
        return 5;
    }

    function getBloomStage() {
        if (activeMode !== 'focus') {
            return sessions > 0 ? 5 : 0;
        }
        const elapsed = totalSeconds - remainingSeconds;
        const ratio = totalSeconds > 0 ? elapsed / totalSeconds : 0;
        if (ratio < 0.78) return 0;
        if (ratio < 0.84) return 1;
        if (ratio < 0.89) return 2;
        if (ratio < 0.94) return 3;
        if (ratio < 0.985) return 4;
        return 5;
    }

    function updatePlantStage() {
        const stage = getPlantStage();
        const bloomStage = getBloomStage();
        card.classList.remove('plant-stage-0', 'plant-stage-1', 'plant-stage-2', 'plant-stage-3', 'plant-stage-4', 'plant-stage-5');
        card.classList.remove('plant-bloom-0', 'plant-bloom-1', 'plant-bloom-2', 'plant-bloom-3', 'plant-bloom-4', 'plant-bloom-5');
        card.classList.add(`plant-stage-${stage}`);
        card.classList.add(`plant-bloom-${bloomStage}`);
        sessionCount.textContent = sessions;
    }

    function render() {
        display.textContent = formatTime(remainingSeconds);
        timerMode.textContent = modeLabels[activeMode] || 'Focus Time';
        message.textContent = modeMessages[activeMode] || modeMessages.focus;
        card.classList.toggle('break-mode', activeMode !== 'focus');
        updateProgress();
        updatePlantStage();
    }

    function stopTimer() {
        if (timerId) {
            window.clearInterval(timerId);
            timerId = null;
        }
        card.classList.remove('plant-growing');
        startButton.disabled = false;
    }

    function setMode(mode, minutes) {
        stopTimer();
        activeMode = mode;
        totalSeconds = minutes * 60;
        remainingSeconds = totalSeconds;
        modeButtons.forEach(button => {
            button.classList.toggle('active-mode', button.dataset.mode === mode);
        });
        render();
    }

    function playCompletionAnimation() {
        card.classList.remove('plant-complete');
        completionMessage.textContent = getBloomMessage();
        window.requestAnimationFrame(() => {
            card.classList.add('plant-complete');
            window.setTimeout(() => {
                card.classList.remove('plant-complete');
                completionMessage.textContent = '';
            }, 5200);
        });
    }

    function completeSession() {
        stopTimer();
        if (activeMode === 'focus') {
            sessions += 1;
            localStorage.setItem(STORAGE_KEY, `${sessions}`);
            playCompletionAnimation();
            const nextMode = sessions % 4 === 0 ? 'long' : 'short';
            const nextButton = Array.from(modeButtons).find(button => button.dataset.mode === nextMode);
            const minutes = Number.parseInt(nextButton ? nextButton.dataset.time : '5', 10);
            setMode(nextMode, minutes);
            message.textContent = sessions % 4 === 0
                ? 'A quiet bloom. Take a long break.'
                : 'A quiet bloom. Take a short break.';
        } else {
            const focusButton = Array.from(modeButtons).find(button => button.dataset.mode === 'focus');
            const minutes = Number.parseInt(focusButton ? focusButton.dataset.time : '40', 10);
            setMode('focus', minutes);
            message.textContent = 'The room is ready. Return gently.';
        }
    }

    startButton.addEventListener('click', () => {
        if (timerId) return;
        startButton.disabled = true;
        card.classList.add('plant-growing');
        timerId = window.setInterval(() => {
            remainingSeconds -= 1;
            if (remainingSeconds <= 0) {
                remainingSeconds = 0;
                render();
                completeSession();
                return;
            }
            render();
        }, 1000);
    });

    pauseButton.addEventListener('click', () => {
        stopTimer();
        message.textContent = 'Paused. The garden holds its breath.';
    });

    resetButton.addEventListener('click', () => {
        stopTimer();
        remainingSeconds = totalSeconds;
        render();
    });

    modeButtons.forEach(button => {
        button.addEventListener('click', () => {
            const minutes = Number.parseInt(button.dataset.time || '25', 10);
            setMode(button.dataset.mode || 'focus', minutes);
        });
    });

    render();
}

window.addEventListener('DOMContentLoaded', () => {
    initSidebar();
    initUploadFileName();
    initProductivitySystem();
    initPlantPomodoro();
    renderCalendar(new Date(), window.calendarItems || []);
});
