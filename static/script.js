document.addEventListener('DOMContentLoaded', function () {
    // Initialize common interactions
});

function toggleTask(taskId) {
    const btn = document.getElementById(`btn-toggle-${taskId}`);
    // Optimistic UI update: toggle immediately
    const icon = btn.querySelector('i');
    const originalClass = icon.className;

    // Send request
    fetch(`/toggle/${taskId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const card = document.getElementById(`task-${taskId}`);
                const badge = document.getElementById(`status-badge-${taskId}`);

                if (data.new_state) {
                    // Task is now completed
                    card.classList.add('completed');
                    icon.className = 'bi bi-arrow-counterclockwise';
                    btn.className = 'btn btn-sm btn-outline-secondary';
                    btn.title = 'Mark Incomplete';

                    badge.className = 'badge bg-success rounded-pill';
                    badge.innerHTML = '<i class="bi bi-check-circle"></i> Done';
                } else {
                    // Task is now pending
                    card.classList.remove('completed');
                    icon.className = 'bi bi-check-lg';
                    btn.className = 'btn btn-sm btn-outline-success';
                    btn.title = 'Mark Complete';

                    badge.className = 'badge bg-warning text-dark rounded-pill';
                    badge.innerHTML = '<i class="bi bi-clock"></i> Pending';
                }
            } else {
                console.error('Error:', data.message);
                // Revert on error could be implemented here
                alert('Failed to update task: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred. Please try again.');
        });
}

function deleteTask(taskId) {
    if (!confirm('Are you sure you want to delete this task?')) return;

    const card = document.getElementById(`task-${taskId}`);
    card.classList.add('slide-out');

    fetch(`/delete/${taskId}`, {
        method: 'POST',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Remove element after animation
                setTimeout(() => {
                    card.remove();
                    // Optionally check if list is empty and show empty state
                }, 500);
            } else {
                card.classList.remove('slide-out'); // Revert animation
                alert('Failed to delete task: ' + data.message);
            }
        })
        .catch(error => {
            card.classList.remove('slide-out');
            console.error('Error:', error);
            alert('An error occurred deleting the task.');
        });
}
