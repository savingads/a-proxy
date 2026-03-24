document.addEventListener('DOMContentLoaded', function () {
    const messageContainer = document.getElementById('messageContainer');
    const messageInput = document.getElementById('messageInput');
    const sendMessageBtn = document.getElementById('sendMessage');
    const resetChatBtn = document.getElementById('resetChat');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const llmModelSelect = document.getElementById('llmModel');
    const systemPromptInput = document.getElementById('systemPrompt');

    // Store conversation history
    let conversationHistory = [];
    let conversationId = Date.now().toString();

    // Show error message
    function showError(message) {
        const errorElement = document.getElementById('errorMessage');
        const errorText = document.getElementById('errorText');
        
        errorText.textContent = message;
        errorElement.style.display = 'block';
        
        // Auto-hide after 8 seconds
        setTimeout(() => {
            errorElement.style.display = 'none';
        }, 8000);
    }

    // Function to add a message to the chat
    function addMessage(message, sender) {
        // Add to UI
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'agent-message');

        const messagePara = document.createElement('p');
        messagePara.innerText = message;
        messageDiv.appendChild(messagePara);

        messageContainer.appendChild(messageDiv);

        // Scroll to bottom
        messageContainer.scrollTop = messageContainer.scrollHeight;

        // Add to history
        conversationHistory.push({
            sender: sender,
            message: message,
            timestamp: new Date().toISOString()
        });
    }

    // Function to send message to agent
    async function sendToAgent(message) {
        try {
            console.log("Sending message to Claude:", message);
            loadingIndicator.style.display = 'block';

            // Get current settings
            const model = llmModelSelect.value;
            const systemPrompt = systemPromptInput.value;

            console.log("Using model:", model);
            console.log("Using system prompt:", systemPrompt);

            const response = await fetch(`/agent/message`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    message: message,
                    conversation_id: conversationId,
                    model: model,
                    system_prompt: systemPrompt
                })
            });

            console.log("Response status:", response.status);
            
            if (!response.ok) {
                const errorText = await response.text();
                console.error("Error response:", errorText);
                throw new Error(`Failed to get response from agent: ${response.status} ${errorText}`);
            }

            const data = await response.json();
            console.log("Response data:", data);

            if (data.success) {
                addMessage(data.response, 'agent');
            } else {
                const errorMsg = data.error || "Unknown error occurred";
                console.error('Agent error:', errorMsg);
                showError(errorMsg);
                addMessage("I'm sorry, I encountered an error processing your request: " + errorMsg, 'agent');
            }
        } catch (error) {
            console.error('Error communicating with agent:', error);
            showError(error.message);
            addMessage("I'm sorry, I encountered an error. Please try again later.", 'agent');
        } finally {
            loadingIndicator.style.display = 'none';
        }
    }

    // Event listener for send button
    sendMessageBtn.addEventListener('click', function () {
        const message = messageInput.value.trim();
        if (message) {
            addMessage(message, 'user');
            messageInput.value = '';
            sendToAgent(message);
        }
    });

    // Event listener for Enter key
    messageInput.addEventListener('keypress', function (e) {
        if (e.key === 'Enter') {
            const message = messageInput.value.trim();
            if (message) {
                addMessage(message, 'user');
                messageInput.value = '';
                sendToAgent(message);
            }
        }
    });

    // Reset chat
    resetChatBtn.addEventListener('click', function () {
        if (confirm('Are you sure you want to reset the chat? This will clear the current conversation.')) {
            // Clear UI
            messageContainer.innerHTML = '';
            // Hide any displayed error
            document.getElementById('errorMessage').style.display = 'none';
            // Add initial message
            addMessage('Hello! I\'m Claude, an AI assistant. How can I help you today?', 'agent');
            // Reset history and ID
            conversationHistory = [];
            conversationId = Date.now().toString();
        }
    });

    // Initialize with first message already in the history
    conversationHistory.push({
        sender: 'agent',
        message: 'Hello! I\'m Claude, an AI assistant. How can I help you today?',
        timestamp: new Date().toISOString()
    });
});
