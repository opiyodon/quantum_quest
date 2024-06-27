document.addEventListener('DOMContentLoaded', () => {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            validateForm(form);
        });
    });

    function validateForm(form) {
        const inputs = form.querySelectorAll('input');
        let valid = true;
        const button = form.querySelector('button');

        inputs.forEach(input => {
            if (!input.value) {
                valid = false;
                showNotification('error', `Please fill out the ${input.name} field.`);
            }
        });

        if (valid) {
            button.disabled = true;
            button.classList.add('loading');
            submitForm(form, button);
        }
    }

    function submitForm(form, button) {
        const formData = new FormData(form);

        fetch(action, {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            button.disabled = false;
            button.classList.remove('loading');

            if (data.status === 'success') {
                form.reset();
                window.location.href = data.redirect || 'index.html';
            } else {
                showNotification('error', data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('error', 'An error occurred during form submission.');
            button.disabled = false;
            button.classList.remove('loading');
        });
    }

    function showNotification(type, message) {
        const notificationContainer = document.getElementById('notification-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const notificationContent = `
            <div class="notification-header">
                <span>${type === 'success' ? 'Success' : 'Error'}</span>
                <button class="notification-close">&times;</button>
            </div>
            <p>${message}</p>
            <div class="notification-progress">
                <div class="notification-progress-bar"></div>
            </div>
        `;
        
        notification.innerHTML = notificationContent;
        notificationContainer.appendChild(notification);

        const progressBar = notification.querySelector('.notification-progress-bar');
        const closeButton = notification.querySelector('.notification-close');

        closeButton.addEventListener('click', () => {
            notificationContainer.removeChild(notification);
        });

        const duration = 5000; // 5 seconds
        progressBar.style.transition = `width ${duration}ms linear`;
        setTimeout(() => {
            progressBar.style.width = '100%';
        }, 10);

        setTimeout(() => {
            notificationContainer.removeChild(notification);
        }, duration);
    }
});
