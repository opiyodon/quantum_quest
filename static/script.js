const socket = io();

document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const chatHistoryList = document.getElementById('chat-history-list');
    const clearHistoryBtn = document.getElementById('clear-history');
    const newChatBtn = document.getElementById('new-chat-btn');
    const notificationContainer = document.getElementById('notification-container');
    const profileImg = document.getElementById('profile-img');
    const profileBtn = document.getElementById('profile-btn');
    const profileModal = document.getElementById('profile-modal');
    const closeModal = document.getElementsByClassName('close')[0];
    const profileForm = document.getElementById('profile-form');
    const deleteAccountBtn = document.getElementById('delete-account');

    let isRecording = false;
    let mediaRecorder;

    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            addMessageToChat('You', message, 'user-message');
            socket.emit('user_message', { message: message });
            userInput.value = '';
        }
    }

    function addMessageToChat(sender, message, className) {
        const messageElement = document.createElement('div');
        messageElement.className = `message ${className}`;
        messageElement.innerHTML = `
            <div class="sender">${sender}</div>
            <div class="message-content">${marked.parse(message)}</div>
            <div class="timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    sendBtn.addEventListener('click', sendMessage);
    userInput.addEventListener('keypress', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    socket.on('bot_message', function (data) {
        addMessageToChat('Quantum Quest', data.message, 'bot-message');
    });

    micBtn.addEventListener('click', toggleRecording);

    async function toggleRecording() {
        if (!isRecording) {
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start();
                isRecording = true;
                micBtn.classList.add('recording');

                const audioChunks = [];
                mediaRecorder.addEventListener("dataavailable", event => {
                    audioChunks.push(event.data);
                });

                mediaRecorder.addEventListener("stop", () => {
                    const audioBlob = new Blob(audioChunks);
                    sendAudioToServer(audioBlob);
                });

            } catch (err) {
                console.error('Error accessing microphone:', err);
            }
        } else {
            mediaRecorder.stop();
            isRecording = false;
            micBtn.classList.remove('recording');
        }
    }

    function sendAudioToServer(audioBlob) {
        const formData = new FormData();
        formData.append("audio", audioBlob);

        fetch('/transcribe', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.transcription) {
                    userInput.value = data.transcription;
                    sendMessage();
                }
            })
            .catch(error => console.error('Error:', error));
    }

    profileImg.onclick = function (event) {
        event.stopPropagation();
        const dropdownContent = document.querySelector('.dropdown-content');
        dropdownContent.style.display = dropdownContent.style.display === 'block' ? 'none' : 'block';
    }

    profileBtn.onclick = function () {
        profileModal.style.display = "block";
    }

    closeModal.onclick = function () {
        profileModal.style.display = "none";
    }

    window.onclick = function (event) {
        if (event.target == profileModal) {
            profileModal.style.display = "none";
        }
        if (!event.target.matches('#profile-img')) {
            const dropdowns = document.getElementsByClassName("dropdown-content");
            for (let i = 0; i < dropdowns.length; i++) {
                let openDropdown = dropdowns[i];
                if (openDropdown.style.display === 'block') {
                    openDropdown.style.display = 'none';
                }
            }
        }
    }

    function setupProfileForm() {
        profileForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            fetch('/update_profile', {
                method: 'POST',
                body: formData
            })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('success', data.message);
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500); // 1.5 seconds delay to allow the user to see the success message
                    } else {
                        showNotification('error', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('error', 'An error occurred while updating the profile');
                });
        });
    }

    function setupDeleteAccount() {
        deleteAccountBtn.addEventListener('click', function () {
            showConfirmation('Are you sure you want to delete your account? This action cannot be undone.', function () {
                fetch('/delete_account', {
                    method: 'POST'
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.status === 'success') {
                            showNotification('success', data.message);
                            setTimeout(() => {
                                window.location.href = '/login';
                            }, 2000);
                        } else {
                            showNotification('error', data.message);
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        showNotification('error', 'An error occurred while deleting the account');
                    });
            });
        });
    }

    function loadChatHistory() {
        fetch('/chat_history')
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    chatHistoryList.innerHTML = '';
                    data.history.forEach(chat => {
                        const li = document.createElement('li');
                        li.textContent = chat.user_message.substring(0, 30) + '...';
                        li.onclick = () => loadChat(chat._id);
                        chatHistoryList.appendChild(li);
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    function loadChat(chatId) {
        fetch(`/load_chat/${chatId}`)
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    chatMessages.innerHTML = '';
                    data.chat.forEach(message => {
                        addMessageToChat(message.sender, message.content, message.sender === 'You' ? 'user-message' : 'bot-message');
                    });
                }
            })
            .catch(error => console.error('Error:', error));
    }

    clearHistoryBtn.onclick = function () {
        showConfirmation('Are you sure you want to clear all chat history?', function () {
            fetch('/clear_all_chats')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        showNotification('success', 'Chat history cleared');
                        // Refresh the page after a short delay
                        setTimeout(() => {
                            window.location.reload();
                        }, 1500); // 1.5 seconds delay to allow the user to see the success message
                    } else {
                        showNotification('error', data.message);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('error', 'An error occurred');
                });
        });
    }

    function showNotification(type, message) {
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

    function showConfirmation(message, onConfirm) {
        const confirmation = document.createElement('div');
        confirmation.className = 'confirmation';
        confirmation.innerHTML = `
            <div class="confirmation-header">
                <span>Confirmation</span>
                <button class="confirmation-close">&times;</button>
            </div>
            <p>${message}</p>
            <div class="confirmation-actions">
                <button class="confirm-yes">Yes</button>
                <button class="confirm-no">No</button>
            </div>
        `;
        notificationContainer.appendChild(confirmation);

        const closeButton = confirmation.querySelector('.confirmation-close');
        const yesButton = confirmation.querySelector('.confirm-yes');
        const noButton = confirmation.querySelector('.confirm-no');

        closeButton.addEventListener('click', () => {
            notificationContainer.removeChild(confirmation);
        });

        noButton.addEventListener('click', () => {
            notificationContainer.removeChild(confirmation);
        });

        yesButton.addEventListener('click', () => {
            notificationContainer.removeChild(confirmation);
            onConfirm();
        });
    }

    newChatBtn.onclick = function () {
        fetch('/start_new_chat', {
            method: 'POST'
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('success', 'Starting a new chat...');
                    // Refresh the page after a short delay
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000); // 1 second delay to allow the user to see the notification
                } else {
                    showNotification('error', data.message || 'Failed to start a new chat');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('error', 'An error occurred while starting a new chat');
            });
    };

    // Initialize everything
    setupProfileForm();
    setupDeleteAccount();
    loadChatHistory();
});
