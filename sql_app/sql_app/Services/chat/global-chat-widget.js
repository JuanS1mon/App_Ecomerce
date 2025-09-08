/**
 * Widget de Chat Global - Disponible en todas las páginas
 * Sistema de chat flotante que se puede usar desde cualquier pantalla
 */

class GlobalChatWidget {
    constructor(options = {}) {
        this.options = {
            position: 'bottom-right', // bottom-right, bottom-left, top-right, top-left
            wsUrl: 'ws://localhost:8000/chat/ws',
            defaultRoomId: 1,
            userId: null,
            userName: 'Usuario Anónimo',
            theme: 'light', // light, dark
            autoConnect: true,
            ...options
        };
        
        this.isOpen = false;
        this.isConnected = false;
        this.ws = null;
        this.messages = [];
        this.connectedUsers = [];
        this.isTyping = false;
        this.typingTimeout = null;
        this.typingUsers = new Set();
        
        this.init();
    }
    
    init() {
        console.log('💬 Inicializando GlobalChatWidget...');
        this.createWidget();
        this.setupEventListeners();
        
        if (this.options.autoConnect) {
            this.connect();
        }
    }
    
    createWidget() {
        // Crear contenedor principal
        this.widget = document.createElement('div');
        this.widget.id = 'global-chat-widget';
        this.widget.className = `chat-widget ${this.options.position} ${this.options.theme}`;
        
        this.widget.innerHTML = `
            <style>
                .chat-widget {
                    position: fixed;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    transition: all 0.3s ease;
                }
                
                .chat-widget.bottom-right {
                    bottom: 20px;
                    right: 20px;
                }
                
                .chat-widget.bottom-left {
                    bottom: 20px;
                    left: 20px;
                }
                
                .chat-widget.closed {
                    width: 60px;
                    height: 60px;
                }
                
                .chat-widget.open {
                    width: 350px;
                    height: 500px;
                    max-height: 80vh;
                }
                
                .chat-toggle {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border: none;
                    color: white;
                    font-size: 24px;
                    cursor: pointer;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: all 0.3s ease;
                    position: relative;
                }
                
                .chat-toggle:hover {
                    transform: translateY(-2px);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.4);
                }
                
                .chat-toggle .notification-badge {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    background: #ff4757;
                    color: white;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    font-size: 11px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                }
                
                .chat-window {
                    display: none;
                    background: white;
                    border-radius: 15px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                    overflow: hidden;
                    flex-direction: column;
                    height: 100%;
                }
                
                .chat-window.open {
                    display: flex;
                }
                
                .chat-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 15px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                }
                
                .chat-title {
                    font-weight: 600;
                    font-size: 16px;
                }
                
                .chat-status {
                    font-size: 12px;
                    opacity: 0.9;
                }
                
                .chat-close {
                    background: none;
                    border: none;
                    color: white;
                    font-size: 20px;
                    cursor: pointer;
                    padding: 5px;
                    border-radius: 5px;
                    transition: background 0.2s;
                }
                
                .chat-close:hover {
                    background: rgba(255,255,255,0.1);
                }
                
                .chat-messages {
                    flex: 1;
                    padding: 15px;
                    overflow-y: auto;
                    background: #f8f9fa;
                    max-height: 300px;
                }
                
                .message {
                    margin-bottom: 15px;
                    display: flex;
                    align-items: flex-start;
                }
                
                .message.own {
                    flex-direction: row-reverse;
                }
                
                .message-avatar {
                    width: 32px;
                    height: 32px;
                    border-radius: 50%;
                    background: #667eea;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    color: white;
                    font-weight: bold;
                    font-size: 12px;
                    margin: 0 8px;
                    flex-shrink: 0;
                }
                
                .message-content {
                    max-width: 70%;
                }
                
                .message-bubble {
                    background: white;
                    padding: 10px 15px;
                    border-radius: 15px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    word-wrap: break-word;
                }
                
                .message.own .message-bubble {
                    background: #667eea;
                    color: white;
                }
                
                .message-info {
                    font-size: 11px;
                    color: #666;
                    margin-top: 5px;
                    text-align: center;
                }
                
                .message.own .message-info {
                    text-align: right;
                }
                
                .system-message {
                    text-align: center;
                    color: #666;
                    font-style: italic;
                    font-size: 12px;
                    margin: 10px 0;
                }
                
                .typing-indicator {
                    display: none;
                    padding: 10px 20px;
                    color: #666;
                    font-style: italic;
                    font-size: 12px;
                }
                
                .typing-indicator.show {
                    display: block;
                }
                
                .chat-input-area {
                    padding: 15px;
                    background: white;
                    border-top: 1px solid #e9ecef;
                }
                
                .chat-input-container {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .chat-input {
                    flex: 1;
                    border: 1px solid #ddd;
                    border-radius: 20px;
                    padding: 10px 15px;
                    font-size: 14px;
                    outline: none;
                    transition: border-color 0.2s;
                }
                
                .chat-input:focus {
                    border-color: #667eea;
                }
                
                .chat-send {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    background: #667eea;
                    border: none;
                    color: white;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    transition: background 0.2s;
                }
                
                .chat-send:hover {
                    background: #5a6fd8;
                }
                
                .chat-send:disabled {
                    background: #ccc;
                    cursor: not-allowed;
                }
                
                .connection-status {
                    position: absolute;
                    top: 5px;
                    right: 5px;
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #28a745;
                }
                
                .connection-status.disconnected {
                    background: #dc3545;
                }
                
                .users-list {
                    padding: 10px 20px;
                    background: #f8f9fa;
                    border-top: 1px solid #e9ecef;
                    font-size: 12px;
                    color: #666;
                }
                
                .demo-controls {
                    padding: 10px 15px;
                    background: #e3f2fd;
                    border-top: 1px solid #bbdefb;
                    display: flex;
                    gap: 5px;
                    flex-wrap: wrap;
                }
                
                .demo-btn {
                    background: #2196f3;
                    color: white;
                    border: none;
                    padding: 5px 10px;
                    border-radius: 15px;
                    font-size: 11px;
                    cursor: pointer;
                    transition: background 0.2s;
                }
                
                .demo-btn:hover {
                    background: #1976d2;
                }
                
                @media (max-width: 480px) {
                    .chat-widget.open {
                        width: calc(100vw - 40px);
                        height: calc(100vh - 40px);
                        max-height: none;
                    }
                }
            </style>
            
            <!-- Botón toggle -->
            <button class="chat-toggle" onclick="globalChat.toggle()">
                <i class="fas fa-comments"></i>
                <span class="notification-badge" style="display: none;">0</span>
                <div class="connection-status disconnected"></div>
            </button>
            
            <!-- Ventana de chat -->
            <div class="chat-window">
                <div class="chat-header">
                    <div>
                        <div class="chat-title">Chat Global</div>
                        <div class="chat-status">Desconectado</div>
                    </div>
                    <button class="chat-close" onclick="globalChat.close()">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                
                <div class="chat-messages" id="chat-messages">
                    <div class="system-message">
                        🎉 ¡Bienvenido al chat global! Conéctate para empezar a chatear.
                    </div>
                </div>
                
                <div class="typing-indicator" id="typing-indicator">
                    <span id="typing-text"></span>
                </div>
                
                <div class="users-list" id="users-list">
                    <strong>Usuarios conectados:</strong> <span id="users-count">0</span>
                </div>
                
                <div class="chat-input-area">
                    <div class="chat-input-container">
                        <input type="text" 
                               class="chat-input" 
                               id="chat-input" 
                               placeholder="Escribe un mensaje..." 
                               disabled>
                        <button class="chat-send" 
                                id="chat-send" 
                                onclick="globalChat.sendMessage()" 
                                disabled>
                            <i class="fas fa-paper-plane"></i>
                        </button>
                    </div>
                </div>
                
                <!-- Controles de demo -->
                <div class="demo-controls">
                    <button class="demo-btn" onclick="globalChat.connect()">Conectar</button>
                    <button class="demo-btn" onclick="globalChat.disconnect()">Desconectar</button>
                    <button class="demo-btn" onclick="globalChat.sendDemoMessage()">Mensaje Demo</button>
                    <button class="demo-btn" onclick="globalChat.showStats()">Stats</button>
                </div>
            </div>
        `;
        
        document.body.appendChild(this.widget);
        
        // Referencias a elementos
        this.messagesContainer = document.getElementById('chat-messages');
        this.chatInput = document.getElementById('chat-input');
        this.chatSend = document.getElementById('chat-send');
        this.typingIndicator = document.getElementById('typing-indicator');
        this.usersCount = document.getElementById('users-count');
        this.connectionStatus = this.widget.querySelector('.connection-status');
        this.chatStatus = this.widget.querySelector('.chat-status');
        this.notificationBadge = this.widget.querySelector('.notification-badge');
    }
    
