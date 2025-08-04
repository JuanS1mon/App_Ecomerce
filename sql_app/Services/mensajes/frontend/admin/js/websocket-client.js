/**
 * Cliente WebSocket para notificaciones en tiempo real
 * Sistema de mensajes - Notificaciones Push
 */

class NotificationWebSocket {
    constructor(options = {}) {
        this.url = options.url || `ws://localhost:8000/ws/notifications`;
        this.token = options.token || null;
        this.userId = options.userId || null;
        this.reconnectInterval = options.reconnectInterval || 5000;
        this.maxReconnectAttempts = options.maxReconnectAttempts || 10;
        this.pingInterval = options.pingInterval || 30000;
        
        this.ws = null;
        this.reconnectAttempts = 0;
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectTimer = null;
        this.pingTimer = null;
        this.eventListeners = new Map();
        
        // Callbacks
        this.onConnect = options.onConnect || (() => {});
        this.onDisconnect = options.onDisconnect || (() => {});
        this.onMessage = options.onMessage || (() => {});
        this.onError = options.onError || (() => {});
        
        console.log('🔔 NotificationWebSocket inicializado');
    }
    
    /**
     * Conectar al WebSocket
     */
    connect() {
        if (this.isConnecting || this.isConnected) {
            console.log('⚠️ Ya hay una conexión en progreso o activa');
            return;
        }
        
        this.isConnecting = true;
        
        // Construir URL con parámetros
        let wsUrl = this.url;
        const params = new URLSearchParams();
        
        if (this.token) {
            params.append('token', this.token);
        }
        
        if (this.userId) {
            params.append('user_id', this.userId);
        }
        
        if (params.toString()) {
            wsUrl += '?' + params.toString();
        }
        
        console.log('🔌 Conectando a WebSocket:', wsUrl);
        
        try {
            this.ws = new WebSocket(wsUrl);
            this.setupEventHandlers();
        } catch (error) {
            console.error('❌ Error creando WebSocket:', error);
            this.handleConnectionError(error);
        }
    }
    
    /**
     * Configurar event handlers del WebSocket
     */
    setupEventHandlers() {
        this.ws.onopen = (event) => {
            console.log('✅ WebSocket conectado');
            this.isConnected = true;
            this.isConnecting = false;
            this.reconnectAttempts = 0;
            
            // Iniciar ping
            this.startPing();
            
            // Callback de conexión
            this.onConnect(event);
            this.emit('connect', event);
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 Mensaje recibido:', data);
                
                // Manejar tipos especiales de mensaje
                this.handleSpecialMessages(data);
                
                // Callback general
                this.onMessage(data);
                this.emit('message', data);
                
                // Emitir evento específico por tipo
                if (data.type) {
                    this.emit(data.type, data);
                }
                
            } catch (error) {
                console.error('❌ Error parseando mensaje:', error);
            }
        };
        
