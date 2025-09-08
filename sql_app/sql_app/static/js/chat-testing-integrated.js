/**
 * Chat Testing JavaScript - Integrado en servidor principal
 * Sistema de chat completo para entorno de prueba en el servidor principal
 */

class ChatTestingIntegrated {
    constructor() {
        this.ws = null;
        this.currentRoom = { id: 1, name: "Chat Admin ↔ Juan" }; // Conversación fija
        this.currentUser = { id: 'juan', name: 'Juan Usuario' };
        this.isConnected = false;
        this.messages = [];
        this.salas = [];
        this.widgetVisible = false;
        this.widgetMinimized = false;
        this.messagesSent = 0;
        
        this.init();
    }

    init() {
        console.log('🚀 Inicializando Chat Directo Admin ↔ Juan...');
        this.setupEventListeners();
        this.loadInitialData();
        this.updateUI();
        this.log('Chat directo entre usuarios iniciado');
        
        // Auto-conectar después de cargar los datos
        setTimeout(() => {
            this.autoConnect();
        }, 1000);
    }

    setupEventListeners() {
        // Botones principales
        document.getElementById('connect-btn').addEventListener('click', () => this.connect());
        document.getElementById('disconnect-btn').addEventListener('click', () => this.disconnect());
        document.getElementById('send-btn').addEventListener('click', () => this.sendMessage());
        document.getElementById('toggle-widget-btn').addEventListener('click', () => this.toggleWidget());

        // Selectores
        document.getElementById('user-select').addEventListener('change', (e) => this.changeUser(e.target.value));
        document.getElementById('room-select').addEventListener('change', (e) => this.changeRoom(e.target.value));

        // Input de mensaje principal
        document.getElementById('message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendMessage();
        });

        // Widget controls
        document.getElementById('fab-button').addEventListener('click', () => this.showWidget());
        document.getElementById('minimize-widget').addEventListener('click', () => this.minimizeWidget());
        document.getElementById('widget-send-btn').addEventListener('click', () => this.sendWidgetMessage());
        
