/**
 * ScraperApp - Aplicación para creación y gestión de web scrapers
 * Versión: 1.0.0
 */
(function() {
    'use strict';

    // ===== VARIABLES GLOBALES =====
    let jsEditor;
    
    // Objeto de configuración de la aplicación
    const config = {
        delays: {
            animationDelay: 300
        },
        selectors: {
            defaultMaxPages: 5
        }
    };
    
    // Mapa de pasos del wizard
    const steps = {
        1: { step: document.getElementById('step1'), content: document.getElementById('step1-content') },
        2: { step: document.getElementById('step2'), content: document.getElementById('step2-content') },
        3: { step: document.getElementById('step3'), content: document.getElementById('step3-content') },
        4: { step: document.getElementById('step4'), content: document.getElementById('step4-content') }
    };

    // ===== INICIALIZACIÓN =====
    document.addEventListener('DOMContentLoaded', initializeApp);

    function initializeApp() {
        // Inicializar componentes principales
        initUI();
        registerEventHandlers();
    }
    
    function initUI() {
        initCodeEditor();
        initToggleControls();
        initDynamicElements();
        initNavigationControls();
        initInteractiveElements();
    }
    
    function initCodeEditor() {
        const codeElement = document.getElementById('javascript-code');
        if (!codeElement) return;
        
        jsEditor = CodeMirror.fromTextArea(codeElement, {
            mode: "javascript",
            theme: "dracula",
            lineNumbers: true,
            autoCloseBrackets: true,
            matchBrackets: true,
            indentUnit: 4
        });
    }
    
    function registerEventHandlers() {
        // Registrar eventos para el menú de perfil
        registerProfileMenuEvents();
        
        // Registrar eventos para selectores de tecnología
        registerTechnologySelectorEvents();
    }
    
    /**
     * Registra eventos para el menú de perfil
     */
    function registerProfileMenuEvents() {
        const perfilButton = document.getElementById('perfil');
        const perfilMenu = document.getElementById('menu-perfil');
        
        if (!perfilButton || !perfilMenu) return;
        
        perfilButton.addEventListener('click', () => {
            perfilMenu.classList.toggle('hidden');
        });
        
        // Cerrar menú cuando se hace clic fuera
        document.addEventListener('click', event => {
            if (!perfilButton.contains(event.target) && !perfilMenu.contains(event.target)) {
                perfilMenu.classList.add('hidden');
            }
        });
    }

    /**
     * Registra eventos para los selectores de tecnología
     */
    function registerTechnologySelectorEvents() {
        const techRadios = document.querySelectorAll('.tech-radio');
        const techChecks = document.querySelectorAll('.tech-check');
        
        if (!techRadios.length || !techChecks.length) return;
        
        techRadios.forEach((radio, index) => {
            radio.addEventListener('change', function() {
                // Ocultar todos los checks primero
                techChecks.forEach(check => check.classList.add('hidden'));
                
                // Mostrar el check correspondiente si el radio está seleccionado
                if (this.checked && techChecks[index]) {
                    techChecks[index].classList.remove('hidden');
                }
            });
        });
    }

    /**
     * Recopila la configuración completa del scraper desde el formulario
     */
    function collectScraperConfig() {
        // URL y tecnología
        const url = document.getElementById('scraper-url')?.value?.trim() || '';
        
        // Determinar la tecnología seleccionada
        let technology = 'beautifulsoup'; // Valor por defecto
        document.querySelectorAll('input[name="tech"]').forEach(radio => {
            if (radio.checked) technology = radio.value;
        });
        
        // Recopilación de selectores
        const selectors = [];
        document.querySelectorAll('.selector-item').forEach(item => {
            const name = item.querySelector('input[name="selector_name[]"]')?.value?.trim() || '';
            const path = item.querySelector('input[name="selector_path[]"]')?.value?.trim() || '';
            const type = item.querySelector('select[name="selector_type[]"]')?.value || 'text';
            const attribute = item.querySelector('input[name="selector_attribute[]"]')?.value?.trim() || '';
            const multiple = item.querySelector('select[name="selector_multiple[]"]')?.value === 'yes';
            
            // Solo añadir selectores con nombre y path definidos
            if (name && path) {
                selectors.push({ name, path, type, attribute, multiple });
            }
        });
        
        // Validación básica: si no hay selectores, añadir uno por defecto
        if (selectors.length === 0) {
            selectors.push({
                name: "contenido",
                path: "body",
                type: "text",
                attribute: "",
                multiple: false
            });
        }
        
        // Estructura completa de la configuración
        return {
            url,
            technology,
            selectors,
            container_selector: document.getElementById('container-selector')?.value?.trim() || '',
            request_delay: parseInt(document.getElementById('request-delay')?.value || '0'),
            request_timeout: parseInt(document.getElementById('request-timeout')?.value || '30'),
            proxy: {
                enabled: document.getElementById('use-proxy')?.checked || false,
                address: document.querySelector('input[name="proxy_address"]')?.value?.trim() || '',
                proxy_type: document.querySelector('select[name="proxy_type"]')?.value || 'http'
            },
            pagination: {
                enabled: document.getElementById('use-pagination')?.checked || false,
                type: document.getElementById('pagination-type')?.value || 'link',
                next_selector: document.querySelector('input[name="next_page_selector"]')?.value?.trim() || '',
                page_parameter: document.querySelector('input[name="page_parameter"]')?.value?.trim() || '',
                max_pages: parseInt(document.querySelector('input[name="max_pages"]')?.value || '5'),
                load_more_selector: document.querySelector('input[name="load_more_selector"]')?.value?.trim() || ''
            },
            javascript: {
                enabled: document.getElementById('use-javascript')?.checked || false,
                code: jsEditor ? jsEditor.getValue() : document.getElementById('javascript-code')?.value?.trim() || ''
            }
        };
    }
    
    /**
     * Inicializa controles que muestran/ocultan elementos basados en checkboxes
     */
    function initToggleControls() {
        // Mapeo de elementos controladores y sus objetivos
        const toggleMap = [
            { checkbox: 'use-proxy', target: 'proxy-options' },
            { checkbox: 'use-pagination', target: 'pagination-options' },
            { checkbox: 'use-javascript', target: 'javascript-options' },
            { checkbox: 'use-filters', target: 'filter-options' },
            { checkbox: 'schedule-scraper', target: 'schedule-options' },
            { checkbox: 'export-results', target: 'export-options' },
            { checkbox: 'notify-completion', target: 'notification-options' }
        ];
        
        // Configurar cada par de elementos
        toggleMap.forEach(pair => setupVisibilityToggle(pair.checkbox, pair.target));
    }
    
    /**
     * Configura un control de visibilidad basado en checkbox
     * @param {string} checkboxId - ID del checkbox que controla la visibilidad
     * @param {string} targetId - ID del elemento cuya visibilidad será controlada
     */
    function setupVisibilityToggle(checkboxId, targetId) {
        const checkbox = document.getElementById(checkboxId);
        const target = document.getElementById(targetId);
        
        if (!checkbox || !target) return;
        
        // Estado inicial basado en el checkbox
        target.classList.toggle('hidden', !checkbox.checked);
        
        // Cambio dinámico al hacer clic
        checkbox.addEventListener('change', function() {
            target.classList.toggle('hidden', !this.checked);
        });
    }
    
    /**
     * Inicializa elementos dinámicos (selectores, filtros) que pueden añadirse o eliminarse
     */
    function initDynamicElements() {
        initPaginationTypeSelector();
        initScheduleFrequencySelector();
        setupDynamicItemList('add-selector', 'selector-container', '.selector-item', '.remove-selector');
        setupDynamicItemList('add-filter', 'filter-container', '.filter-item', '.remove-filter');
    }

    /**
     * Inicializa el selector de tipo de paginación
     */
    function initPaginationTypeSelector() {
        const paginationType = document.getElementById('pagination-type');
        if (!paginationType) return;
        
        // Elementos que se muestran/ocultan según el tipo
        const containers = {
            link: document.getElementById('next-page-selector-container'),
            parameter: document.getElementById('param-pagination-container'),
            infinite: document.getElementById('scroll-pagination-container')
        };
        
        // Verificar que los contenedores existen
        if (!containers.link || !containers.parameter) return;
        
        paginationType.addEventListener('change', function() {
            // Ocultar todos los contenedores
            Object.values(containers).forEach(container => {
                if (container) container.classList.add('hidden');
            });
            
            // Mostrar el contenedor correspondiente al tipo seleccionado
            const selectedType = this.value;
            if (containers[selectedType]) {
                containers[selectedType].classList.remove('hidden');
            }
        });
    }

    /**
     * Inicializa el selector de frecuencia de programación
     */
    function initScheduleFrequencySelector() {
        const scheduleFrequency = document.getElementById('schedule-frequency');
        const scheduleDateContainer = document.getElementById('schedule-date-container');
        const scheduleCronContainer = document.getElementById('schedule-cron-container');
        
        if (!scheduleFrequency || !scheduleDateContainer || !scheduleCronContainer) return;
        
        scheduleFrequency.addEventListener('change', function() {
            const isCustom = this.value === 'custom';
            scheduleDateContainer.classList.toggle('hidden', isCustom);
            scheduleCronContainer.classList.toggle('hidden', !isCustom);
        });
    }

        /**
     * Configura una lista de elementos dinámicos que pueden añadirse o eliminarse
     * @param {string} addButtonId - ID del botón para añadir elementos
     * @param {string} containerId - ID del contenedor de la lista
     * @param {string} itemSelector - Selector CSS para los elementos de la lista
     * @param {string} removeButtonSelector - Selector CSS para los botones de eliminación
     */
    function setupDynamicItemList(addButtonId, containerId, itemSelector, removeButtonSelector) {
        const addButton = document.getElementById(addButtonId);
        const container = document.getElementById(containerId);
        
        if (!addButton || !container) return;
        
        const firstItem = container.querySelector(itemSelector);
        if (!firstItem) return;
        
        // Configurar botón para añadir elementos
        addButton.addEventListener('click', function() {
            // Clonar el primer elemento como plantilla
            const newItem = firstItem.cloneNode(true);
            // Resetear los valores de los campos
            resetFormFields(newItem);
            // Añadir el nuevo elemento al contenedor
            container.appendChild(newItem);
            // Configurar el botón de eliminación para el nuevo elemento
            setupRemoveButton(newItem, removeButtonSelector);
        });
    
        // Configurar botones de eliminación para elementos existentes
        const items = container.querySelectorAll(itemSelector);
        items.forEach(item => {
            setupRemoveButton(item, removeButtonSelector, () => {
                // Condición: permitir eliminar solo si hay más de un elemento
                return container.querySelectorAll(itemSelector).length > 1;
            });
        });
    }
    /**
     * Resetea los valores de campos de formulario en un elemento
     * @param {HTMLElement} element - Elemento contenedor con campos a resetear
     */
    function resetFormFields(element) {
        if (!element) return;
        
        element.querySelectorAll('input, select, textarea').forEach(field => {
            if (field.tagName === 'SELECT') {
                field.selectedIndex = 0;
            } else {
                field.value = '';
            }
        });
    }
    
    /**
     * Configura un botón para eliminar su elemento contenedor
     * @param {HTMLElement} item - Elemento que contiene el botón de eliminación
     * @param {string} buttonSelector - Selector CSS para el botón de eliminación
     * @param {Function} [condition] - Función opcional que debe retornar true para permitir eliminación
     */
    function setupRemoveButton(item, buttonSelector, condition = () => true) {
        if (!item) return;
        
        const removeButton = item.querySelector(buttonSelector);
        if (!removeButton) return;
        
        removeButton.addEventListener('click', function() {
            // Verificar condición adicional si se proporciona
            if (condition()) {
                item.remove();
            }
        });
    }
    
    /**
     * Inicializa los controles de navegación entre pasos del wizard
     */
    function initNavigationControls() {
        // Configuración de botones de navegación
        const navigationButtons = [
            // Botones "Siguiente"
            { id: 'next-step1', from: 1, to: 2 },
            { id: 'next-step2', from: 2, to: 3 },
            { id: 'next-step3', from: 3, to: 4, callback: updateSummary },
            
            // Botones "Anterior"
            { id: 'prev-step2', from: 2, to: 1 },
            { id: 'prev-step3', from: 3, to: 2 },
            { id: 'prev-step4', from: 4, to: 3 }
        ];
        
        // Configurar cada botón
        navigationButtons.forEach(button => {
            const element = document.getElementById(button.id);
            if (!element) return;
            
            element.addEventListener('click', () => {
                navigateToStep(button.from, button.to);
                
                // Si hay un callback definido, ejecutarlo
                if (button.callback) button.callback();
            });
        });
    }

    /**
     * Cambia la visualización entre pasos del wizard
     * @param {number} currentStep - Número del paso actual
     * @param {number} targetStep - Número del paso destino
     */
    function navigateToStep(currentStep, targetStep) {
        // Validar que los pasos existan
        if (!steps[currentStep]?.content || !steps[targetStep]?.content) return;
        
        // Ocultar el paso actual
        steps[currentStep].content.classList.add('hidden');
        
        // Mostrar el paso destino
        steps[targetStep].content.classList.remove('hidden');
        
        // Actualizar los indicadores visuales de progreso
        updateStepIndicators(targetStep);
    }

    /**
     * Actualiza los indicadores visuales del progreso del wizard
     * @param {number} activeStep - Número del paso activo
     */
    function updateStepIndicators(activeStep) {
        // Recorrer todos los pasos y actualizar su estado visual
        for (let i = 1; i <= Object.keys(steps).length; i++) {
            const stepElement = steps[i]?.step;
            if (!stepElement) continue;
            
            // Eliminar todas las clases de estado
            stepElement.classList.remove('step-active', 'step-complete', 'step-incomplete');
            
            // Añadir la clase adecuada según la posición relativa al paso activo
            if (i < activeStep) {
                stepElement.classList.add('step-complete');
            } else if (i === activeStep) {
                stepElement.classList.add('step-active');
            } else {
                stepElement.classList.add('step-incomplete');
            }
        }
    }
    
    /**
     * Inicializa componentes interactivos (prueba, tooltips, etc)
     */
    function initInteractiveElements() {
        setupExtractionTesting();
        setupActivateScraperButton();
    }

        /**
     * Configura la funcionalidad de prueba de extracción con manejo mejorado de errores
     * y feedback al usuario
     */
    function setupExtractionTesting() {
        // Almacenar referencias a elementos DOM (mejor rendimiento)
        const testButton = document.getElementById('test-extraction');
        const resultsContainer = document.getElementById('preview-results');
        const previewContent = document.getElementById('preview-content');
        
        if (!testButton || !resultsContainer) return;
        
        // Constantes para mensajes de error comunes
        const ERROR_MESSAGES = {
            NO_URL: 'No se ha especificado una URL para extraer datos',
            INVALID_URL: 'La URL proporcionada no tiene un formato válido',
            NO_RESPONSE: 'No se pudo conectar con el servidor. Verifique su conexión a internet',
            TIMEOUT: 'La solicitud ha excedido el tiempo máximo de espera'
        };
        
        // Utilizar AbortController para manejar timeouts
        let controller;
        
        testButton.addEventListener('click', async function() {
            // Verificación previa de URL para evitar peticiones innecesarias
            const urlInput = document.getElementById('scraper-url');
            const url = urlInput?.value?.trim() || '';
            
            if (!url) {
                showExtractionError(ERROR_MESSAGES.NO_URL);
                // Enfoque visual en el campo de URL
                urlInput?.focus();
                return;
            }
            
            try {
                new URL(url); // Validar formato
            } catch (e) {
                showExtractionError(ERROR_MESSAGES.INVALID_URL);
                urlInput?.focus();
                return;
            }
            
            // Actualizar estado del botón
            updateButtonState(testButton, true, 'Ejecutando prueba...', ['opacity-75']);
            
            // Mostrar indicador de carga
            showLoadingIndicator();
            
            // Mostrar contenedor de resultados
            resultsContainer.classList.remove('hidden');
            
            // Crear nuevo controller para esta solicitud
            controller = new AbortController();
            const signal = controller.signal;
            
            // Configurar timeout
            const timeout = setTimeout(() => {
                controller.abort();
            }, 30000); // 30 segundos de timeout
            
            try {
                // Obtener la configuración completa
                const config = collectScraperConfig();
                
                // Realizar petición al backend con timeout y señal para abortar
                const response = await fetch('/scraping/test-extraction', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config),
                    signal
                });
                
                clearTimeout(timeout);
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || data.error || 'Error al realizar la prueba de extracción');
                }
                
                // Mostrar resultados
                if (data.success && data.results?.length) {
                    // Registro de éxito para análisis
                    console.log(`Extracción exitosa: ${data.results.length} elementos`);
                    displayExtractionResults(data.results, data.count || data.results.length);
                } else {
                    throw new Error('La extracción no produjo resultados. Verifique los selectores configurados.');
                }
            } catch (error) {
                // Manejo específico de errores de timeout
                if (error.name === 'AbortError') {
                    showExtractionError(ERROR_MESSAGES.TIMEOUT);
                } else {
                    // Mostrar mensaje de error
                    showExtractionError(error.message);
                    console.error('Error en la extracción:', error);
                }
            } finally {
                clearTimeout(timeout);
                // Restaurar estado del botón
                updateButtonState(testButton, false, 'Probar extracción', [], ['opacity-75']);
            }
        });
        
        // Añadir botón para cancelar la petición
        const cancelButton = document.createElement('button');
        cancelButton.textContent = 'Cancelar';
        cancelButton.className = 'btn btn-sm btn-outline-secondary ml-2';
        cancelButton.style.display = 'none';
        
        // Insertar después del botón de prueba
        testButton.parentNode.insertBefore(cancelButton, testButton.nextSibling);
        
        // Funcionalidad para cancelar
        cancelButton.addEventListener('click', () => {
            if (controller) {
                controller.abort();
                cancelButton.style.display = 'none';
                showExtractionError('Petición cancelada por el usuario');
                updateButtonState(testButton, false, 'Probar extracción', [], ['opacity-75']);
            }
        });
        
        // Modificar updateButtonState para mostrar/ocultar el botón cancelar
        const originalUpdateButtonState = updateButtonState;
        updateButtonState = function(button, disabled, text, classesToAdd = [], classesToRemove = []) {
            originalUpdateButtonState(button, disabled, text, classesToAdd, classesToRemove);
            
            // Si es el botón de prueba, actualizar visibilidad del botón cancelar
            if (button === testButton) {
                cancelButton.style.display = disabled ? 'inline-block' : 'none';
            }
        };
    }
    
    /**
     * Configura la funcionalidad para activar el scraper
     */
    function setupActivateScraperButton() {
        const createButton = document.getElementById('create-scraper');
        if (!createButton) return;
        
        createButton.addEventListener('click', async function() {
            try {
                // Actualizar estado del botón
                updateButtonState(createButton, true, 'Creando...', ['opacity-75']);
                
                // Obtener la configuración completa
                const config = collectScraperConfig();
                
                // Añadir información adicional
                config.name = document.getElementById('scraper-name')?.value?.trim();
                config.schedule = getScheduleConfiguration();
                config.filters = getFilterConfiguration();
                config.export_options = getExportConfiguration();
                config.notifications = getNotificationConfiguration();
                
                // Validaciones básicas
                if (!config.name) {
                    throw new Error('El nombre del scraper es obligatorio');
                }
                
                if (!config.url) {
                    throw new Error('La URL de destino es obligatoria');
                }
                
                // Realizar petición al backend
                const response = await fetch('/scraping/create', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config)
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.message || data.error || 'Error al crear el scraper');
                }
                
                // Redireccionar a la página de administración si todo va bien
                if (data.success) {
                    showSuccessMessage('Scraper creado con éxito. Redireccionando...');
                    setTimeout(() => {
                        window.location.href = '/scraping/admin';
                    }, 2000);
                } else {
                    throw new Error(data.message || 'Error al crear el scraper');
                }
            } catch (error) {
                // Mostrar mensaje de error
                showErrorMessage(error.message);
            } finally {
                // Restaurar estado del botón
                updateButtonState(createButton, false, 'Crear y activar scraper', [], ['opacity-75']);
            }
        });
    }
    
    /**
     * Obtiene la configuración de programación
     */
    function getScheduleConfiguration() {
        // Verificar si la programación está habilitada
        const isScheduleEnabled = document.getElementById('schedule-scraper')?.checked || false;
        
        if (!isScheduleEnabled) {
            return { enabled: false };
        }
        
        const frequency = document.getElementById('schedule-frequency')?.value || 'once';
        
        // Configuración básica
        const schedule = {
            enabled: true,
            frequency: frequency
        };
        
        // Configuración específica según el tipo de frecuencia
        if (frequency === 'custom') {
            schedule.cron_expression = document.querySelector('input[name="schedule_cron"]')?.value || '';
        } else if (frequency === 'once') {
            schedule.datetime = document.querySelector('input[name="schedule_datetime"]')?.value || '';
        }
        
        return schedule;
    }
    
    /**
     * Obtiene la configuración de filtros
     */
    function getFilterConfiguration() {
        // Verificar si los filtros están habilitados
        const areFiltersEnabled = document.getElementById('use-filters')?.checked || false;
        
        if (!areFiltersEnabled) {
            return { enabled: false, filters: [] };
        }
        
        // Recopilar filtros configurados
        const filters = [];
        document.querySelectorAll('.filter-item').forEach(item => {
            const field = item.querySelector('select[name="filter_field[]"]')?.value;
            const operation = item.querySelector('select[name="filter_operation[]"]')?.value;
            const value = item.querySelector('input[name="filter_value[]"]')?.value;
            
            if (field && operation) {
                filters.push({ field, operation, value });
            }
        });
        
        return {
            enabled: true,
            filters: filters
        };
    }
    
    /**
     * Obtiene la configuración de exportación
     */
    function getExportConfiguration() {
        // Verificar si la exportación está habilitada
        const isExportEnabled = document.getElementById('export-results')?.checked || false;
        
        if (!isExportEnabled) {
            return { enabled: false };
        }
        
        return {
            enabled: true,
            format: document.querySelector('select[name="export_format"]')?.value || 'csv',
            destination: document.querySelector('select[name="export_destination"]')?.value || 'local',
            filename: document.querySelector('input[name="export_filename"]')?.value || ''
        };
    }
    
    /**
     * Obtiene la configuración de notificaciones
     */
    function getNotificationConfiguration() {
        // Verificar si las notificaciones están habilitadas
        const areNotificationsEnabled = document.getElementById('notify-completion')?.checked || false;
        
        if (!areNotificationsEnabled) {
            return { enabled: false };
        }
        
        return {
            enabled: true,
            method: document.querySelector('select[name="notification_method"]')?.value || 'email',
            recipient: document.querySelector('input[name="notification_recipient"]')?.value || ''
        };
    }
    
    /**
     * Muestra los resultados de la extracción
     * @param {Array} results - Resultados de la extracción
     * @param {number} count - Cantidad de elementos encontrados
     */
    function displayExtractionResults(results, count) {
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return;
        
        if (!results || !results.length) {
            previewContent.innerHTML = `
                <div class="text-center">
                    <p class="text-yellow-600">La extracción no encontró resultados.</p>
                    <p class="text-gray-500 mt-2">Revise los selectores y la URL configurada.</p>
                </div>`;
            return;
        }
        
        // Obtener los nombres de los campos de los resultados
        const fields = Object.keys(results[0]);
        
        // Crear tabla de resultados
        let html = `
            <div class="text-sm">
                <p class="text-green-600 mb-2">✓ Extracción exitosa: ${count} elementos encontrados</p>
                <div class="overflow-x-auto">
                    <table class="min-w-full">
                        <thead class="bg-gray-100">
                            <tr>`;
        
        // Cabeceras de tabla
        fields.forEach(field => {
            html += `<th class="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">${field}</th>`;
        });
        
        html += `</tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">`;
        
        // Filas de datos
        results.forEach(item => {
            html += `<tr>`;
            fields.forEach(field => {
                const value = item[field];
                let displayValue;
                
                if (Array.isArray(value)) {
                    // Para valores tipo lista, mostrar cantidad y primer elemento
                    displayValue = `[${value.length}] ${value[0] || ''}...`;
                } else if (typeof value === 'object' && value !== null) {
                    displayValue = JSON.stringify(value).substr(0, 100);
                } else {
                    displayValue = value || '';
                }
                
                html += `<td class="px-4 py-2 whitespace-nowrap overflow-hidden text-ellipsis" 
                          style="max-width: 200px;" title="${displayValue}">${displayValue}</td>`;
            });
            html += `</tr>`;
        });
        
        html += `</tbody>
                </table>
            </div>`;
        
        previewContent.innerHTML = html;
    }
    
    /**
     * Muestra un mensaje de error en la extracción
     * @param {string} message - Mensaje de error a mostrar
     */
    function showExtractionError(message) {
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return;
        
        previewContent.innerHTML = `
            <div class="bg-red-50 p-4 rounded-md">
                <p class="text-red-600 font-medium">Error en la extracción</p>
                <p class="text-red-500 mt-1">${message}</p>
                <p class="text-gray-500 mt-2">Revise la configuración e intente nuevamente.</p>
            </div>`;
    }
    
    /**
     * Muestra un mensaje de éxito
     * @param {string} message - Mensaje a mostrar
     */
    function showSuccessMessage(message) {
        const alertContainer = document.getElementById('alert-container') || createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = 'bg-green-100 border-l-4 border-green-500 text-green-700 p-4 mb-4';
        alert.innerHTML = `<p>${message}</p>`;
        
        alertContainer.appendChild(alert);
        
        // Auto-eliminar después de unos segundos
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    /**
     * Muestra un mensaje de error
     * @param {string} message - Mensaje a mostrar
     */
    function showErrorMessage(message) {
        const alertContainer = document.getElementById('alert-container') || createAlertContainer();
        
        const alert = document.createElement('div');
        alert.className = 'bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-4';
        alert.innerHTML = `<p>${message}</p>`;
        
        alertContainer.appendChild(alert);
        
        // Auto-eliminar después de unos segundos
        setTimeout(() => {
            alert.remove();
        }, 5000);
    }
    
    /**
     * Crea un contenedor para alertas si no existe
     * @returns {HTMLElement} - Contenedor para alertas
     */
    function createAlertContainer() {
        const container = document.createElement('div');
        container.id = 'alert-container';
        container.className = 'fixed top-4 right-4 z-50 w-80';
        document.body.appendChild(container);
        return container;
    }
    
    /**
     * Actualiza el estado de un botón
     * @param {HTMLElement} button - Botón a actualizar
     * @param {boolean} disabled - Si el botón debe estar deshabilitado
     * @param {string} text - Texto a mostrar en el botón
     * @param {string[]} classesToAdd - Clases a añadir
     * @param {string[]} classesToRemove - Clases a quitar
     */
    function updateButtonState(button, disabled, text, classesToAdd = [], classesToRemove = []) {
        if (!button) return;
        
        button.disabled = disabled;
        button.textContent = text;
        
        if (classesToAdd.length) button.classList.add(...classesToAdd);
        if (classesToRemove.length) button.classList.remove(...classesToRemove);
    }

    /**
     * Muestra un indicador de carga en el contenedor de resultados
     */
    function showLoadingIndicator() {
        const previewContent = document.getElementById('preview-content');
        if (!previewContent) return;
        
        previewContent.innerHTML = `
            <div class="flex flex-col items-center justify-center py-12">
                <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-500 mb-4"></div>
                <p class="text-gray-600">Verificando acceso a la URL y extrayendo datos...</p>
            </div>`;
    }
    
    function updateSummary() {
        // Referencias a elementos del resumen CORREGIDAS
        const summary = {
            name: document.getElementById('summary-name'),
            url: document.getElementById('summary-url'),
            technology: document.getElementById('summary-tech'),       // Cambio: summary-technology → summary-tech
            selectors: document.getElementById('summary-fields'),      // Cambio: summary-selectors → summary-fields
            pagination: document.getElementById('summary-pagination'),
            proxy: document.getElementById('summary-proxy'),
            schedule: document.getElementById('summary-schedule'),
            export: document.getElementById('summary-export'),
            notifications: document.getElementById('summary-notifications')
        };
        
        // Obtener la configuración actual
        const config = collectScraperConfig();

        // Verificar y corregir valores críticos
        config.name = document.getElementById('scraper-name')?.value?.trim() || 'Sin nombre';
        
        // Para depuración
        debugScraperConfig(config);
        
        // Actualizar nombre y URL con verificación adicional
        if (summary.name) summary.name.textContent = config.name;
        if (summary.url) summary.url.textContent = config.url || 'No definida';
        
        
        // Actualizar nombre y URL
        if (summary.name) summary.name.textContent = document.getElementById('scraper-name')?.value || 'Sin nombre';
        if (summary.url) summary.url.textContent = config.url || 'No definida';
        
        // Actualizar tecnología
        if (summary.technology) {
            const techNames = {
                'beautifulsoup': 'Beautiful Soup (Python)',
                'selenium': 'Selenium (Python)',
                'puppeteer': 'Puppeteer (Node.js)',
                'scrapy': 'Scrapy (Python)',
                'cheerio': 'Cheerio (Node.js)'
            };
            summary.technology.textContent = techNames[config.technology] || config.technology;
        }
        
        // Actualizar selectores
        if (summary.selectors && config.selectors.length) {
            let selectorsHTML = '<ul class="list-disc pl-5">';
            config.selectors.forEach(selector => {
                const multiplicity = selector.multiple ? 'múltiple' : 'único';
                const attrText = selector.attribute ? ` [atributo: ${selector.attribute}]` : '';
                selectorsHTML += `<li><span class="font-medium">${selector.name}:</span> ${selector.path} (${selector.type}, ${multiplicity}${attrText})</li>`;
            });
            selectorsHTML += '</ul>';
            summary.selectors.innerHTML = selectorsHTML;
        }
        
        // Actualizar paginación
        if (summary.pagination) {
            if (config.pagination.enabled) {
                let paginationText = '';
                switch (config.pagination.type) {
                    case 'link':
                        paginationText = `Enlaces (selector: ${config.pagination.next_selector}), máx. ${config.pagination.max_pages} páginas`;
                        break;
                    case 'parameter':
                        paginationText = `Parámetro URL (${config.pagination.page_parameter}), máx. ${config.pagination.max_pages} páginas`;
                        break;
                    case 'infinite':
                        paginationText = `Carga infinita (selector: ${config.pagination.load_more_selector}), máx. ${config.pagination.max_pages} cargas`;
                        break;
                }
                summary.pagination.innerHTML = paginationText;
            } else {
                summary.pagination.textContent = 'No habilitada';
            }
        }
        
        // Actualizar proxy
        if (summary.proxy) {
            if (config.proxy.enabled) {
                summary.proxy.textContent = `${config.proxy.proxy_type.toUpperCase()}: ${config.proxy.address}`;
            } else {
                summary.proxy.textContent = 'No habilitado';
            }
        }
        
        // Actualizar programación
        const scheduleConfig = getScheduleConfiguration();
        if (summary.schedule) {
            if (scheduleConfig.enabled) {
                let scheduleText = '';
                switch (scheduleConfig.frequency) {
                    case 'once':
                        scheduleText = `Una vez: ${scheduleConfig.datetime || 'No definido'}`;
                        break;
                    case 'daily':
                        scheduleText = 'Diariamente';
                        break;
                    case 'weekly':
                        scheduleText = 'Semanalmente';
                        break;
                    case 'custom':
                        scheduleText = `Personalizado: ${scheduleConfig.cron_expression || 'No definido'}`;
                        break;
                }
                summary.schedule.textContent = scheduleText;
            } else {
                summary.schedule.textContent = 'Ejecución manual';
            }
        }
        
        // Actualizar exportación
        const exportConfig = getExportConfiguration();
        if (summary.export) {
            if (exportConfig.enabled) {
                const destinations = {
                    'local': 'Local',
                    'email': 'Correo electrónico',
                    'ftp': 'Servidor FTP',
                    'api': 'API externa'
                };
                const destination = destinations[exportConfig.destination] || exportConfig.destination;
                summary.export.textContent = `${exportConfig.format.toUpperCase()} → ${destination}`;
                
                if (exportConfig.filename) {
                    summary.export.textContent += ` (${exportConfig.filename})`;
                }
            } else {
                summary.export.textContent = 'Base de datos local';
            }
        }
        
        // Actualizar notificaciones
        const notificationConfig = getNotificationConfiguration();
        if (summary.notifications) {
            if (notificationConfig.enabled) {
                const methods = {
                    'email': 'Correo electrónico',
                    'slack': 'Slack',
                    'webhook': 'Webhook'
                };
                const method = methods[notificationConfig.method] || notificationConfig.method;
                summary.notifications.textContent = `${method}: ${notificationConfig.recipient || 'No definido'}`;
            } else {
                summary.notifications.textContent = 'No habilitadas';
            }
        }
    }
    
/**
 * Valida todos los campos necesarios antes de enviar la configuración
 * @returns {boolean} True si la configuración es válida
 */
function validateScraperConfig() {
    // Validación básica de URL
    const urlInput = document.getElementById('scraper-url');
    const url = urlInput?.value?.trim() || '';
    
    if (!url) {
        showErrorMessage('La URL de destino es obligatoria');
        urlInput?.focus();
        return false;
    }
    
    try {
        new URL(url);
    } catch (e) {
        showErrorMessage('La URL de destino no tiene un formato válido');
        urlInput?.focus();
        return false;
    }
    
    // Validar nombre del scraper
    const nameInput = document.getElementById('scraper-name');
    const name = nameInput?.value?.trim() || '';
    
    if (!name) {
        showErrorMessage('El nombre del scraper es obligatorio');
        nameInput?.focus();
        return false;
    }
    
    // Validar selectores
    let hasValidSelectors = false;
    document.querySelectorAll('.selector-item').forEach(item => {
        const name = item.querySelector('input[name="selector_name[]"]')?.value?.trim();
        const path = item.querySelector('input[name="selector_path[]"]')?.value?.trim();
        
        if (name && path) {
            hasValidSelectors = true;
        }
    });
    
    if (!hasValidSelectors) {
        showErrorMessage('Debe configurar al menos un selector válido');
        const firstSelectorName = document.querySelector('input[name="selector_name[]"]');
        firstSelectorName?.focus();
        return false;
    }
        
        if (!hasValidSelectors) {
            showErrorMessage('Debe configurar al menos un selector válido');
            return false;
        }
        
        // Validar configuración de proxy
        if (document.getElementById('use-proxy')?.checked) {
            const proxyAddress = document.querySelector('input[name="proxy_address"]')?.value?.trim();
            if (!proxyAddress) {
                showErrorMessage('Ha habilitado el proxy pero no ha proporcionado una dirección');
                return false;
            }
        }
        
        // Validar configuración de programación
        if (document.getElementById('schedule-scraper')?.checked) {
            const frequency = document.getElementById('schedule-frequency')?.value;
            
            if (frequency === 'once') {
                const datetime = document.querySelector('input[name="schedule_datetime"]')?.value;
                if (!datetime) {
                    showErrorMessage('Debe especificar la fecha y hora para la ejecución programada');
                    return false;
                }
            } else if (frequency === 'custom') {
                const cronExpression = document.querySelector('input[name="schedule_cron"]')?.value?.trim();
                if (!cronExpression) {
                    showErrorMessage('Debe especificar una expresión cron para la programación personalizada');
                    return false;
                }
            }
        }
        
        return true;
    }
    /**
     * Función de ayuda para depuración
     * @param {Object} config - Configuración a verificar
     */
    function debugScraperConfig(config) {
        console.group('Depuración de ScraperConfig');
        console.log('URL:', config.url || 'NO DEFINIDA');
        console.log('Nombre:', config.name || 'NO DEFINIDO');
        console.log('Tecnología:', config.technology);
        console.log('Selectores:', config.selectors.length ? config.selectors : 'NINGUNO');
        console.log('Configuración completa:', config);
        console.groupEnd();
        
        // Verificar el estado del DOM para detectar problemas
        const urlInput = document.getElementById('scraper-url');
        const nameInput = document.getElementById('scraper-name');
        
        if (!urlInput) console.error('Elemento target-url no encontrado en el DOM');
        if (!nameInput) console.error('Elemento scraper-name no encontrado en el DOM');
    }

    // Asegurar que el script funciona como IIFE (Immediately Invoked Function Expression)
    })();