        this.ws.onclose = (event) => {
            console.log('🔌 WebSocket desconectado:', event.code, event.reason);
            this.isConnected = false;
            this.isConnecting = false;
            
            // Limpiar ping
            this.stopPing();
            
            // Callback de desconexión
            this.onDisconnect(event);
            this.emit('disconnect', event);
            
            // Intentar reconectar si no fue cierre manual
            if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
                this.scheduleReconnect();
            }
        };
        
        this.ws.onerror = (event) => {
            console.error('❌ Error en WebSocket:', event);
            this.onError(event);
            this.emit('error', event);
            this.handleConnectionError(event);
        };
    }
    
    /**
     * Manejar mensajes especiales del sistema
     */
    handleSpecialMessages(data) {
        switch (data.type) {
            case 'ping':
                // Responder al ping
                this.send({ type: 'pong', timestamp: data.timestamp });
                break;
                
            case 'pong':
                // Ping confirmado
                console.log('🏓 Pong recibido');
                break;
                
            case 'connection_established':
                console.log('🎉 Conexión establecida:', data);
                break;
                
            case 'connection_stats':
                console.log('📊 Estadísticas de conexión:', data.data);
                break;
                
            case 'new_message':
                this.handleNewMessage(data.data);
                break;
                
            case 'urgent_message':
                this.handleUrgentMessage(data.data);
                break;
                
            case 'system_notification':
                this.handleSystemNotification(data.data);
                break;
        }
    }
    
    /**
     * Manejar nuevo mensaje
     */
    handleNewMessage(messageData) {
        console.log('📩 Nuevo mensaje:', messageData);
        
        // Mostrar notificación del navegador si está permitido
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification(messageData.title, {
                body: messageData.content,
                icon: '/static/images/message-icon.png',
                tag: `message-${messageData.id}`
            });
        }
        
        // Actualizar UI
        this.updateMessageCounter();
        this.showInAppNotification(messageData, 'new_message');
    }
    
    /**
     * Manejar mensaje urgente
     */
    handleUrgentMessage(messageData) {
        console.log('🚨 Mensaje urgente:', messageData);
        
        // Notificación más prominente para mensajes urgentes
        if ('Notification' in window && Notification.permission === 'granted') {
            new Notification('🚨 MENSAJE URGENTE', {
                body: messageData.title,
                icon: '/static/images/urgent-icon.png',
                tag: `urgent-${messageData.id}`,
                requireInteraction: true
            });
        }
        
        // Mostrar alerta modal
        this.showUrgentAlert(messageData);
    }
    
    /**
     * Manejar notificación del sistema
     */
    handleSystemNotification(notificationData) {
        console.log('🔔 Notificación del sistema:', notificationData);
        this.showInAppNotification(notificationData, 'system');
    }
    
    /**
     * Mostrar notificación en la aplicación
     */
    showInAppNotification(data, type) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `fixed top-4 right-4 z-50 p-4 rounded-lg shadow-lg slide-in max-w-sm ${
            type === 'urgent_message' ? 'bg-red-500 text-white' :
            type === 'system' ? 'bg-blue-500 text-white' :
            'bg-green-500 text-white'
        }`;
        
        notification.innerHTML = `
            <div class="flex items-start justify-between">
                <div class="flex-1">
                    <h4 class="font-semibold mb-1">${data.title || 'Notificación'}</h4>
                    <p class="text-sm opacity-90">${data.content || data.body || ''}</p>
                </div>
                <button onclick="this.parentElement.parentElement.remove()" 
                        class="ml-2 text-white hover:text-gray-200">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        document.body.appendChild(notification);
        
        // Auto-remover después de 5 segundos (10 para urgentes)
        const timeout = type === 'urgent_message' ? 10000 : 5000;
        setTimeout(() => {
            if (notification.parentElement) {
                notification.remove();
            }
        }, timeout);
    }
    
    /**
     * Mostrar alerta urgente modal
     */
    showUrgentAlert(messageData) {
        // Solo si no hay una alerta urgente ya mostrada
        if (document.getElementById('urgent-alert-modal')) {
            return;
        }
        
        const modal = document.createElement('div');
        modal.id = 'urgent-alert-modal';
        modal.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        modal.innerHTML = `
            <div class="bg-white rounded-lg p-6 max-w-md mx-4 border-l-4 border-red-500">
                <div class="flex items-center mb-4">
                    <i class="fas fa-exclamation-triangle text-red-500 text-2xl mr-3"></i>
                    <h3 class="text-lg font-semibold text-gray-900">Mensaje Urgente</h3>
                </div>
                <h4 class="font-medium text-gray-900 mb-2">${messageData.title}</h4>
                <p class="text-gray-700 mb-4">${messageData.content}</p>
                <div class="flex justify-end space-x-3">
                    <button onclick="document.getElementById('urgent-alert-modal').remove()" 
                            class="px-4 py-2 bg-gray-500 hover:bg-gray-600 text-white rounded">
                        Cerrar
                    </button>
                    <button onclick="window.location.href='/administracion/mensajes'; document.getElementById('urgent-alert-modal').remove()" 
                            class="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded">
                        Ver Mensaje
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
    }
    
    /**
     * Actualizar contador de mensajes
     */
    updateMessageCounter() {
        // Buscar elementos de contador en la UI
        const counters = document.querySelectorAll('.message-counter, #message-count, .unread-count');
        counters.forEach(counter => {
            const current = parseInt(counter.textContent) || 0;
            counter.textContent = current + 1;
            
            // Añadir efecto visual
            counter.classList.add('animate-pulse');
            setTimeout(() => counter.classList.remove('animate-pulse'), 1000);
        });
        
        // Actualizar favicon si existe
        this.updateFavicon();
    }
    
    /**
     * Actualizar favicon con indicador
     */
    updateFavicon() {
        // TODO: Implementar actualización de favicon con contador
        console.log('📌 Actualizando favicon...');
    }
    
    /**
     * Enviar mensaje al servidor
     */
    send(data) {
        if (this.isConnected && this.ws) {
            try {
                this.ws.send(JSON.stringify(data));
                console.log('📤 Mensaje enviado:', data);
            } catch (error) {
                console.error('❌ Error enviando mensaje:', error);
            }
        } else {
            console.warn('⚠️ No hay conexión WebSocket activa');
        }
    }
    
    /**
     * Iniciar ping periódico
     */
    startPing() {
        this.pingTimer = setInterval(() => {
            if (this.isConnected) {
                this.send({
                    type: 'ping',
                    timestamp: new Date().toISOString()
                });
            }
        }, this.pingInterval);
    }
    
    /**
     * Detener ping
     */
    stopPing() {
        if (this.pingTimer) {
            clearInterval(this.pingTimer);
            this.pingTimer = null;
        }
    }
    
    /**
     * Programar reconexión
     */
    scheduleReconnect() {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
        }
        
        this.reconnectAttempts++;
        const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
        
        console.log(`🔄 Reconectando en ${delay}ms (intento ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
        
        this.reconnectTimer = setTimeout(() => {
            this.connect();
        }, delay);
    }
    
    /**
     * Manejar errores de conexión
     */
    handleConnectionError(error) {
        this.isConnecting = false;
        this.isConnected = false;
    }
    
    /**
     * Desconectar manualmente
     */
    disconnect() {
        console.log('🔌 Desconectando WebSocket...');
        
        this.stopPing();
        
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        
        if (this.ws) {
            this.ws.close(1000, 'Desconexión manual');
        }
        
        this.isConnected = false;
        this.isConnecting = false;
        this.reconnectAttempts = 0;
    }
    
    /**
     * Solicitar estadísticas de conexión
     */
    requestStats() {
        this.send({ type: 'get_stats' });
    }
    
    /**
     * Solicitar notificaciones pendientes
     */
    requestNotifications() {
        this.send({ type: 'request_notifications' });
    }
    
    /**
     * Registrar listener para eventos
     */
    on(event, callback) {
        if (!this.eventListeners.has(event)) {
            this.eventListeners.set(event, []);
        }
        this.eventListeners.get(event).push(callback);
    }
    
    /**
     * Eliminar listener
     */
    off(event, callback) {
        if (this.eventListeners.has(event)) {
            const listeners = this.eventListeners.get(event);
            const index = listeners.indexOf(callback);
            if (index > -1) {
                listeners.splice(index, 1);
            }
        }
    }
    
    /**
     * Emitir evento
     */
    emit(event, data) {
        if (this.eventListeners.has(event)) {
            this.eventListeners.get(event).forEach(callback => {
                try {
                    callback(data);
                } catch (error) {
                    console.error(`❌ Error en listener para evento ${event}:`, error);
                }
            });
        }
    }
    
    /**
     * Obtener estado de la conexión
     */
    getStatus() {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            reconnectAttempts: this.reconnectAttempts,
            url: this.url,
            userId: this.userId
        };
    }
}

// Función para solicitar permisos de notificación
async function requestNotificationPermission() {
    if ('Notification' in window) {
        if (Notification.permission === 'default') {
            const permission = await Notification.requestPermission();
            console.log('🔔 Permisos de notificación:', permission);
            return permission === 'granted';
        }
        return Notification.permission === 'granted';
    }
    return false;
}

// Exportar para uso global
window.NotificationWebSocket = NotificationWebSocket;
window.requestNotificationPermission = requestNotificationPermission;
