document.addEventListener('DOMContentLoaded', () => {
    const authForms = document.querySelectorAll('.auth-form');
    authForms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (form.id === 'reset-password-form') {
                if (validateResetPasswordForm(form)) {
                    validateForm(form);
                }
            } else {
                validateForm(form);
            }
        });
    });

    function validateForm(form) {
        const inputs = form.querySelectorAll('input');
        let valid = true;
        const button = form.querySelector('button');

        inputs.forEach(input => {
            if (!input.value && input.type !== 'file') {
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

    function validateResetPasswordForm(form) {
        const newPassword = form.querySelector('input[name="password"]');
        const confirmPassword = form.querySelector('input[name="confirm_password"]');
        let valid = true;

        if (newPassword.value !== confirmPassword.value) {
            valid = false;
            showNotification('error', 'Passwords do not match.');
        }

        return valid;
    }

    function submitForm(form, button) {
        const formData = new FormData(form);
        const action = form.getAttribute('action') || window.location.href;

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
                if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    showNotification('success', data.message || 'Operation successful');
                }
            } else {
                showNotification('error', data.message || 'An error occurred');
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