        // Widget input
        document.getElementById('widget-message-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.sendWidgetMessage();
        });

        console.log('Event listeners configurados');
    }

    async loadInitialData() {
        console.log('Cargando datos iniciales...');
        await this.loadSalas();
        await this.loadStats();
        this.log('Datos iniciales cargados');
    }

    async loadSalas() {
        try {
            const response = await fetch('/chat-testing/api/salas');
            const data = await response.json();
            
            if (data.success) {
                this.salas = data.data;
                this.updateRoomSelect();
                this.log(`${this.salas.length} salas cargadas`);
            } else {
                this.log('Error cargando salas', 'error');
            }
        } catch (error) {
            console.error('Error loading salas:', error);
            this.log('Error de conexión al cargar salas', 'error');
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/chat-testing/api/stats');
            const data = await response.json();
            
            if (data.success) {
                this.updateStats(data.data);
            }
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    updateRoomSelect() {
        const select = document.getElementById('room-select');
        select.innerHTML = '<option value="1">Chat Admin ↔ Juan</option>';
        select.value = "1";
        select.disabled = true; // Deshabilitar porque solo hay una conversación
    }

    updateStats(stats) {
        document.getElementById('total-rooms').textContent = stats.total_rooms || 0;
        document.getElementById('messages-sent').textContent = this.messagesSent;
        document.getElementById('active-connections').textContent = stats.active_connections || 0;
    }

    changeUser(userId) {
        const userNames = {
            'juan': 'Juan Usuario',
            'admin': 'Admin Usuario'
        };
        
        this.currentUser = {
            id: userId,
            name: userNames[userId] || userId
        };
        
        this.log(`Usuario cambiado a: ${this.currentUser.name}`);
        
        // Si está conectado, reconectar con nuevo usuario
        if (this.isConnected) {
            this.disconnect();
            setTimeout(() => this.connect(), 500);
        }
    }

    changeRoom(roomId) {
        // En chat directo, siempre es la misma conversación
        this.currentRoom = { id: 1, name: "Chat Admin ↔ Juan" };
        this.log(`Conversación: ${this.currentRoom.name}`);
    }

    autoConnect() {
        // Conexión automática para chat directo
        if (!this.isConnected) {
            this.log('Conectando automáticamente...');
            this.connect();
        }
    }

    async connect() {
        if (this.isConnected) {
            this.showNotification('Ya estás conectado', 'info');
            return;
        }
        
        // Chat directo siempre usa room ID 1
        const wsUrl = `ws://localhost:8000/chat-testing/ws/1?user_id=${this.currentUser.id}&user_name=${encodeURIComponent(this.currentUser.name)}`;
        
        this.log(`Conectando a chat directo: ${wsUrl}`);
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus(true);
            this.enableInputs(true);
            this.log(`Conectado a chat directo como ${this.currentUser.name}`);
            this.showNotification(`Conectado como ${this.currentUser.name}`, 'success');
            this.loadRoomMessages();
        };
        
        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
        
        this.ws.onclose = () => {
            this.isConnected = false;
            this.updateConnectionStatus(false);
            this.enableInputs(false);
            this.log('Conexión WebSocket cerrada');
            this.showNotification('Desconectado del chat', 'info');
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.log('Error en conexión WebSocket', 'error');
            this.showNotification('Error de conexión', 'error');
        };
    }

    disconnect() {
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.isConnected = false;
        this.updateConnectionStatus(false);
        this.enableInputs(false);
        this.log('Desconectado manualmente');
    }

    async loadRoomMessages() {
        // Chat directo siempre usa room ID 1
        try {
            const response = await fetch(`/chat-testing/api/rooms/1/messages`);
            const data = await response.json();
            
            if (data.success) {
                this.messages = data.data;
                this.renderMessages();
                this.log(`${this.messages.length} mensajes cargados del chat directo`);
            }
        } catch (error) {
            console.error('Error loading room messages:', error);
            this.log('Error cargando mensajes', 'error');
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message received:', data);
        
        switch (data.type) {
            case 'message':
                // Marcar si es mensaje propio
                data.is_own = data.user_id === this.currentUser.id;
                this.messages.push(data);
                this.renderMessages();
                this.log(`Mensaje de ${data.user_name}: ${data.message}`);
                console.log('✅ Mensaje procesado y añadido a la lista');
                break;
                
            case 'user_joined':
                this.log(`${data.user_id} se unió al chat`, 'info');
                this.showNotification(`${data.user_id} se unió`, 'info');
                break;
                
            case 'user_left':
                this.log(`${data.user_id} se desconectó`, 'info');
                this.showNotification(`${data.user_id} se desconectó`, 'info');
                break;
                
            case 'error':
                this.log(`Error: ${data.message}`, 'error');
                this.showNotification(data.message, 'error');
                console.error('❌ Error recibido del servidor:', data);
                break;
                
            default:
                console.log('❓ Tipo de mensaje desconocido:', data);
                break;
        }
    }

    sendMessage() {
        const input = document.getElementById('message-input');
        const message = input.value.trim();
        
        if (!message || !this.isConnected) return;
        
        this.sendWebSocketMessage(message);
        input.value = '';
    }

    sendWidgetMessage() {
        const input = document.getElementById('widget-message-input');
        const message = input.value.trim();
        
        if (!message || !this.isConnected) return;
        
        this.sendWebSocketMessage(message);
        input.value = '';
    }

    sendWebSocketMessage(message) {
        if (!this.ws || !this.isConnected) {
            this.showNotification('No hay conexión activa', 'error');
            this.log('Error: No hay conexión WebSocket activa', 'error');
            return;
        }
        
        if (this.ws.readyState !== WebSocket.OPEN) {
            this.showNotification('Conexión no disponible', 'error');
            this.log('Error: WebSocket no está en estado OPEN', 'error');
            return;
        }
        
        const messageData = {
            message: message,
            timestamp: new Date().toISOString()
        };
        
        try {
            this.ws.send(JSON.stringify(messageData));
            this.messagesSent++;
            this.updateStats({ messages_sent: this.messagesSent });
            this.log(`Mensaje enviado: ${message}`);
            console.log('📤 Mensaje enviado al WebSocket:', messageData);
        } catch (error) {
            console.error('❌ Error enviando mensaje:', error);
            this.log(`Error: Error al enviar mensaje`, 'error');
            this.showNotification('Error al enviar mensaje', 'error');
        }
    }

    renderMessages() {
        const container = document.getElementById('messages-container');
        const widgetContainer = document.getElementById('widget-messages');
        
        if (this.messages.length === 0) {
            container.innerHTML = `
                <div class="text-center text-gray-500 text-sm">
                    <i class="fas fa-comment-dots text-3xl mb-2"></i>
                    <p>No hay mensajes en esta sala</p>
                </div>
            `;
            widgetContainer.innerHTML = `
                <div class="text-center text-gray-500 text-xs">
                    <i class="fas fa-comment text-lg mb-1"></i>
                    <p>Sin mensajes</p>
                </div>
            `;
            return;
        }
        
        const messagesHtml = this.messages.map(msg => this.createMessageHtml(msg, false)).join('');
        const widgetHtml = this.messages.slice(-5).map(msg => this.createMessageHtml(msg, true)).join('');
        
        container.innerHTML = messagesHtml;
        widgetContainer.innerHTML = widgetHtml;
        
        // Scroll al final
        container.scrollTop = container.scrollHeight;
        widgetContainer.scrollTop = widgetContainer.scrollHeight;
    }

    createMessageHtml(msg, isWidget = false) {
        const isOwn = msg.user_id === this.currentUser.id;
        const timeStr = new Date(msg.timestamp || msg.created_at).toLocaleTimeString();
        const containerClass = isWidget ? 'mb-2' : 'mb-3';
        const messageClass = isWidget ? 'text-xs' : 'text-sm';
        
        if (isOwn) {
            return `
                <div class="${containerClass} flex justify-end">
                    <div class="message-bubble bg-blue-500 text-white p-2 rounded-lg ${messageClass}">
                        <div class="font-medium">Tú</div>
                        <div>${this.escapeHtml(msg.message)}</div>
                        <div class="text-xs opacity-75 mt-1">${timeStr}</div>
                    </div>
                </div>
            `;
        } else {
            return `
                <div class="${containerClass} flex justify-start">
                    <div class="message-bubble bg-gray-200 text-gray-800 p-2 rounded-lg ${messageClass}">
                        <div class="font-medium text-blue-600">${this.escapeHtml(msg.user_name)}</div>
                        <div>${this.escapeHtml(msg.message)}</div>
                        <div class="text-xs opacity-75 mt-1">${timeStr}</div>
                    </div>
                </div>
            `;
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    updateConnectionStatus(connected) {
        const status = document.getElementById('connection-status');
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        const roomInfo = document.getElementById('chat-room-info');
        
        if (connected) {
            status.textContent = 'Conectado';
            status.className = 'px-2 py-1 rounded-full text-xs bg-green-100 text-green-800';
            connectBtn.disabled = true;
            disconnectBtn.disabled = false;
            roomInfo.textContent = `Chat directo: ${this.currentUser.name} ↔ ${this.currentUser.id === 'admin' ? 'Juan' : 'Admin'}`;
        } else {
            status.textContent = 'Desconectado';
            status.className = 'px-2 py-1 rounded-full text-xs bg-red-100 text-red-800';
            connectBtn.disabled = false;
            disconnectBtn.disabled = true;
            roomInfo.textContent = `Listo para chat directo como ${this.currentUser.name}`;
        }
    }

    enableInputs(enabled) {
        document.getElementById('message-input').disabled = !enabled;
        document.getElementById('send-btn').disabled = !enabled;
        document.getElementById('widget-message-input').disabled = !enabled;
        document.getElementById('widget-send-btn').disabled = !enabled;
    }

    toggleWidget() {
        this.widgetVisible = !this.widgetVisible;
        const widget = document.getElementById('chat-widget');
        const fab = document.getElementById('fab-button');
        
        if (this.widgetVisible) {
            widget.style.display = 'block';
            fab.style.display = 'none';
            this.log('Widget mostrado');
        } else {
            widget.style.display = 'none';
            fab.style.display = 'block';
            this.log('Widget ocultado');
        }
    }

    showWidget() {
        this.widgetVisible = true;
        document.getElementById('chat-widget').style.display = 'block';
        document.getElementById('fab-button').style.display = 'none';
        this.log('Widget activado');
    }

    minimizeWidget() {
        const widget = document.getElementById('chat-widget');
        const content = document.getElementById('widget-content');
        
        this.widgetMinimized = !this.widgetMinimized;
        
        if (this.widgetMinimized) {
            content.style.display = 'none';
            widget.classList.add('widget-minimized');
            this.log('Widget minimizado');
        } else {
            content.style.display = 'flex';
            widget.classList.remove('widget-minimized');
            this.log('Widget expandido');
        }
    }

    updateUI() {
        this.updateConnectionStatus(false);
        this.enableInputs(false);
        
        // Actualizar info del usuario actual
        const userSelect = document.getElementById('user-select');
        userSelect.value = this.currentUser.id;
    }

    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        const logContainer = document.getElementById('activity-log');
        
        const colorClass = {
            'info': 'text-blue-600',
            'success': 'text-green-600',
            'warning': 'text-yellow-600',
            'error': 'text-red-600'
        }[type] || 'text-gray-600';
        
        const logEntry = document.createElement('div');
        logEntry.className = `${colorClass} text-xs`;
        logEntry.innerHTML = `<span class="text-gray-400">${timestamp}</span> ${message}`;
        
        logContainer.appendChild(logEntry);
        logContainer.scrollTop = logContainer.scrollHeight;
        
        console.log(`[${timestamp}] ${message}`);
    }

    showNotification(message, type = 'info') {
        // Crear notificación temporal
        const notification = document.createElement('div');
        const bgColor = {
            'success': 'bg-green-500',
            'error': 'bg-red-500',
            'warning': 'bg-yellow-500',
            'info': 'bg-blue-500'
        }[type] || 'bg-blue-500';
        
        notification.className = `fixed top-4 right-4 ${bgColor} text-white px-4 py-2 rounded-lg shadow-lg z-50 transition-all`;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remover después de 3 segundos
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chatApp = new ChatTestingIntegrated();
});

// Manejar reconexión automática
window.addEventListener('beforeunload', () => {
    if (window.chatApp && window.chatApp.ws) {
        window.chatApp.ws.close();
    }
});
