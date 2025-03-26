document.addEventListener('DOMContentLoaded', function() {
    // Referencias a elementos DOM
    const serviceCards = document.querySelectorAll('.service-card');
    const appContainer = document.getElementById('app-container');
    const appCore = document.getElementById('app-core');
    const servicesContainer = document.getElementById('services-container');
    const connectorPoints = document.querySelectorAll('.connector-point');
    const serviceSummary = document.getElementById('service-summary');
    const generateAppBtn = document.getElementById('generate-app');
    const clearServicesBtn = document.getElementById('clear-services');
    
    // Mapa para rastrear servicios añadidos y sus posiciones
    const addedServices = new Map();
    
    // Colores para los servicios
    const serviceColors = {
        'database': {bg: 'bg-blue-100', text: 'text-blue-600', border: 'border-blue-200'},
        'rest-api': {bg: 'bg-green-100', text: 'text-green-600', border: 'border-green-200'},
        'analytics': {bg: 'bg-purple-100', text: 'text-purple-600', border: 'border-purple-200'},
        'auth': {bg: 'bg-amber-100', text: 'text-amber-600', border: 'border-amber-200'},
        'notifications': {bg: 'bg-red-100', text: 'text-red-600', border: 'border-red-200'},
        'scraping': {bg: 'bg-indigo-100', text: 'text-indigo-600', border: 'border-indigo-200'},
        'frontend': {bg: 'bg-pink-100', text: 'text-pink-600', border: 'border-pink-200'},
        'storage': {bg: 'bg-cyan-100', text: 'text-cyan-600', border: 'border-cyan-200'}
    };
    
    // Coordenadas para posicionar servicios (8 posiciones alrededor del núcleo)
    const positions = [
        {x: 50, y: 15, angle: 270},  // arriba
        {x: 75, y: 25, angle: 315},  // arriba-derecha
        {x: 85, y: 50, angle: 0},    // derecha
        {x: 75, y: 75, angle: 45},   // abajo-derecha
        {x: 50, y: 85, angle: 90},   // abajo
        {x: 25, y: 75, angle: 135},  // abajo-izquierda
        {x: 15, y: 50, angle: 180},  // izquierda
        {x: 25, y: 25, angle: 225}   // arriba-izquierda
    ];
    
    // Configuración de eventos de arrastrar y soltar para servicios
    serviceCards.forEach(card => {
        card.addEventListener('dragstart', handleDragStart);
        card.addEventListener('dragend', handleDragEnd);
    });
    
    // Configuración de eventos para el área de destino
    appContainer.addEventListener('dragover', handleDragOver);
    appContainer.addEventListener('dragenter', handleDragEnter);
    appContainer.addEventListener('dragleave', handleDragLeave);
    appContainer.addEventListener('drop', handleDrop);
    
    // Eventos para puntos de conexión
    connectorPoints.forEach(point => {
        point.addEventListener('dragenter', highlightConnector);
        point.addEventListener('dragleave', unhighlightConnector);
        
        // Añadir clase para hacer más visibles los puntos de conexión disponibles
        point.classList.add('available');
    });
    
    // Evento para el botón de limpiar
    if (clearServicesBtn) {
        clearServicesBtn.addEventListener('click', clearServices);
    }
    
    // Evento para el botón de generar aplicación
    if (generateAppBtn) {
        generateAppBtn.addEventListener('click', generateApplication);
    }
    
    // Función para hacer que un bloque de servicio sea arrastrable
    function makeServiceBlockDraggable(serviceBlockEl, positionIndex) {
        serviceBlockEl.setAttribute('draggable', 'true');
        serviceBlockEl.dataset.position = positionIndex;
        
        // Eventos de arrastrar para bloques ya colocados
        serviceBlockEl.addEventListener('dragstart', function(e) {
            e.stopPropagation(); // Importante para evitar conflictos
            e.dataTransfer.setData('application/serviceblock', this.dataset.serviceId);
            e.dataTransfer.effectAllowed = 'move';
            this.classList.add('opacity-50');
            this.classList.add('dragging');
            
            // Guardar posición original por si se cancela el arrastre
            this.dataset.originalPosition = this.dataset.position;
        });
        
        serviceBlockEl.addEventListener('dragend', function(e) {
            this.classList.remove('opacity-50');
            this.classList.remove('dragging');
            unhighlightAllConnectors();
            
            // Si se soltó fuera de un punto válido, devolver a la posición original
            if (this.dataset.moved !== 'true') {
                const originalPosition = parseInt(this.dataset.originalPosition);
                const serviceId = this.dataset.serviceId;
                
                // Reposicionar al punto original
                repositionService(serviceId, originalPosition);
            }
            
            // Limpiar flag temporal
            delete this.dataset.moved;
            delete this.dataset.originalPosition;
        });
    }
    
    // Funciones de manejo de arrastrar y soltar
    function handleDragStart(e) {
        // Solo aplicar a cards, no a bloques ya colocados
        if (!e.currentTarget.classList.contains('service-block')) {
            e.dataTransfer.setData('text/plain', e.currentTarget.dataset.serviceId);
            e.currentTarget.classList.add('opacity-50');
        }
    }
    
    function handleDragEnd(e) {
        // Solo aplicar a cards, no a bloques ya colocados
        if (!e.currentTarget.classList.contains('service-block')) {
            e.currentTarget.classList.remove('opacity-50');
        }
        unhighlightAllConnectors();
    }
    
    function handleDragOver(e) {
        e.preventDefault();
    }
    
    function handleDragEnter(e) {
        e.preventDefault();
        appContainer.classList.add('drag-over');
    }
    
    function handleDragLeave(e) {
        // Asegúrate de que realmente estamos dejando el contenedor y no entrando a un hijo
        const relatedTarget = e.relatedTarget;
        if (!appContainer.contains(relatedTarget)) {
            appContainer.classList.remove('drag-over');
            unhighlightAllConnectors();
        }
    }
    
    function handleDrop(e) {
        e.preventDefault();
        appContainer.classList.remove('drag-over');
        unhighlightAllConnectors();
        
        // Verificar si es un servicio nuevo o uno existente que se está moviendo
        const newServiceId = e.dataTransfer.getData('text/plain');
        const existingServiceId = e.dataTransfer.getData('application/serviceblock');
        
        // Determinar el punto de conexión más cercano
        let targetConnector = getClosestConnector(e.clientX, e.clientY);
        const targetPosition = parseInt(targetConnector.dataset.position);
        
        // Si es un servicio existente que se está moviendo
        if (existingServiceId && addedServices.has(existingServiceId)) {
            const currentPosition = addedServices.get(existingServiceId).position;
            
            // Si se está intentando soltar en la misma posición, no hacer nada
            if (currentPosition === targetPosition) return;
            
            // Si el punto está ocupado por otro servicio, buscar uno libre
            const occupiedBy = findServiceByPosition(targetPosition);
            if (occupiedBy !== null && occupiedBy !== existingServiceId) {
                targetConnector = findFreeConnector();
                if (targetConnector === null) {
                    showNotification('No hay más puntos de conexión disponibles', 'warning');
                    return;
                }
            }
            
            // Marcar como movido para que no se restaure en dragend
            const serviceBlock = document.querySelector(`.service-block[data-service-id="${existingServiceId}"]`);
            if (serviceBlock) {
                serviceBlock.dataset.moved = 'true';
            }
            
            // Reposicionar el servicio
            repositionService(existingServiceId, parseInt(targetConnector.dataset.position));
            showNotification(`Servicio reposicionado`, 'info');
        } 
        // Si es un nuevo servicio
        else if (newServiceId) {
            const serviceCard = document.querySelector(`.service-card[data-service-id="${newServiceId}"]`);
            
            // Si ya existe este servicio, no lo añadimos de nuevo
            if (addedServices.has(newServiceId)) {
                showNotification('Este servicio ya ha sido añadido', 'warning');
                return;
            }
            
            // Si el punto está ocupado, buscar uno libre
            if (findServiceByPosition(targetPosition) !== null) {
                targetConnector = findFreeConnector();
                if (targetConnector === null) {
                    showNotification('No hay más puntos de conexión disponibles', 'warning');
                    return;
                }
            }
            
            // Añadir servicio en la posición del conector
            addServiceToApp(serviceCard, parseInt(targetConnector.dataset.position));
        }
        
        // Actualizar resumen y botones
        updateServiceSummary();
        updateButtons();
    }
    
    function highlightConnector(e) {
        // No resaltar si ya hay un servicio en esta posición
        const position = this.dataset.position;
        if (findServiceByPosition(position) !== null) return;
        
        this.classList.add('highlight');
    }
    
    function unhighlightConnector() {
        this.classList.remove('highlight');
    }
    
    function unhighlightAllConnectors() {
        connectorPoints.forEach(point => point.classList.remove('highlight'));
    }
    
    // Encontrar el conector más cercano al punto de soltar
    function getClosestConnector(clientX, clientY) {
        const rect = appContainer.getBoundingClientRect();
        const dropX = clientX - rect.left;
        const dropY = clientY - rect.top;
        
        let closestConnector = connectorPoints[0];
        let minDistance = Number.MAX_VALUE;
        
        connectorPoints.forEach(connector => {
            const connectorRect = connector.getBoundingClientRect();
            const connectorX = connectorRect.left - rect.left + connectorRect.width / 2;
            const connectorY = connectorRect.top - rect.top + connectorRect.height / 2;
            
            const distance = Math.sqrt(Math.pow(dropX - connectorX, 2) + Math.pow(dropY - connectorY, 2));
            
            if (distance < minDistance) {
                minDistance = distance;
                closestConnector = connector;
            }
        });
        
        return closestConnector;
    }
    
    // Encontrar un conector libre
    function findFreeConnector() {
        for (let connector of connectorPoints) {
            const position = connector.dataset.position;
            if (findServiceByPosition(position) === null) {
                return connector;
            }
        }
        return null;
    }
    
    // Encontrar un servicio por su posición
    function findServiceByPosition(position) {
        for (let [id, data] of addedServices) {
            if (data.position.toString() === position.toString()) {
                return id;
            }
        }
        return null;
    }
    
    // Añadir servicio a la aplicación
    function addServiceToApp(serviceCard, positionIndex) {
        const serviceId = serviceCard.dataset.serviceId;
        const serviceName = serviceCard.querySelector('h3').textContent;
        const serviceIconClass = serviceCard.querySelector('.service-icon').className.split(' ').filter(cls => cls.startsWith('fa-'))[0]; // Obtener solo "fa-xxx"
        const colors = serviceColors[serviceId];
        
        // Crear el elemento del bloque de servicio
        const serviceBlockEl = document.createElement('div');
        serviceBlockEl.className = `service-block ${colors.border}`;
        serviceBlockEl.dataset.serviceId = serviceId;
        serviceBlockEl.innerHTML = `
            <div class="service-block-icon ${colors.bg} ${colors.text}">
                <i class="fas ${serviceIconClass}"></i>
            </div>
            <div class="service-block-title">${serviceName}</div>
            <button class="remove-service absolute -top-2 -right-2 bg-red-100 text-red-600 rounded-full w-6 h-6 flex items-center justify-center hover:bg-red-200" title="Eliminar servicio">
                <i class="fas fa-times text-xs"></i>
            </button>
        `;
        
        // Posicionar el bloque según la posición asignada
        const position = positions[positionIndex];
        serviceBlockEl.style.top = `${position.y}%`;
        serviceBlockEl.style.left = `${position.x}%`;
        serviceBlockEl.style.transform = 'translate(-50%, -50%) scale(0)';
        
        // Crear la línea de conexión
        const connectionLine = document.createElement('div');
        connectionLine.className = 'connection-line';
        
        // Calcular la posición y rotación de la línea
        const centerX = 50;
        const centerY = 50;
        const deltaX = position.x - centerX;
        const deltaY = position.y - centerY;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
        
        connectionLine.style.top = `${centerY}%`;
        connectionLine.style.left = `${centerX}%`;
        connectionLine.style.width = `${distance - 40}px`;  // Restamos el radio del núcleo y del bloque
        connectionLine.style.transform = `rotate(${angle}deg)`;
        
        // Añadir elementos al DOM
        servicesContainer.appendChild(connectionLine);
        servicesContainer.appendChild(serviceBlockEl);
        
        // Animar la conexión y la aparición del bloque
        setTimeout(() => {
            connectionLine.style.animation = 'connect 0.5s forwards';
            setTimeout(() => {
                serviceBlockEl.style.transform = 'translate(-50%, -50%) scale(1)';
                serviceBlockEl.style.animation = 'pop 0.5s forwards';
            }, 300);
        }, 100);
        
        // Guardar el servicio y su posición
        addedServices.set(serviceId, {
            name: serviceName,
            position: positionIndex,
            element: serviceBlockEl,
            connection: connectionLine
        });
        
        // Añadir evento para eliminar el servicio
        serviceBlockEl.querySelector('.remove-service').addEventListener('click', () => {
            removeService(serviceId);
        });
        
        // Hacer que el bloque de servicio sea arrastrable
        makeServiceBlockDraggable(serviceBlockEl, positionIndex);
        
        // Mostrar notificación
        showNotification(`Servicio "${serviceName}" conectado correctamente`, 'success');
    }
    
    // Función para reposicionar un servicio existente
    function repositionService(serviceId, newPosition) {
        const serviceData = addedServices.get(serviceId);
        if (!serviceData) return;
        
        // Obtener elementos
        const serviceElement = serviceData.element;
        const oldConnectionElement = serviceData.connection;
        
        // Eliminar la conexión anterior
        oldConnectionElement.style.opacity = '0';
        setTimeout(() => {
            oldConnectionElement.remove();
        }, 300);
        
        // Posicionar el bloque según la nueva posición
        const position = positions[newPosition];
        serviceElement.style.transition = 'all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        serviceElement.style.top = `${position.y}%`;
        serviceElement.style.left = `${position.x}%`;
        serviceElement.dataset.position = newPosition;
        
        // Crear nueva línea de conexión
        const connectionLine = document.createElement('div');
        connectionLine.className = 'connection-line';
        
        // Calcular la posición y rotación de la línea
        const centerX = 50;
        const centerY = 50;
        const deltaX = position.x - centerX;
        const deltaY = position.y - centerY;
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
        const angle = Math.atan2(deltaY, deltaX) * (180 / Math.PI);
        
        connectionLine.style.top = `${centerY}%`;
        connectionLine.style.left = `${centerX}%`;
        connectionLine.style.width = `${distance - 40}px`;
        connectionLine.style.transform = `rotate(${angle}deg)`;
        
        // Añadir nueva línea de conexión al DOM
        servicesContainer.appendChild(connectionLine);
        
        // Animar la conexión
        setTimeout(() => {
            connectionLine.style.animation = 'connect 0.5s forwards';
        }, 100);
        
        // Actualizar datos del servicio
        serviceData.position = newPosition;
        serviceData.connection = connectionLine;
    }
    
    // Eliminar un servicio
    function removeService(serviceId) {
        const serviceData = addedServices.get(serviceId);
        if (!serviceData) return;
        
        // Obtener elementos
        const serviceElement = serviceData.element;
        const connectionElement = serviceData.connection;
        const serviceName = serviceData.name;
        
        // Animar la desaparición
        serviceElement.style.transform = 'translate(-50%, -50%) scale(0)';
        connectionElement.style.opacity = '0';
        
        // Eliminar del DOM después de la animación
        setTimeout(() => {
            serviceElement.remove();
            connectionElement.remove();
            
            // Eliminar del mapa
            addedServices.delete(serviceId);
            
            // Actualizar UI
            updateServiceSummary();
            updateButtons();
            
            // Mostrar notificación
            showNotification(`Servicio "${serviceName}" desconectado`, 'info');
        }, 300);
    }
    
    // Limpiar todos los servicios
    function clearServices() {
        // Crear una copia de las IDs para iterar mientras eliminamos
        const serviceIds = Array.from(addedServices.keys());
        
        // Eliminar cada servicio con una pequeña demora para efecto visual en cadena
        let delay = 0;
        serviceIds.forEach(id => {
            setTimeout(() => {
                removeService(id);
            }, delay);
            delay += 100;
        });
        
        // Mostrar notificación
        showNotification('Todos los servicios han sido desconectados', 'info');
    }
    
    // Actualizar el resumen de servicios
    function updateServiceSummary() {
        if (serviceSummary) {
            if (addedServices.size === 0) {
                serviceSummary.innerHTML = '<p>No hay servicios añadidos todavía.</p>';
                return;
            }
            
            let html = '<ul class="list-disc list-inside space-y-1">';
            
            addedServices.forEach((data, serviceId) => {
                const originalCard = document.querySelector(`[data-service-id="${serviceId}"]`);
                if (originalCard) {
                    const serviceDesc = originalCard.querySelector('p') ? 
                                     originalCard.querySelector('p').textContent : '';
                    
                    html += `<li><span class="font-medium">${data.name}</span>${serviceDesc ? ' - ' + serviceDesc : ''}</li>`;
                }
            });
            
            html += '</ul>';
            serviceSummary.innerHTML = html;
        }
    }
    
    // Actualizar estado de los botones
    function updateButtons() {
        const hasServices = addedServices.size > 0;
        
        if (generateAppBtn) {
            generateAppBtn.disabled = !hasServices;
            
            if (hasServices) {
                generateAppBtn.classList.remove('disabled:opacity-50', 'disabled:cursor-not-allowed');
            } else {
                generateAppBtn.classList.add('disabled:opacity-50', 'disabled:cursor-not-allowed');
            }
        }
        
        if (clearServicesBtn) {
            clearServicesBtn.disabled = !hasServices;
            
            if (hasServices) {
                clearServicesBtn.classList.remove('disabled:opacity-50', 'disabled:cursor-not-allowed');
            } else {
                clearServicesBtn.classList.add('disabled:opacity-50', 'disabled:cursor-not-allowed');
            }
        }
        
        // Actualizar la visibilidad del indicador de arrastrar y soltar
        const dropIndicator = document.querySelector('.drop-indicator');
        if (dropIndicator) {
            if (hasServices) {
                dropIndicator.style.opacity = '0';
            } else {
                dropIndicator.style.opacity = '1';
            }
        }
    }
    
    // Generar aplicación
    function generateApplication() {
        // Array con los IDs de los servicios seleccionados
        const selectedServices = Array.from(addedServices.keys());
        
        // Aquí iría el código para enviar los servicios al backend
        console.log('Generando aplicación con servicios:', selectedServices);
        
        // Animar el núcleo de la aplicación
        appCore.style.transform = 'scale(1.2)';
        setTimeout(() => {
            appCore.style.transform = 'scale(1)';
        }, 300);
        
        // Mostrar notificación
        showNotification('¡Aplicación generada con éxito!', 'success');
        
        // En un caso real, aquí redirigirías a la nueva aplicación o mostrarías más información
        setTimeout(() => {
            alert('Aplicación generada con éxito. En un entorno real, serías redirigido a tu nueva aplicación.');
        }, 1000);
    }
    
    // Mostrar notificación temporal
    function showNotification(message, type = 'info') {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        
        // Determinar color según el tipo
        let bgColor, textColor, icon;
        switch (type) {
            case 'success':
                bgColor = 'bg-green-100';
                textColor = 'text-green-800';
                icon = 'fa-check-circle';
                break;
            case 'warning':
                bgColor = 'bg-yellow-100';
                textColor = 'text-yellow-800';
                icon = 'fa-exclamation-triangle';
                break;
            case 'error':
                bgColor = 'bg-red-100';
                textColor = 'text-red-800';
                icon = 'fa-times-circle';
                break;
            default:
                bgColor = 'bg-blue-100';
                textColor = 'text-blue-800';
                icon = 'fa-info-circle';
        }
        
        // Configurar notificación
        notification.className = `fixed top-4 right-4 ${bgColor} ${textColor} px-4 py-3 rounded-lg shadow-md flex items-center space-x-3 transition-all duration-300 ease-in-out z-50`;
        notification.innerHTML = `
            <i class="fas ${icon}"></i>
            <span>${message}</span>
        `;
        
        // Añadir a DOM
        document.body.appendChild(notification);
        
        // Animar entrada
        setTimeout(() => notification.style.opacity = '1', 10);
        
        // Auto eliminación
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }
});