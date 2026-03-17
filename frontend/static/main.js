/**
 * Main frontend logic for RKLLM Chat
 */

let client = null;
let conversationHistory = [];
let currentImage = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', async () => {
    await initializeApp();
});

/**
 * Initialize the application
 */
async function initializeApp() {
    try {
        // Fetch configuration
        const configResponse = await fetch('/api/config');
        const config = await configResponse.json();

        // Initialize RKLLM client
        client = new window.RKLLMClient(config);

        // Update UI with config
        document.getElementById('model-name').textContent = config.model;
        
        // Set max character limit based on context
        const maxChars = Math.min(1000, Math.floor(config.max_context_length / 4));
        document.getElementById('message-input').maxLength = maxChars;

        updateStatus('Ready');
    } catch (error) {
        console.error('Initialization error:', error);
        updateStatus('Error: Failed to connect', 'error');
    }
}

/**
 * Handle image selection
 */
function handleImageSelect(event) {
    const file = event.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError('Please select a valid image file');
        return;
    }

    // Validate file size (10MB max)
    if (file.size > 10 * 1024 * 1024) {
        showError('Image size must be less than 10MB');
        return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
        currentImage = e.target.result;
        showImagePreview(e.target.result);
        clearError();
    };
    reader.onerror = () => {
        showError('Failed to read image file');
    };
    reader.readAsDataURL(file);
}

/**
 * Show image preview
 */
function showImagePreview(dataUrl) {
    const container = document.getElementById('image-preview-container');
    const img = document.getElementById('image-preview');
    img.src = dataUrl;
    container.classList.remove('hidden');
}

/**
 * Clear selected image
 */
function clearImage() {
    currentImage = null;
    document.getElementById('image-preview-container').classList.add('hidden');
    document.getElementById('image-input').value = '';
}

/**
 * Send message to API
 */
async function sendMessage() {
    const input = document.getElementById('message-input');
    const message = input.value.trim();

    if (!message) {
        showError('Please enter a message');
        return;
    }

    if (!client) {
        showError('Client not initialized');
        return;
    }

    // Save image before clearing
    const imageToSend = currentImage;

    // Add user message to UI
    addMessage('user', message, imageToSend);
    conversationHistory.push({ role: 'user', content: message, image: imageToSend });

    // Add AI response placeholder
    addMessage('assistant', '');

    // Clear input and image
    input.value = '';
    clearImage();
    updateCharCount();

    // Show loading state
    const sendButton = document.getElementById('send-button');
    sendButton.disabled = true;
    updateStatus('Processing...');

    try {
        // Send message with streaming
        let fullResponse = '';
        await client.sendMessage(message, imageToSend, (chunk) => {
            fullResponse += chunk;
            updateLastMessage(fullResponse);
        });

        // Add AI response to history
        conversationHistory.push({ role: 'assistant', content: fullResponse });
        updateStatus('Ready');
    } catch (error) {
        console.error('Error:', error);
        showError(`Error: ${error.message}`);
        updateStatus('Error', 'error');

        // Remove incomplete message if streaming failed
        const messagesDiv = document.getElementById('chat-messages');
        const lastMsg = messagesDiv.lastElementChild;
        if (lastMsg && lastMsg.dataset.contentId) {
            lastMsg.remove();
        }
    } finally {
        sendButton.disabled = false;
        input.focus();
    }
}

/**
 * Add message to chat UI
 */
function addMessage(role, content, imageUrl = null) {
    const messagesDiv = document.getElementById('chat-messages');

    // Clear welcome message if this is the first message
    if (conversationHistory.length === 0) {
        messagesDiv.innerHTML = '';
    }

    // Create message element
    const messageDiv = document.createElement('div');
    messageDiv.className = 'chat-message';

    if (role === 'user') {
        messageDiv.innerHTML = `
            <div class="flex justify-end mb-4">
                <div class="msg-user rounded-lg px-4 py-3 max-w-2xl">
                    <p class="break-words">${escapeHtml(content)}</p>
                    ${imageUrl ? `<img src="${imageUrl}" class="image-preview mt-3">` : ''}
                </div>
            </div>
        `;
    } else {
        // Generate unique ID for each AI message to avoid conflicts
        const messageId = 'ai-msg-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
        messageDiv.innerHTML = `
            <div class="flex justify-start mb-4">
                <div class="msg-ai rounded-lg px-4 py-3 max-w-2xl">
                    <p class="break-words whitespace-pre-wrap" id="${messageId}"></p>
                </div>
            </div>
        `;
        // Store the ID on the messageDiv for later reference
        messageDiv.dataset.contentId = messageId;
    }

    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * Update the last message with streaming content
 */
function updateLastMessage(content) {
    const messagesDiv = document.getElementById('chat-messages');
    const lastMessage = messagesDiv.lastElementChild;
    
    if (lastMessage && lastMessage.dataset.contentId) {
        const contentDiv = document.getElementById(lastMessage.dataset.contentId);
        if (contentDiv) {
            contentDiv.textContent = content;
            // Scroll chat area to bottom
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    }
}

/**
 * Clear conversation context
 */
function clearContext() {
    if (confirm('确定要清空对话历史吗？')) {
        conversationHistory = [];
        currentImage = null;
        document.getElementById('chat-messages').innerHTML = `
            <div class="text-center py-12">
                <p class="text-3xl mb-3">👋</p>
                <p class="text-xl font-bold text-gray-800 mb-2">欢迎使用 RKLLM Chat</p>
                <p class="text-gray-600">输入文本或上传图片开始对话</p>
            </div>
        `;
        clearError();
    }
}

/**
 * Update status indicator
 */
function updateStatus(message, type = 'info') {
    const statusEl = document.getElementById('status');
    statusEl.textContent = message;
    if (type === 'error') {
        statusEl.htmlContent = '❌ ' + message;
        statusEl.className = 'text-xs text-error font-semibold';
    } else if (type === 'warning') {
        statusEl.textContent = '⚠️ ' + message;
        statusEl.className = 'text-xs text-warning font-semibold';
    } else {
        statusEl.textContent = '✨ ' + message;
        statusEl.className = 'text-xs text-success font-semibold';
    }
}

/**
 * Show error message
 */
function showError(message) {
    const errorEl = document.getElementById('error-message');
    errorEl.innerHTML = '⚠️ ' + escapeHtml(message);
    errorEl.classList.remove('hidden');
    updateStatus('Error', 'error');
}

/**
 * Clear error message
 */
function clearError() {
    const errorEl = document.getElementById('error-message');
    errorEl.textContent = '';
    errorEl.classList.add('hidden');
}

/**
 * Update character count
 */
function updateCharCount() {
    const input = document.getElementById('message-input');
    const count = document.getElementById('char-count');
    count.textContent = `${input.value.length}/${input.maxLength} characters`;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Update character count on input
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('message-input');
    if (input) {
        input.addEventListener('input', updateCharCount);
    }
});
