const socket = io();

let isRecording = false;
let mediaRecorder;
let audioChunks = [];

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value.trim();
    if (message) {
        input.value = '';
        addMessageToChat('You', message, 'user-message');
        socket.emit('user_message', { message: message });
    }
}

socket.on('bot_message', (data) => {
    addMessageToChat('Quantum Quest', data.message, 'bot-message');
});

socket.on('bot_question', (data) => {
    addMessageToChat('Quantum Quest', data.question, 'bot-message');
});

socket.on('bot_result', (data) => {
    const resultText = data.correct ? 'Correct!' : 'Incorrect.';
    addMessageToChat('Quantum Quest', `${resultText} ${data.explanation}`, 'bot-message');
});

socket.on('bot_progress', (data) => {
    let progressText = 'Your Progress:\n';
    Object.entries(data.progress).forEach(([subject, stats]) => {
        progressText += `${subject}: ${stats.correct_answers}/${stats.total_questions}\n`;
    });
    addMessageToChat('Quantum Quest', progressText, 'bot-message');
});

socket.on('bot_hint', (data) => {
    addMessageToChat('Quantum Quest', `Hint: ${data.hint}`, 'bot-message');
});

function addMessageToChat(sender, message, className) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.className = `message ${className}`;
    messageElement.innerHTML = `
        <div class="sender">${sender}</div>
        <div class="message-content">${message}</div>
    `;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
});

document.getElementById('send-btn').addEventListener('click', sendMessage);

document.getElementById('close-btn').addEventListener('click', function() {
    if (confirm('Are you sure you want to close Quantum Quest?')) {
        window.close();
    }
});


document.addEventListener("DOMContentLoaded", function() {
    const userInput = document.getElementById("user-input");
    const defaultHeight = "30px";

    userInput.addEventListener("input", function() {
        // Reset textarea height to auto to shrink if needed
        userInput.style.height = "auto";
        
        // Calculate the scroll height and set it as the new height
        userInput.style.height = userInput.scrollHeight + "px";

        // Set default height when input is empty
        if (userInput.value.trim() === "") {
            userInput.style.height = defaultHeight;
        }
    });
});


document.getElementById('mic-btn').addEventListener('click', toggleRecording);

async function toggleRecording() {
    if (!isRecording) {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            startRecording(stream);
        } catch (err) {
            console.error('Error accessing microphone:', err);
            alert('Unable to access the microphone. Please check your permissions.');
        }
    } else {
        stopRecording();
    }
}

function startRecording(stream) {
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];

    mediaRecorder.addEventListener('dataavailable', event => {
        audioChunks.push(event.data);
    });

    mediaRecorder.addEventListener('stop', sendAudioToServer);

    mediaRecorder.start();
    isRecording = true;
    document.getElementById('mic-btn').style.color = 'red';
}

function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
        isRecording = false;
        document.getElementById('mic-btn').style.color = '#90adcb';
    }
}

function sendAudioToServer() {
    const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recording.webm');

    fetch('/transcribe', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcription) {
            document.getElementById('user-input').value = data.transcription;
            sendMessage();
        } else {
            console.error('Transcription failed:', data.error);
            alert('Sorry, I couldn\'t understand that. Could you try again?');
        }
    })
    .catch(error => {
        console.error('Error sending audio to server:', error);
        alert('There was an error processing your speech. Please try again.');
    });
}

// Initialize the chat with a welcome message
window.addEventListener('load', () => {
    socket.emit('start_chat');
});
