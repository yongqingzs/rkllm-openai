/**
 * API Communication Layer
 * Handles communication with RKLLM API backend
 */

class RKLLMClient {
    constructor(config) {
        this.baseUrl = config.api_base_url;
        this.apiKey = config.api_key;
        this.model = config.model;
        this.maxContextLength = config.max_context_length;
    }

    /**
     * Send chat message with optional image
     * @param {string} message - The user message
     * @param {string|null} imageUrl - Base64 image data or HTTP(S) URL
     * @param {Function} onChunk - Callback for streaming chunks
     */
    async sendMessage(message, imageUrl = null, onChunk = null) {
        const messageContent = [{ type: 'text', text: message }];

        if (imageUrl) {
            messageContent.push({
                type: 'image_url',
                image_url: { url: imageUrl }
            });
        }

        const requestBody = {
            model: this.model,
            messages: [
                {
                    role: 'user',
                    content: messageContent
                }
            ],
            stream: true
        };

        console.log('Sending request to:', `${this.baseUrl}/chat/completions`);
        console.log('Request body:', requestBody);

        try {
            const response = await fetch(`${this.baseUrl}/chat/completions`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.apiKey}`
                },
                body: JSON.stringify(requestBody)
            });

            console.log('Response status:', response.status, response.statusText);

            if (!response.ok) {
                const errorText = await response.text();
                console.error('API response error:', errorText);
                throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorText.substring(0, 200)}`);
            }

            // Handle streaming response
            if (onChunk) {
                await this._handleStream(response, onChunk);
            } else {
                const data = await response.json();
                return data.choices[0].message.content;
            }
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    /**
     * Handle streaming response
     */
    async _handleStream(response, onChunk) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');

                // Process all complete lines
                for (let i = 0; i < lines.length - 1; i++) {
                    const line = lines[i].trim();
                    if (line.startsWith('data: ')) {
                        const data = line.slice(6);
                        if (data === '[DONE]') continue;

                        try {
                            const json = JSON.parse(data);
                            const chunk = json.choices?.[0]?.delta?.content;
                            if (chunk) {
                                onChunk(chunk);
                            }
                        } catch (e) {
                            // Invalid JSON, skip
                        }
                    }
                }

                // Keep the last incomplete line in buffer
                buffer = lines[lines.length - 1];
            }

            // Process final buffer
            if (buffer.trim()) {
                const line = buffer.trim();
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data !== '[DONE]') {
                        try {
                            const json = JSON.parse(data);
                            const chunk = json.choices?.[0]?.delta?.content;
                            if (chunk) {
                                onChunk(chunk);
                            }
                        } catch (e) {
                            // Invalid JSON, skip
                        }
                    }
                }
            }
        } finally {
            reader.releaseLock();
        }
    }
}

// Export for use in main.js
window.RKLLMClient = RKLLMClient;
