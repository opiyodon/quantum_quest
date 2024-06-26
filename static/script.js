const socket = io();

function sendMessage() {
    const input = document.getElementById('user-input');
    const message = input.value;
    input.value = '';
    
    addMessageToChat('You', message);
    
    socket.emit('message', {text: message, subject: 'physics', difficulty: 'medium', user_id: 'user123'});
}

socket.on('question', (data) => {
    addMessageToChat('Quantum Quest', data.text);
});

socket.on('result', (data) => {
    const resultText = data.correct ? 'Correct!' : 'Incorrect.';
    addMessageToChat('Quantum Quest', `${resultText} ${data.explanation}`);
});

socket.on('progress', (data) => {
    let progressText = 'Your Progress:\n';
    data.progress.forEach(p => {
        progressText += `${p.subject}: ${p.correct_answers}/${p.total_questions}\n`;
    });
    addMessageToChat('Quantum Quest', progressText);
});

socket.on('hint', (data) => {
    addMessageToChat('Quantum Quest', `Hint: ${data.hint}`);
});

function addMessageToChat(sender, message) {
    const chatMessages = document.getElementById('chat-messages');
    const messageElement = document.createElement('div');
    messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}