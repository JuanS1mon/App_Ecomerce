// Gestor principal de servicios
const ServiceManager = {
    init() {
        // Inicializar cuando el DOM esté listo
        document.addEventListener('DOMContentLoaded', () => {
            this.initTabs();
            this.loadServices();
            this.loadMaestros();
            this.initDragAndDrop();
            this.initButtons();
            this.initAppNameEditor();
            this.initContextMenu();
        });
    },

    // Inicializar pestañas
    initTabs() {
        const tabs = document.querySelectorAll('.tab');
        const panels = document.querySelectorAll('.panel');
        
        tabs.forEach(tab => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                panels.forEach(panel => panel.classList.add('hidden'));
                const targetPanel = document.getElementById(tab.dataset.target);
                if (targetPanel) targetPanel.classList.remove('hidden');
            });
        });
    },

    // Cargar servicios
    async loadServices() {
        const servicesTable = document.getElementById('services-table');
        try {
            const response = await fetch('/servicios/api/listar');
            if (!response.ok) throw new Error('Error al cargar servicios');
            
            const data = await response.json();
            this.renderServicesTable(data.servicios || []);
        } catch (error) {
            console.error('Error:', error);
            this.showNotification('Error al cargar servicios', 'error');
        }
    },

    // Renderizar tabla de servicios
    renderServicesTable(services) {
        const servicesTable = document.getElementById('services-table');
        if (!services.length) {
            servicesTable.innerHTML = `
                <tr>
                    <td colspan="4" class="py-4 text-center text-gray-500">
                        No hay servicios disponibles
                    </td>
                </tr>
            `;
            return;
        }

        servicesTable.innerHTML = services.map(service => `
            <tr>
                <td class="py-2 px-4 border-b border-gray-200">${service.name || 'Sin nombre'}</td>
                <td class="py-2 px-4 border-b border-gray-200">${service.path || 'Sin ruta'}</td>
                <td class="py-2 px-4 border-b border-gray-200">
                    <span class="px-2 py-1 text-sm rounded-full ${
                        service.active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }">
                        ${service.active ? 'Activo' : 'Inactivo'}
                    </span>
                </td>
                <td class="py-2 px-4 border-b border-gray-200 flex gap-2">
                    <button onclick="ServiceManager.toggleService('${service.path}', ${!service.active})"
                            class="px-3 py-1 text-sm rounded-md ${
                                service.active 
                                    ? 'bg-red-100 text-red-700 hover:bg-red-200' 
                                    : 'bg-green-100 text-green-700 hover:bg-green-200'
                            }">
                        ${service.active ? 'Desactivar' : 'Activar'}
                    </button>
                    <button onclick="ServiceManager.refreshService('${service.path}')"
                            class="bg-blue-100 text-blue-700 px-3 py-1 text-sm rounded-md hover:bg-blue-200">
                        <i class="fas fa-sync-alt mr-1"></i> Refrescar
                    </button>
                </td>
            </tr>
        `).join('');
    },

    // Inicializar botones
    initButtons() {
        document.getElementById('refresh-all-btn')?.addEventListener('click', () => this.refreshAll());
        document.getElementById('scan-services-btn')?.addEventListener('click', () => this.scanNewServices());
        document.getElementById('save-state-btn')?.addEventListener('click', () => this.saveState());
    },

    // Inicializar drag and drop
    initDragAndDrop() {
        const serviceCards = document.querySelectorAll('.service-card');
        const appContainer = document.getElementById('app-container');
        
        serviceCards.forEach(card => {
            card.addEventListener('dragstart', this.handleDragStart.bind(this));
            card.addEventListener('dragend', this.handleDragEnd.bind(this));
        });

        appContainer.addEventListener('dragover', this.handleDragOver.bind(this));
        appContainer.addEventListener('drop', this.handleDrop.bind(this));
    },

    // Funciones para drag and drop
    handleDragStart(e) {
        e.dataTransfer.setData('text/plain', e.target.dataset.serviceId);
        e.target.classList.add('dragging');
    },

    handleDragEnd(e) {
        e.target.classList.remove('dragging');
    },

    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    },

    handleDrop(e) {
        e.preventDefault();
        const serviceId = e.dataTransfer.getData('text/plain');
        // Implementar lógica de colocación del servicio
        this.addServiceToContainer(serviceId, e.clientX, e.clientY);
    },

    // Notificaciones
    showNotification(message, type = 'success') {
        const container = document.getElementById('notifications-container');
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        
        const icon = type === 'success' ? 'check-circle' : 
                    type === 'error' ? 'exclamation-circle' : 'info-circle';

        notification.innerHTML = `
            <div class="flex items-center p-4 bg-white rounded-lg shadow-md border-l-4 ${
                type === 'success' ? 'border-green-500' :
                type === 'error' ? 'border-red-500' : 'border-blue-500'
            }">
                <i class="fas fa-${icon} mr-3 ${
                    type === 'success' ? 'text-green-500' :
                    type === 'error' ? 'text-red-500' : 'text-blue-500'
                }"></i>
                <span>${message}</span>
                <button class="ml-auto" onclick="this.parentElement.parentElement.remove();">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        `;
        
        container.appendChild(notification);
        setTimeout(() => notification.remove(), 3000);
    }
};

// Inicializar el gestor de servicios
ServiceManager.init();