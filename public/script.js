const chatContainer = document.getElementById('chatContainer');
const userInput = document.getElementById('userInput');

function formatMessage(text) {
    // Convert markdown-style formatting to HTML
    let formatted = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    // Handle code blocks
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    return formatted;
}

function addMessage(text, isUser = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'bot-message'}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(text);
    
    messageDiv.appendChild(contentDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message bot-message';
    typingDiv.id = 'typing-indicator';
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = '<div class="typing-indicator"><span></span><span></span><span></span></div>';
    
    typingDiv.appendChild(contentDiv);
    chatContainer.appendChild(typingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeTypingIndicator() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    
    if (!message) return;
    
    // Add user message
    addMessage(message, true);
    userInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator();
        
        // Add bot response
        addMessage(data.text);
        
    } catch (error) {
        removeTypingIndicator();
        addMessage('Sorry, I encountered an error. Please try again.');
        console.error('Error:', error);
    }
}

function sendQuickQuestion(question) {
    userInput.value = question;
    sendMessage();
}

function handleKeyPress(event) {
    if (event.key === 'Enter') {
        sendMessage();
    }
}

// Health check and model info
async function checkModelInfo() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    
    // Display model info in UI
    const modelInfo = document.createElement('div');
    modelInfo.className = 'model-info';
    modelInfo.innerHTML = `
      <span class="model-badge">${data.mode.toUpperCase()}</span>
      ${data.model ? `<span class="model-name">${data.model}</span>` : ''}
    `;
    
    const header = document.querySelector('.chat-header');
    if (header && !document.querySelector('.model-info')) {
      header.appendChild(modelInfo);
    }
  } catch (error) {
    console.error('Failed to fetch model info:', error);
  }
}

// Check model info on load
checkModelInfo();

// Focus input on load
userInput.focus();
