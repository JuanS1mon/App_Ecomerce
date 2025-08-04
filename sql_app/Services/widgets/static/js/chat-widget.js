/**
 * Chat Widget - Widget de Chat en Tiempo Real
 * Componente modular para chat flotante con WebSockets
 */

class ChatWidget {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            wsUrl: '/chat/ws/room/',
            apiUrl: '/chat/api/',
            roomId: 1,
            userId: null,
            userName: 'Usuario',
            autoConnect: true,
            position: 'bottom-right',
            showUserList: true,
            maxMessages: 100,
            ...options
        };
        
        this.messages = [];
        this.connectedUsers = [];
        this.isOpen = false;
        this.isConnected = false;
        this.websocket = null;
        this.typingTimer = null;
        this.messageCount = 0;
        
        if (!this.container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }
        
        // Generar ID de usuario aleatorio si no se proporciona
        if (!this.options.userId) {
            this.options.userId = Math.floor(Math.random() * 10000);
        }
    }

    async init() {
        try {
            this.render();
            this.setupEventListeners();
            
            if (this.options.autoConnect) {
                await this.connect();
            }
            
            console.log('ChatWidget initialized successfully');
        } catch (error) {
            console.error('Error initializing ChatWidget:', error);
            this.renderError('Error al inicializar el widget de chat');
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="chat-widget">
                <button class="chat-widget-trigger" id="${this.containerId}-trigger">
                    <i class="fas fa-comments"></i>
                    <div class="chat-widget-badge" id="${this.containerId}-badge" style="display: none;">0</div>
                </button>
                
                <div class="chat-widget-panel" id="${this.containerId}-panel">
                    <div class="chat-widget-header">
                        <div>
                            <h3 class="chat-widget-title">
                                <i class="fas fa-comments"></i>
                                Chat
                            </h3>
                            <div class="chat-widget-status" id="${this.containerId}-status">
                                <span class="status-dot"></span>
                                Desconectado
                            </div>
                        </div>
                        <button class="chat-widget-close" id="${this.containerId}-close">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>
                    
                    ${this.options.showUserList ? `
                    <div class="chat-widget-user-list" id="${this.containerId}-users" style="display: none;">
                        <div class="chat-widget-user-item">
                            <span class="user-status-dot"></span>
                            <span>Conectando...</span>
                        </div>
                    </div>
                    ` : ''}
                    
                    <div class="chat-widget-messages" id="${this.containerId}-messages">
                        <div class="chat-widget-empty">
                            <i class="fas fa-comments"></i>
                            <p>¡Inicia una conversación!</p>
                        </div>
                    </div>
                    
                    <div class="chat-widget-typing" id="${this.containerId}-typing" style="display: none;">
                        <span class="typing-indicator">
                            <span class="typing-dot"></span>
                            <span class="typing-dot"></span>
                            <span class="typing-dot"></span>
                        </span>
                        <span>Alguien está escribiendo...</span>
                    </div>
                    
                    <div class="chat-widget-input-area">
                        <div class="chat-widget-input-container">
                            <textarea 
                                class="chat-widget-input" 
                                id="${this.containerId}-input"
                                placeholder="Escribe tu mensaje..."
                                rows="1"
                                disabled
                            ></textarea>
                            <button class="chat-widget-send" id="${this.containerId}-send" disabled>
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const trigger = document.getElementById(`${this.containerId}-trigger`);
        const panel = document.getElementById(`${this.containerId}-panel`);
        const closeBtn = document.getElementById(`${this.containerId}-close`);
        const input = document.getElementById(`${this.containerId}-input`);
        const sendBtn = document.getElementById(`${this.containerId}-send`);
        
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        closeBtn.addEventListener('click', () => {
            this.close();
        });
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!trigger.contains(e.target) && !panel.contains(e.target)) {
                this.close();
            }
        });
        
        // Enviar mensaje
        sendBtn.addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Enviar con Enter, nueva línea con Shift+Enter
        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Auto-resize textarea
        input.addEventListener('input', () => {
            this.autoResizeInput(input);
            this.onTyping();
        });
        
        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    autoResizeInput(input) {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }

    async loadMessages() {
        try {
            console.log('📚 Cargando historial de mensajes...');
            const response = await fetch(`/api/chat/room/${this.options.roomId}/messages`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.success && data.messages) {
                console.log(`📚 Cargados ${data.messages.length} mensajes del historial`);
                
                // Limpiar mensajes existentes
                this.messages = [];
                
                // Agregar mensajes del historial
                data.messages.forEach(msg => {
                    const message = {
                        id: msg.id,
                        user_id: msg.user_id,
                        user_name: msg.user_name,
                        content: msg.message,
                        timestamp: msg.timestamp,
                        type: 'message',
                        isOwn: msg.user_id === this.options.userId.toString()
                    };
                    this.messages.push(message);
                });
                
                this.renderMessages();
                console.log('✅ Historial cargado correctamente');
            }
        } catch (error) {
            console.error('❌ Error cargando mensajes:', error);
            this.addMessage({
                user_id: 'system',
                user_name: 'Sistema',
                content: 'Error cargando historial de mensajes',
                type: 'error'
            });
        }
    }

    async connect() {
        if (this.isConnected || this.websocket) {
            return;
        }
        
        this.updateStatus('Conectando...', false);
        
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}${this.options.wsUrl}${this.options.roomId}`;
            
            this.websocket = new WebSocket(`${wsUrl}?user_id=${this.options.userId}&user_name=${encodeURIComponent(this.options.userName)}`);
            
            this.websocket.onopen = async () => {
                this.isConnected = true;
                this.updateStatus('Conectado', true);
                this.enableInput(true);
                console.log('Chat WebSocket connected');
                
                // Cargar historial de mensajes cuando se conecte
                await this.loadMessages();
            };
            
            this.websocket.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };
            
            this.websocket.onclose = (event) => {
                this.isConnected = false;
                this.updateStatus('Desconectado', false);
                this.enableInput(false);
                console.log('Chat WebSocket closed:', event.code, event.reason);
                
                // Intentar reconectar después de 3 segundos
                setTimeout(() => {
                    if (!this.isConnected) {
                        this.connect();
                    }
                }, 3000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('Chat WebSocket error:', error);
                this.updateStatus('Error de conexión', false);
            };
            
        } catch (error) {
            console.error('Error connecting to chat:', error);
            this.updateStatus('Error', false);
        }
    }

    disconnect() {
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        this.isConnected = false;
        this.updateStatus('Desconectado', false);
        this.enableInput(false);
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'message':
                this.addMessage(data.data);
                break;
                
            case 'user_joined':
                this.onUserJoined(data.data);
                break;
                
            case 'user_left':
                this.onUserLeft(data.data);
                break;
                
            case 'room_users':
                this.updateUserList(data.data.users);
                break;
                
            case 'typing_start':
                this.showTyping(data.data);
                break;
                
            case 'typing_stop':
                this.hideTyping();
                break;
                
            case 'error':
                console.error('Chat error:', data.message);
                break;
                
            default:
                console.log('Unknown message type:', data.type);
        }
    }

    addMessage(messageData) {
        const message = {
            id: Date.now(),
            user_id: messageData.user_id,
            user_name: messageData.user_name,
            content: messageData.content,
            timestamp: messageData.timestamp || new Date().toISOString(),
            type: messageData.type || 'message',
            isOwn: messageData.user_id === this.options.userId
        };
        
        this.messages.push(message);
        
        // Limitar número de mensajes
        if (this.messages.length > this.options.maxMessages) {
            this.messages = this.messages.slice(-this.options.maxMessages);
        }
        
        this.renderMessages();
        
        // Actualizar badge si el chat está cerrado
        if (!this.isOpen && !message.isOwn) {
            this.messageCount++;
            this.updateBadge();
            
            // Efecto de notificación
            const trigger = document.getElementById(`${this.containerId}-trigger`);
            trigger.classList.add('has-messages');
        }
    }

    renderMessages() {
        const messagesContainer = document.getElementById(`${this.containerId}-messages`);
        
        if (this.messages.length === 0) {
            messagesContainer.innerHTML = `
                <div class="chat-widget-empty">
                    <i class="fas fa-comments"></i>
                    <p>¡Inicia una conversación!</p>
                </div>
            `;
            return;
        }
        
        const messagesHtml = this.messages.map(message => {
            if (message.type === 'system') {
                return `<div class="chat-system-message">${this.escapeHtml(message.content)}</div>`;
            }
            
            return `
                <div class="chat-message ${message.isOwn ? 'own' : 'other'}">
                    ${!message.isOwn ? `<div class="chat-message-header">${this.escapeHtml(message.user_name)}</div>` : ''}
                    <div class="chat-message-content">${this.escapeHtml(message.content)}</div>
                    <div class="chat-message-time">${this.formatTime(message.timestamp)}</div>
                </div>
            `;
        }).join('');
        
        messagesContainer.innerHTML = messagesHtml;
        
        // Scroll al final
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    async sendMessage() {
        const input = document.getElementById(`${this.containerId}-input`);
        const content = input.value.trim();
        
        if (!content) {
            return;
        }
        
        // Si está conectado, enviar por WebSocket como antes
        if (this.isConnected && this.websocket) {
            const message = {
                type: 'message',
                data: {
                    content: content,
                    user_id: this.options.userId,
                    user_name: this.options.userName,
                    timestamp: new Date().toISOString()
                }
            };
            
            this.websocket.send(JSON.stringify(message));
            input.value = '';
            input.style.height = 'auto';
            
            // Parar indicador de escritura
            this.stopTyping();
        } else {
            // Si está desconectado, enviar mensaje al admin por API
            await this.sendOfflineMessageToAdmin(content);
            input.value = '';
            input.style.height = 'auto';
        }
    }
    
    async sendOfflineMessageToAdmin(message) {
        try {
            console.log('📤 Enviando mensaje offline al admin:', message);
            
            // Mostrar mensaje en la interfaz inmediatamente
            this.addMessage({
                id: Date.now(),
                user_id: this.options.userId,
                user_name: this.options.userName,
                content: message,
                timestamp: new Date().toISOString(),
                type: 'user'
            });
            
            // Enviar por API REST
            const response = await fetch('/api/chat/send-to-admin', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    user_name: this.options.userName || 'Usuario Anónimo',
                    user_id: this.options.userId
                })
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('✅ Mensaje enviado al admin exitosamente:', result);
                
                // Mostrar confirmación
                this.addMessage({
                    id: Date.now() + 1,
                    user_id: 0,
                    user_name: 'Sistema',
                    content: '✅ Tu mensaje ha sido enviado al admin. Te contactaremos pronto.',
                    timestamp: new Date().toISOString(),
                    type: 'system'
                });
            } else {
                throw new Error('Error en la respuesta del servidor');
            }
            
        } catch (error) {
            console.error('❌ Error enviando mensaje offline:', error);
            
            // Mostrar error al usuario
            this.addMessage({
                id: Date.now() + 2,
                user_id: 0,
                user_name: 'Sistema',
                content: '❌ Error enviando mensaje. Por favor intenta de nuevo.',
                timestamp: new Date().toISOString(),
                type: 'system'
            });
        }
    }

    onTyping() {
        if (!this.isConnected) return;
        
        // Enviar indicador de escritura
        if (!this.typingTimer) {
            this.websocket.send(JSON.stringify({
                type: 'typing_start',
                data: {
                    user_id: this.options.userId,
                    user_name: this.options.userName
                }
            }));
        }
        
        // Reiniciar timer
        clearTimeout(this.typingTimer);
        this.typingTimer = setTimeout(() => {
            this.stopTyping();
        }, 2000);
    }

    stopTyping() {
        if (this.typingTimer) {
            clearTimeout(this.typingTimer);
            this.typingTimer = null;
            
            if (this.isConnected) {
                this.websocket.send(JSON.stringify({
                    type: 'typing_stop',
                    data: {
                        user_id: this.options.userId
                    }
                }));
            }
        }
    }

    showTyping(data) {
        if (data.user_id === this.options.userId) return;
        
        const typingDiv = document.getElementById(`${this.containerId}-typing`);
        typingDiv.style.display = 'block';
    }

    hideTyping() {
        const typingDiv = document.getElementById(`${this.containerId}-typing`);
        typingDiv.style.display = 'none';
    }

    onUserJoined(data) {
        this.addMessage({
            type: 'system',
            content: `${data.user_name} se unió al chat`,
            timestamp: data.timestamp
        });
    }

    onUserLeft(data) {
        this.addMessage({
            type: 'system',
            content: `${data.user_name} dejó el chat`,
            timestamp: data.timestamp
        });
    }

    updateUserList(users) {
        if (!this.options.showUserList) return;
        
        const usersList = document.getElementById(`${this.containerId}-users`);
        this.connectedUsers = users;
        
        if (users.length > 0) {
            const usersHtml = users.map(user => `
                <div class="chat-widget-user-item">
                    <span class="user-status-dot"></span>
                    <span>${this.escapeHtml(user.user_name)}</span>
                </div>
            `).join('');
            
            usersList.innerHTML = usersHtml;
            usersList.style.display = 'block';
        } else {
            usersList.style.display = 'none';
        }
    }

    updateStatus(status, connected) {
        const statusElement = document.getElementById(`${this.containerId}-status`);
        const statusDot = statusElement.querySelector('.status-dot');
        
        statusElement.lastChild.textContent = status;
        
        if (connected) {
            statusDot.style.background = '#34d399';
        } else {
            statusDot.style.background = '#ef4444';
        }
    }

    enableInput(enabled) {
        const input = document.getElementById(`${this.containerId}-input`);
        const sendBtn = document.getElementById(`${this.containerId}-send`);
        
        input.disabled = !enabled;
        sendBtn.disabled = !enabled;
        
        if (enabled) {
            input.placeholder = 'Escribe tu mensaje...';
        } else {
            input.placeholder = 'Conectando...';
        }
    }

    updateBadge() {
        const badge = document.getElementById(`${this.containerId}-badge`);
        if (this.messageCount > 0) {
            badge.textContent = this.messageCount > 99 ? '99+' : this.messageCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }

    clearBadge() {
        this.messageCount = 0;
        this.updateBadge();
        
        const trigger = document.getElementById(`${this.containerId}-trigger`);
        trigger.classList.remove('has-messages');
    }

    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }

    open() {
        const panel = document.getElementById(`${this.containerId}-panel`);
        panel.classList.add('show');
        this.isOpen = true;
        
        // Limpiar badge
        this.clearBadge();
        
        // Conectar si no está conectado
        if (!this.isConnected) {
            this.connect();
        }
        
        // Focus en input
        setTimeout(() => {
            const input = document.getElementById(`${this.containerId}-input`);
            if (input && !input.disabled) {
                input.focus();
            }
        }, 300);
    }

    close() {
        const panel = document.getElementById(`${this.containerId}-panel`);
        if (panel) {
            panel.classList.remove('show');
        }
        this.isOpen = false;
        
        // Parar indicador de escritura
        this.stopTyping();
    }

    formatTime(timestamp) {
        try {
            const date = new Date(timestamp);
            return date.toLocaleTimeString('es-ES', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
        } catch (error) {
            return '';
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    renderError(errorMessage) {
        const messagesContainer = document.getElementById(`${this.containerId}-messages`);
        messagesContainer.innerHTML = `
            <div class="chat-widget-error">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${errorMessage}</p>
            </div>
        `;
    }

    destroy() {
        this.stopTyping();
        this.disconnect();
        
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        console.log('ChatWidget destroyed');
    }
}

// Exportar para uso global
window.ChatWidget = ChatWidget;
