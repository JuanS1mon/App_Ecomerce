// ============================================================================
// CONSOLIDACIÓN DE TODOS LOS EVENT LISTENERS DOMContentLoaded
// ============================================================================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 Inicializando aplicación generar.html...');
    
    // ============================
    // 1. FUNCIONALIDAD DE PESTAÑAS
    // ============================
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    function switchTab(tabId) {
        // Ocultar todos los contenidos
        tabContents.forEach(content => {
            content.classList.add('hidden');
            content.classList.remove('block');
        });
        
        // Mostrar el contenido seleccionado
        const targetContent = document.getElementById('content-' + tabId);
        if (targetContent) {
            targetContent.classList.remove('hidden');
            targetContent.classList.add('block');
        }
        
        // Actualizar estilos de los botones
        tabButtons.forEach(btn => {
            btn.classList.remove('border-indigo-500', 'text-gray-700', 'active');
            btn.classList.add('border-transparent', 'text-gray-500');
        });
        
        const activeButton = document.getElementById('tab-' + tabId);
        if (activeButton) {
            activeButton.classList.remove('border-transparent', 'text-gray-500');
            activeButton.classList.add('border-indigo-500', 'text-gray-700', 'active');
        }
    }
    
    // Asignar eventos de clic a los botones de pestañas
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const tabId = this.id.replace('tab-', '');
            switchTab(tabId);
        });
    });
    
    // ============================
    // 2. DETECCIÓN EDITOR VISUAL
    // ============================
    const urlParams = new URLSearchParams(window.location.search);
    const fromEditorVisual = document.referrer && document.referrer.includes('/editor-visual') || 
                               urlParams.get('from') === 'editor-visual';
    
    if (fromEditorVisual) {
        console.log('🎯 Detectado acceso desde Editor Visual - Abriendo Sistema Multi-Tabla');
        switchTab('multi-tabla');
        
        // Cargar automáticamente el JSON desde localStorage
        setTimeout(() => {
            const storedConfig = localStorage.getItem('generator_config');
            console.log('🔍 [DEBUG GENERADOR] storedConfig raw:', storedConfig);
            
            if (storedConfig) {
                try {
                    const config = JSON.parse(storedConfig);
                    console.log('🔍 [DEBUG GENERADOR] config parseado:', config);
                    console.log('🔍 [DEBUG GENERADOR] service_name:', config.service_name);
                    console.log('🔍 [DEBUG GENERADOR] número de tablas:', config.tables?.length);
                    
                    const jsonTextarea = document.getElementById('json-config');
                    if (jsonTextarea) {
                        jsonTextarea.value = JSON.stringify(config, null, 2);
                        console.log('✅ JSON cargado automáticamente desde Editor Visual:', config.service_name);
                        
                        // Mostrar feedback visual
                        const feedbackDiv = document.createElement('div');
                        feedbackDiv.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4';
                        feedbackDiv.innerHTML = `
                            <div class="flex items-center">
                                <i class="fas fa-check-circle mr-2"></i>
                                <span><strong>¡JSON cargado automáticamente!</strong></span>
                            </div>
                            <div class="text-sm mt-1">
                                Proyecto: ${config.service_name || 'Sin nombre'} | 
                                Tablas: ${config.tables ? config.tables.length : 0} | 
                                Relaciones: ${config.relationships ? config.relationships.length : 0}
                            </div>
                        `;
                        
                        // Insertar el feedback antes del textarea
                        jsonTextarea.parentNode.insertBefore(feedbackDiv, jsonTextarea);
                        
                        // Limpiar el feedback después de 5 segundos
                        setTimeout(() => {
                            if (feedbackDiv.parentNode) {
                                feedbackDiv.remove();
                            }
                        }, 5000);
                    }
                } catch (error) {
                    console.error('❌ Error al cargar JSON desde Editor Visual:', error);
                }
            } else {
                console.warn('⚠️ No se encontró configuración en localStorage desde Editor Visual');
            }
            
            // Abrir automáticamente la sección de Configurar JSON
            const jsonConfigSection = document.getElementById('json-config-section');
            if (jsonConfigSection) {
                // Expandir la sección de configurar JSON
                jsonConfigSection.classList.remove('hidden');
                jsonConfigSection.classList.add('block');
                
                // Hacer scroll suave hacia la sección
                jsonConfigSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
                
                console.log('✅ Sección JSON Config abierta automáticamente');
            } else {
                console.warn('⚠️ No se encontró la sección json-config-section');
            }
        }, 200);
    } else {
        // Inicializar en Sistema Multi-Tabla por defecto (sistema simple obsoleto)
        switchTab('multi-tabla');
    }
    
    // ============================
    // 3. AGREGAR PRIMER CAMPO
    // ============================
    if (document.getElementById('add_field')) {
        document.getElementById('add_field').click();
    }
    
    // ============================
    // 4. FUNCIONALIDAD BOTONES
    // ============================
    
    // Botón "Cargar Ejemplo"
    const btnCargarEjemplo = document.getElementById('btn-cargar-ejemplo');
    if (btnCargarEjemplo) {
        btnCargarEjemplo.addEventListener('click', function() {
            fetch('/generar/multi-table-example')
                .then(response => response.json())
                .then(data => {
                    const jsonTextarea = document.getElementById('json-config');
                    if (jsonTextarea && data.example) {
                        jsonTextarea.value = JSON.stringify(data.example, null, 2);
                        console.log('✅ Ejemplo cargado correctamente');
                    }
                })
                .catch(error => {
                    console.error('❌ Error al cargar ejemplo:', error);
                });
        });
    }
    
    // Botón "Validar JSON"
    const btnValidarJSON = document.getElementById('btn-validar-json');
    if (btnValidarJSON) {
        btnValidarJSON.addEventListener('click', function() {
            const jsonTextarea = document.getElementById('json-config');
            const resultDiv = document.getElementById('json-validation-result');
            
            if (!jsonTextarea || !resultDiv) return;
            
            try {
                const jsonText = jsonTextarea.value.trim();
                if (!jsonText) {
                    throw new Error('El campo JSON está vacío');
                }
                
                const parsed = JSON.parse(jsonText);
                
                // Validaciones básicas
                if (!parsed.service_name) throw new Error('Falta service_name');
                if (!parsed.tables || !Array.isArray(parsed.tables)) throw new Error('Falta array de tables');
                if (parsed.tables.length === 0) throw new Error('No hay tablas definidas');
                
                resultDiv.className = 'bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4';
                resultDiv.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-check-circle mr-2"></i>
                        <span><strong>✅ JSON válido</strong></span>
                    </div>
                    <div class="text-sm mt-1">
                        Servicio: ${parsed.service_name} | Tablas: ${parsed.tables.length} | 
                        Relaciones: ${parsed.relationships ? parsed.relationships.length : 0}
                    </div>
                `;
                resultDiv.classList.remove('hidden');
                
                console.log('✅ JSON validado correctamente:', parsed);
                
            } catch (error) {
                resultDiv.className = 'bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4';
                resultDiv.innerHTML = `
                    <div class="flex items-center">
                        <i class="fas fa-exclamation-triangle mr-2"></i>
                        <span><strong>❌ JSON inválido</strong></span>
                    </div>
                    <div class="text-sm mt-1">${error.message}</div>
                `;
                resultDiv.classList.remove('hidden');
                
                console.error('❌ Error en validación JSON:', error);
            }
        });
    }
    
    // Botón "Exportar JSON"
    const btnExportarJSON = document.getElementById('btn-exportar-json');
    if (btnExportarJSON) {
        btnExportarJSON.addEventListener('click', function() {
            const jsonTextarea = document.getElementById('json-config');
            if (!jsonTextarea) return;
            
            try {
                const jsonText = jsonTextarea.value.trim();
                if (!jsonText) {
                    alert('No hay JSON para exportar');
                    return;
                }
                
                // Validar que sea JSON válido
                const parsed = JSON.parse(jsonText);
                const fileName = (parsed.service_name || 'configuracion') + '.json';
                
                // Crear blob y descargar
                const blob = new Blob([jsonText], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = fileName;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                console.log(`✅ JSON exportado como: ${fileName}`);
                
            } catch (error) {
                alert('Error: JSON inválido para exportar');
                console.error('❌ Error al exportar JSON:', error);
            }
        });
    }
    
    // ============================
    // 5. CARGAR JSON EXISTENTE  
    // ============================
    
    // JSON cargado automáticamente desde 'generator_config' en el bloque fromEditorVisual arriba
    console.log('✅ Bloque de carga de JSON existente ya manejado por detección de Editor Visual');
    
    // ============================
    // 6. VALIDACIONES DE FORMULARIO
    // ============================
    
    // Asegurar que module_name tenga valor
    const moduleNameInput = document.getElementById('module_name');
    if (moduleNameInput && !moduleNameInput.value.trim()) {
        moduleNameInput.value = 'mi_modulo_generado';
        console.log('⚠️ Campo "module_name" estaba vacío. Se asignó un valor predeterminado.');
    }
    
    // Generar campos dinámicos desde JSON si existe
    const jsonTextarea = document.getElementById('json-config');
    if (jsonTextarea && jsonTextarea.value.trim()) {
        generateFieldsFromJson(jsonTextarea.value);
        console.log('✅ Campos generados dinámicamente desde el JSON.');
    }
    
    // ============================
    // 7. CONFIGURAR EDITOR VISUAL
    // ============================
    // Configuración manejada por script separado para evitar interferencias
    console.log('✅ Editor Visual configurado correctamente');
    
    console.log('🎉 Inicialización completa de generar.html');
});

// ============================
// FUNCIONES AUXILIARES DE PESTAÑAS
// ============================
function updateActiveButton(activeTabId) {
    const tabButtons = document.querySelectorAll('[id^="tab-"]');
    tabButtons.forEach(btn => {
        btn.classList.remove('border-indigo-500', 'text-gray-700', 'active');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    const activeButton = document.getElementById(`tab-${activeTabId}`);
    if (activeButton) {
        activeButton.classList.remove('border-transparent', 'text-gray-500');
        activeButton.classList.add('border-indigo-500', 'text-gray-700', 'active');
    }
}

// ============================
// ASIGNAR EVENTOS DE PESTAÑAS
// ============================
// Asignar eventos de clic a los botones de pestañas
const tabButtons = document.querySelectorAll('[id^="tab-"]');
tabButtons.forEach(button => {
    button.addEventListener('click', function() {
        const tabId = this.id.replace('tab-', '');
        switchTab(tabId);
    });
});
    
    // Agregar el primer campo automáticamente
    if (document.getElementById('add_field')) {
        document.getElementById('add_field').click();
    }
    
    // ============================
    // FUNCIONALIDAD AGREGAR CAMPOS
    // ============================
    // Función para agregar campos dinámicamente
    document.getElementById('add_field').addEventListener('click', function() {
        const fieldsCount = document.querySelectorAll('#fields > div').length;
        const fieldNumber = fieldsCount + 1;
    
    const div = document.createElement('div');
    div.className = 'field-container flex items-center space-x-3 p-3 border border-gray-200 rounded-lg bg-white';
    
    // Icono del campo
    const iconDiv = document.createElement('div');
    iconDiv.className = 'flex-shrink-0 h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-600';
    iconDiv.innerHTML = '<i class="fas fa-database"></i>';
    div.appendChild(iconDiv);
    
    // Contenedor para inputs
    const inputsContainer = document.createElement('div');
    inputsContainer.className = 'flex-grow grid grid-cols-1 sm:grid-cols-2 gap-3';
    
    // Input para nombre
    const nameContainer = document.createElement('div');
    
    const input = document.createElement('input');
    input.type = 'text';
    input.name = 'field_names[]';
    input.placeholder = fieldNumber === 1 ? 'Campo principal (obligatorio)' : 'Nombre del campo';
    input.className = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500';
    if (fieldNumber === 1) {
        input.classList.add('border-yellow-500');
    }
    
    nameContainer.appendChild(input);
    inputsContainer.appendChild(nameContainer);
    
    // Select para tipo
    const typeContainer = document.createElement('div');
    
    const select = document.createElement('select');
    select.name = 'field_types[]';
    select.className = 'w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500';
    
    const opcionTipos = ['str', 'int', 'float', 'bool'];
    opcionTipos.forEach(function(tipo) {
        const option = document.createElement('option');
        option.value = tipo;
        option.text = tipo;
        select.appendChild(option);
    });
    
    typeContainer.appendChild(select);
    inputsContainer.appendChild(typeContainer);
    div.appendChild(inputsContainer);
    
    // Botón para eliminar
    const button = document.createElement('button');
    button.type = 'button';
    button.className = 'flex-shrink-0 bg-red-500 hover:bg-red-600 text-white p-2 rounded-full focus:outline-none transition-colors';
    button.innerHTML = '<i class="fas fa-trash"></i>';
    button.title = 'Quitar campo';
    div.appendChild(button);
    
    document.getElementById('fields').appendChild(div);
    input.focus();
    
    // Marcar el primer campo como especial
    if (fieldNumber === 1) {
        div.classList.add('border-yellow-300', 'bg-yellow-50');
    }
});

// ============================
// FUNCIONES DE GESTIÓN DE CAMPOS
// ============================
// Eliminar campos
document.addEventListener('click', function(e) {
    if (e.target && e.target.closest('button') && e.target.closest('button').innerHTML.includes('fa-trash')) {
        e.target.closest('.field-container').remove();
    }
});

// ============================
// CONFIGURAR BOTÓN GENERAR SISTEMA
// ============================
// Asegurar existencia del botón "Generar Sistema"
const btnGenerateSystem = document.getElementById('btn-generate-multi-table');
if (!btnGenerateSystem) {
    console.warn('⚠️ El botón "Generar Sistema" no se encontró en el DOM.');
} else {
    console.log('✅ Botón "Generar Sistema" encontrado y listo para usar.');
    
    // Agregar funcionalidad específica al botón multi-tabla
    btnGenerateSystem.addEventListener('click', function(event) {
        event.preventDefault();
        sendMultiTableJSON();
    });
}

// ============================
// CONFIGURAR VALIDACIÓN JSON
// ============================
// Reparar funcionalidad de Validar JSON - mostrar resultado visual
const btnValidateJson = document.getElementById('btn-validate-json');
const jsonTextarea = document.getElementById('json-config');
const resultDiv = document.getElementById('json-validation-result');

if (btnValidateJson) {
    btnValidateJson.addEventListener('click', function(event) {
        event.preventDefault();
        
        if (!resultDiv) {
            console.error('❌ Div de resultados no encontrado');
            return;
        }

            try {
                const jsonData = JSON.parse(jsonTextarea.value);
                const requiredFields = ['service_name', 'description', 'tables'];
                const missingFields = requiredFields.filter(field => !jsonData[field]);

                if (missingFields.length > 0) {
                    showValidationResult('error', `❌ Campos requeridos faltantes: ${missingFields.join(', ')}`);
                    return;
                }

                if (!Array.isArray(jsonData.tables) || jsonData.tables.length === 0) {
                    showValidationResult('error', '❌ Debe definir al menos una tabla.');
                    return;
                }

                // Validar cada tabla
                for (let i = 0; i < jsonData.tables.length; i++) {
                    const table = jsonData.tables[i];
                    if (!table.name) {
                        showValidationResult('error', `❌ La tabla ${i + 1} no tiene nombre.`);
                        return;
                    }
                    if (!table.fields || !Array.isArray(table.fields) || table.fields.length === 0) {
                        showValidationResult('error', `❌ La tabla "${table.name}" no tiene campos definidos.`);
                        return;
                    }
                }

                showValidationResult('success', `✅ JSON válido - ${jsonData.tables.length} tabla(s) detectada(s) - Listo para generar.`);
            } catch (error) {
                showValidationResult('error', `❌ Error de sintaxis JSON: ${error.message}`);
            }
        });
    } else {
        console.warn('⚠️ El botón "Validar JSON" no se encontró en el DOM.');
    }

    // Función auxiliar para mostrar resultados de validación
    function showValidationResult(type, message) {
        const resultDiv = document.getElementById('json-validation-result');
        if (!resultDiv) return;
        
        resultDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'border-green-300', 'bg-red-100', 'text-red-700', 'border-red-300');
        
        if (type === 'success') {
            resultDiv.classList.add('bg-green-100', 'text-green-700', 'border', 'border-green-300');
        } else {
            resultDiv.classList.add('bg-red-100', 'text-red-700', 'border', 'border-red-300');
        }
        
        resultDiv.innerHTML = `<i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-triangle'} mr-2"></i>${message}`;
        resultDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

// ============================
// CONFIGURAR BOTÓN CARGAR EJEMPLO
// ============================
// Funcionalidad del botón "Cargar Ejemplo"
const btnLoadExample = document.getElementById('btn-load-example');

if (btnLoadExample) {
    btnLoadExample.addEventListener('click', function(event) {
        event.preventDefault();
            
            const exampleJson = {
                "service_name": "sistema_ejemplo",
                "description": "Sistema de ejemplo con usuarios y productos",
                "tables": [
                    {
                        "name": "usuarios",
                        "fields": [
                            {
                                "name": "id",
                                "field_type": "integer",
                                "primary_key": true,
                                "auto_increment": true
                            },
                            {
                                "name": "nombre",
                                "field_type": "string",
                                "max_length": 100,
                                "nullable": false
                            },
                            {
                                "name": "email",
                                "field_type": "string",
                                "max_length": 150,
                                "nullable": false,
                                "unique": true
                            },
                            {
                                "name": "fecha_registro",
                                "field_type": "datetime",
                                "default": "now"
                            }
                        ]
                    },
                    {
                        "name": "productos",
                        "fields": [
                            {
                                "name": "id",
                                "field_type": "integer",
                                "primary_key": true,
                                "auto_increment": true
                            },
                            {
                                "name": "nombre",
                                "field_type": "string",
                                "max_length": 200,
                                "nullable": false
                            },
                            {
                                "name": "precio",
                                "field_type": "decimal",
                                "precision": 10,
                                "scale": 2
                            },
                            {
                                "name": "usuario_id",
                                "field_type": "integer",
                                "foreign_key": {
                                    "table": "usuarios",
                                    "field": "id"
                                }
                            }
                        ]
                    }
                ],
                "relationships": [
                    {
                        "from_table": "productos",
                        "from_field": "usuario_id",
                        "to_table": "usuarios",
                        "to_field": "id",
                        "relationship_type": "many_to_one"
                    }
                ],
                "generate_crud_for_all": true
            };

            jsonTextarea.value = JSON.stringify(exampleJson, null, 2);
            
            // Limpiar resultado de validación anterior
            const resultDiv = document.getElementById('json-validation-result');
            if (resultDiv) {
                resultDiv.classList.add('hidden');
            }
            
            console.log('✅ Ejemplo cargado correctamente');
        });
    } else {
        console.warn('⚠️ El botón "Cargar Ejemplo" no se encontró en el DOM.');
    }

// ============================
// CONFIGURAR BOTÓN EXPORTAR JSON
// ============================
// Funcionalidad del botón "Exportar JSON"
const btnExportJson = document.getElementById('btn-export-json');

if (btnExportJson) {
    btnExportJson.addEventListener('click', function(event) {
            event.preventDefault();
            
            try {
                // Validar que el JSON sea válido antes de exportar
                const jsonData = JSON.parse(jsonTextarea.value);
                
                // Crear el archivo para descarga
                const dataStr = JSON.stringify(jsonData, null, 2);
                const dataBlob = new Blob([dataStr], {type: 'application/json'});
                
                // Crear elemento de descarga
                const downloadLink = document.createElement('a');
                downloadLink.href = URL.createObjectURL(dataBlob);
                
                // Usar el service_name del JSON como nombre del archivo, o un nombre por defecto
                const fileName = jsonData.service_name ? `${jsonData.service_name}.json` : 'configuracion_sistema.json';
                downloadLink.download = fileName;
                
                // Agregar al DOM, hacer clic y remover
                document.body.appendChild(downloadLink);
                downloadLink.click();
                document.body.removeChild(downloadLink);
                
                // Limpiar la URL del objeto
                URL.revokeObjectURL(downloadLink.href);
                
                console.log(`✅ JSON exportado como: ${fileName}`);
                
                // Mostrar confirmación visual
                const resultDiv = document.getElementById('json-validation-result');
                if (resultDiv) {
                    resultDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'border-green-300', 'bg-red-100', 'text-red-700', 'border-red-300');
                    resultDiv.classList.add('bg-blue-100', 'text-blue-700', 'border', 'border-blue-300');
                    resultDiv.innerHTML = `<i class="fas fa-download mr-2"></i>✅ JSON exportado como: ${fileName}`;
                    
                    // Auto-ocultar después de 3 segundos
                    setTimeout(() => {
                        resultDiv.classList.add('hidden');
                    }, 3000);
                }
                
            } catch (error) {
                console.error('❌ Error al exportar JSON:', error);
                
                // Mostrar error
                const resultDiv = document.getElementById('json-validation-result');
                if (resultDiv) {
                    resultDiv.classList.remove('hidden', 'bg-green-100', 'text-green-700', 'border-green-300', 'bg-blue-100', 'text-blue-700', 'border-blue-300');
                    resultDiv.classList.add('bg-red-100', 'text-red-700', 'border', 'border-red-300');
                    resultDiv.innerHTML = `<i class="fas fa-exclamation-triangle mr-2"></i>❌ Error: JSON inválido. Corrija la sintaxis antes de exportar.`;
                }
            }
        });
    } else {
        console.warn('⚠️ El botón "Exportar JSON" no se encontró en el DOM.');
    }

// ============================
// CONFIGURAR GENERACIÓN DE SISTEMA
// ============================
// Reparar funcionalidad de Generar Sistema - Ya configurado arriba, evitar duplicado
console.log('✅ Todas las funcionalidades configuradas correctamente');

// ============================
// FUNCIONES AUXILIARES GLOBALES 
// ============================

// Validación del formulario tradicional (solo para generación simple)
function validateTraditionalForm(event) {
    const jsonTextarea = document.getElementById('json-config');
    
    // Si hay JSON válido, usar el flujo multi-tabla (sin validación de checkboxes)
    if (jsonTextarea && jsonTextarea.value.trim()) {
        try {
            JSON.parse(jsonTextarea.value);
            return true; // JSON válido, permitir envío multi-tabla
        } catch (e) {
            // JSON inválido, continuar con validación tradicional
        }
    }

    const moduleName = document.getElementById('module_name');
    if (!moduleName || !moduleName.value.trim()) {
        event.preventDefault();
        alert('Por favor, ingrese un nombre para el módulo.');
        if (moduleName) moduleName.focus();
        return false;
    }

    const fields = document.querySelectorAll('#fields > div');
    if (fields.length < 1) {
        event.preventDefault();
        alert('Por favor, añada al menos un campo.');
        return false;
    }

    const inputs = document.querySelectorAll('input[name="field_names[]"]');
    for (let input of inputs) {
        if (!input.value.trim()) {
            event.preventDefault();
            alert('Por favor, complete todos los nombres de los campos.');
            input.focus();
            return false;
        }
    }

    const checkboxes = document.querySelectorAll('input[type="checkbox"]');
    const anyChecked = Array.from(checkboxes).some(cb => cb.checked);
    if (!anyChecked) {
        event.preventDefault();
        alert('Por favor, seleccione al menos una opción de generación.');
        return false;
    }
    
    return true;
}

// ============================
// SCRIPT PRINCIPAL FINALIZADO CORRECTAMENTE
// ============================

// ============ FUNCIONES PARA CELEBRACIÓN ============

function showLoadingSpinner() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.add('active');
}

function hideLoadingSpinner() {
    const overlay = document.getElementById('loading-overlay');
    overlay.classList.remove('active');
}

function showCelebration() {
    const modal = document.getElementById('celebration-modal');
    modal.classList.add('active');
    
    // Efecto de sonido (opcional, comentado por compatibilidad)
    // const audio = new Audio('data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmQcBz2a3O/GdSMFl3DJ8d2QPgkTXrDp8qlVEQtGmN3xvGMcBy');
    // audio.play().catch(() => {}); // Ignorar errores de audio
}

function closeCelebration() {
    const modal = document.getElementById('celebration-modal');
    modal.classList.remove('active');
}

// Función para enviar JSON multi-tabla
function sendMultiTableJSON() {
    const jsonTextarea = document.getElementById('json-config');
    let jsonData;

    try {
        jsonData = JSON.parse(jsonTextarea.value);
    } catch (error) {
        alert(`❌ Error de sintaxis JSON: ${error.message}`);
        return;
    }

    console.log('🚀 Enviando JSON multi-tabla al servidor...');
    
    // Mostrar spinner de carga
    showLoadingSpinner();

    fetch('/generar/generate-multi-table', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(jsonData)
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        } else {
            throw new Error('Error en la generación del sistema.');
        }
    })
    .then(data => {
        console.log('✅ Respuesta del servidor:', data);
        
        // Ocultar spinner
        hideLoadingSpinner();
        
        if (data.success) {
            // Pequeña pausa para suavizar la transición
            setTimeout(() => {
                // Mostrar celebración en lugar del alert básico
                showCelebration();
            }, 300);
            
            // Mostrar detalles de archivos generados si existen
            if (data.generated_files && data.generated_files.length > 0) {
                console.log(`📁 Archivos generados: ${data.generated_files.length}`);
                data.generated_files.forEach(file => console.log(`  - ${file}`));
            }
        } else {
            alert(`❌ Error: ${data.message || 'Error desconocido'}`);
        }
    })
    .catch(error => {
        console.error('❌ Error:', error);
        
        // Ocultar spinner en caso de error
        hideLoadingSpinner();
        
        alert(`❌ ${error.message}`);
    });
}