    setupEventListeners() {
        // Enter para enviar mensaje
        this.chatInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Detectar escritura
        this.chatInput.addEventListener('input', () => {
            this.handleTyping();
        });
        
        // Auto-scroll cuando se abren mensajes
        this.messagesContainer.addEventListener('DOMNodeInserted', () => {
            this.scrollToBottom();
        });
    }
    
    connect() {
        if (this.isConnected || !this.options.userId) {
            console.log('⚠️ Ya conectado o falta userId');
            return;
        }
        
        const wsUrl = `${this.options.wsUrl}/room/${this.options.defaultRoomId}?user_id=${this.options.userId}&user_name=${encodeURIComponent(this.options.userName)}`;
        
        console.log('🔌 Conectando a chat:', wsUrl);
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('✅ Chat conectado');
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.chatInput.disabled = false;
                this.chatSend.disabled = false;
                
                this.addSystemMessage('✅ Conectado al chat');
                
                // Solicitar usuarios conectados
                this.send({ type: 'get_room_users' });
            };
            
            this.ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                this.handleMessage(data);
            };
            
            this.ws.onclose = () => {
                console.log('🔌 Chat desconectado');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.chatInput.disabled = true;
                this.chatSend.disabled = true;
                
                this.addSystemMessage('❌ Desconectado del chat');
            };
            
            this.ws.onerror = (error) => {
                console.error('❌ Error en chat:', error);
                this.addSystemMessage('❌ Error de conexión');
            };
            
        } catch (error) {
            console.error('❌ Error conectando chat:', error);
            this.addSystemMessage('❌ Error al conectar');
        }
    }
    
    disconnect() {
        if (this.ws) {
            this.ws.close();
        }
    }
    
    send(data) {
        if (this.isConnected && this.ws) {
            this.ws.send(JSON.stringify(data));
        }
    }
    
    sendMessage() {
        const content = this.chatInput.value.trim();
        if (!content || !this.isConnected) return;
        
        this.send({
            type: 'send_message',
            data: { content }
        });
        
        this.chatInput.value = '';
        this.stopTyping();
    }
    
    handleMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.addMessage(data.data);
                if (data.data.user_id !== this.options.userId) {
                    this.showNotification();
                }
                break;
                
            case 'user_joined':
                this.addSystemMessage(`${data.data.user_name} se unió al chat`);
                break;
                
            case 'user_left':
                this.addSystemMessage(`${data.data.user_name} dejó el chat`);
                break;
                
            case 'typing_status':
                this.handleTypingStatus(data.data);
                break;
                
            case 'room_users':
                this.updateUsersList(data.data.users);
                break;
                
            case 'system_message':
                this.addSystemMessage(data.data.content);
                break;
        }
    }
    
    addMessage(messageData) {
        const isOwn = messageData.user_id === this.options.userId;
        const time = new Date(messageData.timestamp).toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        const messageEl = document.createElement('div');
        messageEl.className = `message ${isOwn ? 'own' : ''}`;
        messageEl.innerHTML = `
            <div class="message-avatar">
                ${messageData.user_name.charAt(0).toUpperCase()}
            </div>
            <div class="message-content">
                <div class="message-bubble">
                    ${this.escapeHtml(messageData.content)}
                </div>
                <div class="message-info">
                    ${messageData.user_name} • ${time}
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(messageEl);
        this.messages.push(messageData);
        this.scrollToBottom();
    }
    
    addSystemMessage(content) {
        const messageEl = document.createElement('div');
        messageEl.className = 'system-message';
        messageEl.textContent = content;
        
        this.messagesContainer.appendChild(messageEl);
        this.scrollToBottom();
    }
    
    handleTyping() {
        if (!this.isConnected) return;
        
        if (!this.isTyping) {
            this.isTyping = true;
            this.send({ type: 'typing_start' });
        }
        
        // Reset timeout
        clearTimeout(this.typingTimeout);
        this.typingTimeout = setTimeout(() => {
            this.stopTyping();
        }, 3000);
    }
    
    stopTyping() {
        if (this.isTyping) {
            this.isTyping = false;
            this.send({ type: 'typing_stop' });
        }
        clearTimeout(this.typingTimeout);
    }
    
    handleTypingStatus(data) {
        if (data.user_id === this.options.userId) return;
        
        if (data.is_typing) {
            this.typingUsers.add(data.user_id);
        } else {
            this.typingUsers.delete(data.user_id);
        }
        
        this.updateTypingIndicator();
    }
    
    updateTypingIndicator() {
        const typingText = document.getElementById('typing-text');
        
        if (this.typingUsers.size === 0) {
            this.typingIndicator.classList.remove('show');
        } else {
            const count = this.typingUsers.size;
            typingText.textContent = count === 1 
                ? 'Alguien está escribiendo...' 
                : `${count} personas están escribiendo...`;
            this.typingIndicator.classList.add('show');
        }
    }
    
    updateUsersList(users) {
        this.connectedUsers = users;
        this.usersCount.textContent = users.length;
    }
    
    updateConnectionStatus(connected) {
        this.connectionStatus.className = `connection-status ${connected ? '' : 'disconnected'}`;
        this.chatStatus.textContent = connected ? 'Conectado' : 'Desconectado';
    }
    
    showNotification() {
        if (!this.isOpen) {
            const badge = this.notificationBadge;
            const current = parseInt(badge.textContent) || 0;
            badge.textContent = current + 1;
            badge.style.display = 'flex';
        }
    }
    
    clearNotifications() {
        this.notificationBadge.style.display = 'none';
        this.notificationBadge.textContent = '0';
    }
    
    toggle() {
        if (this.isOpen) {
            this.close();
        } else {
            this.open();
        }
    }
    
    open() {
        this.isOpen = true;
        this.widget.classList.add('open');
        this.widget.classList.remove('closed');
        this.widget.querySelector('.chat-window').classList.add('open');
        this.clearNotifications();
        this.scrollToBottom();
        
        if (!this.isConnected && this.options.userId) {
            this.connect();
        }
    }
    
    close() {
        this.isOpen = false;
        this.widget.classList.remove('open');
        this.widget.classList.add('closed');
        this.widget.querySelector('.chat-window').classList.remove('open');
    }
    
    scrollToBottom() {
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 100);
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // Métodos de demo
    sendDemoMessage() {
        if (!this.isConnected) {
            this.addSystemMessage('⚠️ Conecta primero para enviar mensajes');
            return;
        }
        
        const demoMessages = [
            'Este es un mensaje de prueba 🚀',
            '¡El chat en tiempo real funciona perfectamente!',
            'Probando notificaciones y conexiones WebSocket',
            '¿Alguien más está viendo esto? 👀',
            'Sistema de chat implementado con éxito ✅'
        ];
        
        const randomMessage = demoMessages[Math.floor(Math.random() * demoMessages.length)];
        this.chatInput.value = randomMessage;
        this.sendMessage();
    }
    
    showStats() {
        if (this.isConnected) {
            this.send({ type: 'get_stats' });
        }
        
        const stats = `
            📊 Estadísticas del Chat:
            • Estado: ${this.isConnected ? '✅ Conectado' : '❌ Desconectado'}
            • Mensajes: ${this.messages.length}
            • Usuarios conectados: ${this.connectedUsers.length}
            • Sala actual: ${this.options.defaultRoomId}
            • Usuario: ${this.options.userName} (${this.options.userId})
        `;
        
        alert(stats);
    }
}

// Función para inicializar el chat global
function initGlobalChat(options = {}) {
    // Configuración por defecto
    const defaultOptions = {
        userId: 999, // Usuario demo
        userName: 'Usuario Demo',
        defaultRoomId: 1
    };
    
    // Intentar obtener datos del usuario actual si están disponibles
    if (window.currentUser) {
        defaultOptions.userId = window.currentUser.id;
        defaultOptions.userName = window.currentUser.name;
    }
    
    // Crear instancia global
    window.globalChat = new GlobalChatWidget({
        ...defaultOptions,
        ...options
    });
    
    console.log('💬 Chat global inicializado');
    return window.globalChat;
}

// Auto-inicializar si no está en modo manual
if (typeof window !== 'undefined' && !window.manualChatInit) {
    document.addEventListener('DOMContentLoaded', () => {
        initGlobalChat();
    });
}

// Exportar para uso manual
window.GlobalChatWidget = GlobalChatWidget;
window.initGlobalChat = initGlobalChat;
