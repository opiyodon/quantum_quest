const socket = io();

document.addEventListener('DOMContentLoaded', function () {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendBtn = document.getElementById('send-btn');
    const micBtn = document.getElementById('mic-btn');
    const profileImg = document.getElementById('profile-img');
    const profileModal = document.getElementById('profile-modal');
    const closeModal = document.getElementsByClassName('close')[0];
    const profileForm = document.getElementById('profile-form');
    const deleteAccountBtn = document.getElementById('delete-account');
    const chatHistoryList = document.getElementById('chat-history-list');
    const clearHistoryBtn = document.getElementById('clear-history');

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

    profileImg.onclick = function () {
        profileModal.style.display = "block";
    }

    closeModal.onclick = function () {
        profileModal.style.display = "none";
    }

    window.onclick = function (event) {
        if (event.target == profileModal) {
            profileModal.style.display = "none";
        }
    }

    profileForm.onsubmit = function (e) {
        e.preventDefault();
        const formData = new FormData(profileForm);

        fetch('/update_profile', {
            method: 'POST',
            body: formData
        })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    showNotification('Profile updated successfully', 'success');
                    profileModal.style.display = "none";
                } else {
                    showNotification(data.message, 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                showNotification('An error occurred', 'error');
            });
    }

    deleteAccountBtn.onclick = function () {
        if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
            fetch('/delete_account', { method: 'POST' })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        window.location.href = '/login';
                    } else {
                        showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('An error occurred', 'error');
                });
        }
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
        if (confirm('Are you sure you want to clear all chat history?')) {
            fetch('/clear_all_chats')
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'success') {
                        chatHistoryList.innerHTML = '';
                        showNotification('Chat history cleared', 'success');
                    } else {
                        showNotification(data.message, 'error');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('An error occurred', 'error');
                });
        }
    }

    function showNotification(message, type) {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        document.body.appendChild(notification);
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Load chat history on page load
    loadChatHistory();
});