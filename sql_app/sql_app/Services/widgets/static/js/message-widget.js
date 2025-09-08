/**
 * Message Widget - Widget de Mensajes en Tiempo Real
 * Componente modular para mostrar notificaciones y mensajes
 */

class MessageWidget {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            apiUrl: '/api/mensajes/',
            wsUrl: '/ws/notifications',
            autoRefresh: true,
            refreshInterval: 30000,
            maxMessages: 10,
            showTypes: ['sistema', 'alerta', 'info'],
            position: 'top-right',
            ...options
        };
        
        this.messages = [];
        this.unreadCount = 0;
        this.isOpen = false;
        this.websocket = null;
        this.refreshTimer = null;
        
        if (!this.container) {
            throw new Error(`Container with ID '${containerId}' not found`);
        }
    }

    async init() {
        try {
            this.render();
            await this.loadMessages();
            this.setupWebSocket();
            this.setupEventListeners();
            
            if (this.options.autoRefresh) {
                this.startAutoRefresh();
            }
            
            console.log('MessageWidget initialized successfully');
        } catch (error) {
            console.error('Error initializing MessageWidget:', error);
            this.renderError('Error al inicializar el widget de mensajes');
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="message-widget">
                <button class="message-widget-trigger" id="${this.containerId}-trigger">
                    <i class="fas fa-bell"></i>
                    <span>Mensajes</span>
                    <div class="message-widget-badge" id="${this.containerId}-badge" style="display: none;">0</div>
                </button>
                
                <div class="message-widget-panel" id="${this.containerId}-panel">
                    <div class="message-widget-header">
                        <h3 class="message-widget-title">
                            <i class="fas fa-envelope"></i>
                            Mensajes Recientes
                        </h3>
                    </div>
                    
                    <div class="message-widget-content" id="${this.containerId}-content">
                        <div class="message-widget-loading">
                            <i class="fas fa-spinner"></i>
                            <p>Cargando mensajes...</p>
                        </div>
                    </div>
                    
                    <div class="message-widget-footer">
                        <a href="/admin/mensajes" class="message-widget-link">
                            <span>Ver todos los mensajes</span>
                            <i class="fas fa-arrow-right"></i>
                        </a>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventListeners() {
        const trigger = document.getElementById(`${this.containerId}-trigger`);
        const panel = document.getElementById(`${this.containerId}-panel`);
        
        trigger.addEventListener('click', (e) => {
            e.stopPropagation();
            this.toggle();
        });
        
        // Cerrar al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!trigger.contains(e.target) && !panel.contains(e.target)) {
                this.close();
            }
        });
        
        // Cerrar con Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.close();
            }
        });
    }

    async loadMessages() {
        try {
            // Cargar contador de no leídos
            const countResponse = await fetch(`${this.options.apiUrl}no-leidos/count`);
            if (countResponse.ok) {
                const countData = await countResponse.json();
                this.unreadCount = countData.count || 0;
                this.updateBadge();
            }
            
            // Cargar mensajes para navbar
            const messagesResponse = await fetch(`${this.options.apiUrl}navbar`);
            if (messagesResponse.ok) {
                this.messages = await messagesResponse.json();
                this.renderMessages();
            } else {
                throw new Error(`Error ${messagesResponse.status}: ${messagesResponse.statusText}`);
            }
        } catch (error) {
            console.error('Error loading messages:', error);
            this.renderError('Error al cargar los mensajes');
        }
    }

    renderMessages() {
        const content = document.getElementById(`${this.containerId}-content`);
        
        if (!this.messages || this.messages.length === 0) {
            content.innerHTML = `
                <div class="message-widget-empty">
                    <i class="fas fa-inbox"></i>
                    <p>No hay mensajes nuevos</p>
                </div>
            `;
            return;
        }
        
        const messagesHtml = this.messages
            .slice(0, this.options.maxMessages)
            .map(message => this.renderMessageItem(message))
            .join('');
        
        content.innerHTML = messagesHtml;
        
        // Agregar event listeners para los mensajes
        content.querySelectorAll('.message-item').forEach((item, index) => {
            item.addEventListener('click', () => {
                this.onMessageClick(this.messages[index]);
            });
        });
    }

    renderMessageItem(message) {
        const isUnread = !message.leido;
        const fecha = this.formatDate(message.fecha_creacion);
        
        return `
            <div class="message-item ${isUnread ? 'unread' : ''}" data-id="${message.id}">
                <div class="message-title">${this.escapeHtml(message.titulo)}</div>
                <div class="message-preview">${this.escapeHtml(message.contenido)}</div>
                <div class="message-meta">
                    <span class="message-type ${message.tipo}">${message.tipo}</span>
                    <span class="message-date">${fecha}</span>
                </div>
            </div>
        `;
    }

    renderError(errorMessage) {
        const content = document.getElementById(`${this.containerId}-content`);
        content.innerHTML = `
            <div class="message-widget-empty">
                <i class="fas fa-exclamation-triangle"></i>
                <p>${errorMessage}</p>
            </div>
        `;
    }

    setupWebSocket() {
        try {
            const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
            const wsUrl = `${protocol}//${window.location.host}${this.options.wsUrl}`;
            
            this.websocket = new WebSocket(wsUrl);
            
            this.websocket.onopen = () => {
                console.log('WebSocket connected to MessageWidget');
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
                console.log('WebSocket closed:', event.code, event.reason);
                // Intentar reconectar después de 5 segundos
                setTimeout(() => this.setupWebSocket(), 5000);
            };
            
            this.websocket.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Error setting up WebSocket:', error);
        }
    }

    handleWebSocketMessage(data) {
        switch (data.type) {
            case 'new_message':
                this.unreadCount++;
                this.updateBadge();
                this.loadMessages(); // Recargar mensajes
                break;
                
            case 'message_read':
                if (this.unreadCount > 0) {
                    this.unreadCount--;
                    this.updateBadge();
                }
                break;
                
            case 'messages_updated':
                this.loadMessages();
                break;
        }
    }

    updateBadge() {
        const badge = document.getElementById(`${this.containerId}-badge`);
        if (this.unreadCount > 0) {
            badge.textContent = this.unreadCount > 99 ? '99+' : this.unreadCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
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
        
        // Recargar mensajes al abrir
        this.loadMessages();
    }

    close() {
        const panel = document.getElementById(`${this.containerId}-panel`);
        if (panel) {
            panel.classList.remove('show');
        }
        this.isOpen = false;
    }

    onMessageClick(message) {
        // Marcar como leído si no lo está
        if (!message.leido) {
            this.markAsRead(message.id);
        }
        
        // Opcional: navegar a la página de detalles del mensaje
        if (this.options.onMessageClick) {
            this.options.onMessageClick(message);
        }
    }

    async markAsRead(messageId) {
        try {
            const response = await fetch(`${this.options.apiUrl}${messageId}/marcar-leido`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Actualizar localmente
                const message = this.messages.find(m => m.id === messageId);
                if (message) {
                    message.leido = true;
                    if (this.unreadCount > 0) {
                        this.unreadCount--;
                        this.updateBadge();
                    }
                    this.renderMessages();
                }
            }
        } catch (error) {
            console.error('Error marking message as read:', error);
        }
    }

    startAutoRefresh() {
        this.refreshTimer = setInterval(() => {
            if (!this.isOpen) { // Solo refrescar cuando está cerrado
                this.loadMessages();
            }
        }, this.options.refreshInterval);
    }

    stopAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
        }
    }

    formatDate(dateString) {
        try {
            const date = new Date(dateString);
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMs / 3600000);
            const diffDays = Math.floor(diffMs / 86400000);
            
            if (diffMins < 1) return 'Ahora';
            if (diffMins < 60) return `${diffMins}m`;
            if (diffHours < 24) return `${diffHours}h`;
            if (diffDays < 7) return `${diffDays}d`;
            
            return date.toLocaleDateString('es-ES', { 
                day: 'numeric', 
                month: 'short' 
            });
        } catch (error) {
            return 'Fecha inválida';
        }
    }

    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    destroy() {
        this.stopAutoRefresh();
        
        if (this.websocket) {
            this.websocket.close();
            this.websocket = null;
        }
        
        if (this.container) {
            this.container.innerHTML = '';
        }
        
        console.log('MessageWidget destroyed');
    }
}

// Exportar para uso global
window.MessageWidget = MessageWidget;