// Hacer funciones accesibles globalmente para los event handlers del HTML
window.closeCelebration = closeCelebration;

// Manejar envío del formulario - separar flujos tradicional y multi-tabla
const generadorForm = document.getElementById('generador');
if (generadorForm) {
    generadorForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const jsonTextarea = document.getElementById('json-config');
        
        // Si hay JSON válido, usar flujo multi-tabla
        if (jsonTextarea && jsonTextarea.value.trim()) {
            try {
                JSON.parse(jsonTextarea.value);
                sendMultiTableJSON();
                return;
            } catch (e) {
                // JSON inválido, continuar con flujo tradicional
            }
        }

        // Flujo tradicional con validación de checkboxes
        if (validateTraditionalForm(event)) {
            // Enviar formulario tradicional aquí si es necesario
            console.log('📝 Enviando formulario tradicional...');
        }
    });
}

// -----------------------------
// Script separado para el botón Editor Visual - Evitar interferencias (IIFE)
// -----------------------------
(function() {
    'use strict';
    
    // Ejecutar inmediatamente después del DOM
    function setupEditorVisualButton() {
        const btn = document.getElementById('btn-editor-visual-multitable');
        if (!btn) {
            console.warn('Botón Editor Visual no encontrado');
            return;
        }
        
        // Limpiar cualquier listener existente
        const newBtn = btn.cloneNode(true);
        btn.parentNode.replaceChild(newBtn, btn);
        
        // Agregar nuestro listener exclusivo
        newBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            console.log('🚀 Editor Visual - Solo abriendo nueva pestaña');
            window.open('/editor-visual', '_blank');
            
            return false;
        });
        
        console.log('✅ Editor Visual configurado correctamente');
    }
    
    // Ejecutar cuando esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupEditorVisualButton);
    } else {
        setupEditorVisualButton();
    }
    
    // También ejecutar después de un pequeño delay para asegurarse
    setTimeout(setupEditorVisualButton, 100);
})();
