const chatContainer = document.getElementById('chat-container');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

function addMessage(message, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `d-flex mb-3 ${isUser ? 'justify-content-end' : 'justify-content-start'}`;

    const bubble = document.createElement('div');
    bubble.className = `chat-bubble ${isUser ? 'user' : 'ai'}`;
    bubble.innerHTML = `<strong>${isUser ? 'You' : 'E-Parchi AI'}:</strong> ${message}`;

    messageDiv.appendChild(bubble);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTyping() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'd-flex mb-3 justify-content-start';
    typingDiv.id = 'typing-indicator';

    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble ai';
    bubble.innerHTML = '<div class="typing-indicator me-2"></div> AI is thinking...';

    typingDiv.appendChild(bubble);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function hideTyping() {
    const typing = document.getElementById('typing-indicator');
    if (typing) typing.remove();
}

function setLoading(loading) {
    sendBtn.disabled = loading;
    userInput.disabled = loading;
    if (loading) {
        sendBtn.innerHTML = '<div class="spinner-border spinner-border-sm" role="status"></div>';
    } else {
        sendBtn.innerHTML = '<i class="fas fa-paper-plane"></i>';
    }
}

async function sendMessage(message = null) {
    const msg = message || userInput.value.trim();
    if (!msg) return;

    addMessage(msg, true);
    userInput.value = '';

    // Hide suggestion chips after first message
    const suggestionChips = document.getElementById('suggestion-chips');
    if (suggestionChips) {
        suggestionChips.style.display = 'none';
    }

    showTyping();
    setLoading(true);

    try {
        const response = await fetch('/api/assistant/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: msg }),
        });

        const data = await response.json();

        if (response.ok) {
            hideTyping();
            addMessage(data.reply);
        } else {
            hideTyping();
            addMessage('Sorry, I\'m having trouble connecting right now. Please try again in a moment.');
        }
    } catch (error) {
        console.error('Chat error:', error);
        hideTyping();
        addMessage('Sorry, I\'m having trouble connecting right now. Please try again in a moment.');
    } finally {
        setLoading(false);
    }
}

function sendSuggestion(message) {
    userInput.value = message;
    sendMessage(message);
}

function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Initialize with welcome message
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        addMessage('👋 Hello! I\'m your AI Health Assistant. I can help you with:\n\n• Finding the right hospital department for your symptoms\n• Understanding how the queue system works\n• Getting recommendations for doctors\n• General healthcare guidance\n\nWhat can I help you with today?');
    }, 500);
});