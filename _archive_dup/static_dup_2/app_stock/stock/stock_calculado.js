// Stock Calculado - Aplicación Vue.js
const { createApp, ref, computed, onMounted, watch } = Vue;

createApp({
    setup() {
        // Estados
        const depositos = ref([]);
        const activeTab = ref('consulta');
        const filtros = ref({
            deposito: '',
            articulo: '',
            depositoComp: '',
            articuloComp: '',
            depositoVista: '',
            minDisponible: '',
            articuloVista: '',
            busquedaGlobal: '',
            limitGlobal: 10,
            ordenGlobal: 'disponible_desc',
            paginaGlobal: 1
        });
        
        // Estados para autocompletado
        const sugerenciasArticulos = ref([]);
        const mostrarSugerencias = ref(false);
        const loadingSugerencias = ref(false);
        const campoActivo = ref('');
        const sugerenciasIndices = ref({
            articulo: -1,
            articuloComp: -1,
            articuloVista: -1,
            busquedaGlobal: -1
        });

        const resultadoConsulta = ref(null);
        const resultadoComparacion = ref(null);
        const resultadoDeposito = ref(null);
        const resultadoArticulo = ref(null);
        const resultadoGlobal = ref(null);
        const resumenEjecutivo = ref(null);
        const loading = ref(false);
        const loadingComparacion = ref(false);
        const loadingDeposito = ref(false);
        const loadingArticulo = ref(false);
        const loadingGlobal = ref(false);
        const loadingResumen = ref(false);
        const busquedaRealizada = ref(false);
        const busquedaDepositoRealizada = ref(false);
        const busquedaArticuloRealizada = ref(false);
        const busquedaGlobalRealizada = ref(false);
        let comparisonChart = null;

        // Computed properties
        const porcentajeDisponible = computed(() => {
            if (!resultadoConsulta.value || !resultadoConsulta.value.stock || (resultadoConsulta.value.stock.fisico || 0) <= 0) return 0;
            const porcentaje = ((resultadoConsulta.value.stock.disponible || 0) / (resultadoConsulta.value.stock.fisico || 1)) * 100;
            return Math.min(Math.max(porcentaje, 0), 100); // Limitar entre 0 y 100
        });
        
        const algunaDiferencia = computed(() => {
            if (!resultadoComparacion.value) return false;
            const dif = resultadoComparacion.value.diferencias;
            return dif.fisico !== 0 || dif.reservado !== 0 || dif.preparado !== 0 || 
                   dif.bloqueado !== 0 || dif.disponible !== 0;
        });

        // Computed para páginas disponibles en Vista Global
        const paginasDisponibles = computed(() => {
            if (!resultadoGlobal.value || !resultadoGlobal.value.total) return [];
            const totalPaginas = Math.ceil(resultadoGlobal.value.total / filtros.value.limitGlobal);
            const paginas = [];
            const paginaActual = filtros.value.paginaGlobal;
            
            // Mostrar hasta 5 páginas alrededor de la actual
            const inicio = Math.max(1, paginaActual - 2);
            const fin = Math.min(totalPaginas, paginaActual + 2);
            
            for (let i = inicio; i <= fin; i++) {
                paginas.push(i);
            }
            
            return paginas;
        });
        
        // Computed para información de paginación
        const infoPaginacion = computed(() => {
            if (!resultadoGlobal.value) return '';
            const desde = ((filtros.value.paginaGlobal - 1) * filtros.value.limitGlobal) + 1;
            const hasta = Math.min(filtros.value.paginaGlobal * filtros.value.limitGlobal, resultadoGlobal.value.total);
            return `Mostrando ${desde}-${hasta} de ${resultadoGlobal.value.total} artículos`;
        });

        // Cargar depósitos al iniciar
        onMounted(async () => {
            try {
                // Inicializar con datos de ejemplo primero para evitar errores
                depositos.value = [
                    { id: 1, descripcion: "Depósito Principal" },
                    { id: 2, descripcion: "Depósito Secundario" },
                    { id: 3, descripcion: "Depósito Auxiliar" }
                ];

                // Intentar obtener la lista real de depósitos desde la API
                const response = await fetch('/stock/calculado/depositos');
                if (response.ok) {
                    const data = await response.json();
                    depositos.value = data.map(d => ({
                        id: d.id,
                        descripcion: d.descripcion
                    }));
                    console.log('Depósitos cargados desde API:', depositos.value);
                } else {
                    console.warn('No se pudo cargar depósitos desde API, usando datos de ejemplo');
                }
                
                // Cargar componentes compartidos (navbar, footer)
                if (typeof loadComponents === 'function') {
                    loadComponents();
                }
            } catch (error) {
                console.error('Error al cargar datos iniciales:', error);
                mostrarToast('Error al cargar datos iniciales', 'error');
                
                // Usar datos de ejemplo en caso de error
                depositos.value = [
                    { id: 1, descripcion: "Depósito Principal" },
                    { id: 2, descripcion: "Depósito Secundario" },
                    { id: 3, descripcion: "Depósito Auxiliar" }
                ];
            }
        });
        
        // Métodos para mostrar notificaciones
        function mostrarToast(mensaje, tipo = 'info') {
            const toastContainer = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = `p-4 mb-3 rounded-md shadow-md ${tipo === 'error' ? 'bg-red-500' : 'bg-blue-500'} text-white`;
            toast.innerHTML = `
                <div class="flex items-center">
                    <i class="fas ${tipo === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'} mr-2"></i>
                    <span>${mensaje}</span>
                </div>
            `;
            toastContainer.appendChild(toast);
            
            // Eliminar después de 3 segundos
            setTimeout(() => {
                toast.classList.add('opacity-0');
                setTimeout(() => {
                    toastContainer.removeChild(toast);
                }, 300);
            }, 3000);
        }
        
        // Función para buscar stock individual
        const buscarStockIndividual = async () => {
            if (!filtros.value.deposito || !filtros.value.articulo) {
                mostrarToast('Por favor selecciona un depósito e ingresa un artículo', 'error');
                return;
            }
            
            loading.value = true;
            busquedaRealizada.value = true;
            resultadoConsulta.value = null;
            
            try {
                // Llamar a la API para obtener el stock calculado
                const response = await fetch(`/stock/calculado/deposito/${filtros.value.deposito}/${filtros.value.articulo}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                resultadoConsulta.value = await response.json();
                mostrarToast('Stock calculado con éxito');
            } catch (error) {
                console.error('Error al buscar stock:', error);
                mostrarToast(`Error al calcular el stock: ${error.message}`, 'error');
            } finally {
                loading.value = false;
            }
        };
        
        // Función para comparar stock
        const compararStock = async () => {
            if (!filtros.value.depositoComp || !filtros.value.articuloComp) {
                mostrarToast('Por favor selecciona un depósito e ingresa un artículo', 'error');
                return;
            }
            
            loadingComparacion.value = true;
            resultadoComparacion.value = null;
            
            try {
                // Llamar a la API para obtener la comparación
                const response = await fetch(`/stock/calculado/comparar/${filtros.value.depositoComp}/${filtros.value.articuloComp}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                resultadoComparacion.value = await response.json();
                mostrarToast('Comparación realizada con éxito');
                
                // Dibujar gráfico de comparación
                setTimeout(() => {
                    dibujarGraficoComparacion();
                }, 100);
            } catch (error) {
                console.error('Error al comparar stock:', error);
                mostrarToast(`Error al comparar el stock: ${error.message}`, 'error');
            } finally {
                loadingComparacion.value = false;
            }
        };
        
        // Función para buscar stock por depósito
        const buscarStockDeposito = async () => {
            if (!filtros.value.depositoVista) {
                mostrarToast('Por favor selecciona un depósito', 'error');
                return;
            }
            
            loadingDeposito.value = true;
            busquedaDepositoRealizada.value = true;
            resultadoDeposito.value = null;
            
            try {
                // Construir URL de consulta
                let url = `/stock/calculado/deposito/${filtros.value.depositoVista}`;
                
                // Añadir filtro de disponibilidad mínima si se especificó
                if (filtros.value.minDisponible) {
                    url += `?min_disponible=${filtros.value.minDisponible}`;
                }
                
                // Llamar a la API para obtener el stock del depósito
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                resultadoDeposito.value = await response.json();
                mostrarToast(`Se encontraron ${resultadoDeposito.value.length} artículos en el depósito`);
            } catch (error) {
                console.error('Error al buscar stock por depósito:', error);
                mostrarToast(`Error al calcular el stock del depósito: ${error.message}`, 'error');
            } finally {
                loadingDeposito.value = false;
            }
        };
        
        // Función para buscar stock por artículo
        const buscarStockArticulo = async () => {
            if (!filtros.value.articuloVista) {
                mostrarToast('Por favor ingresa un código de artículo', 'error');
                return;
            }
            
            loadingArticulo.value = true;
            busquedaArticuloRealizada.value = true;
            resultadoArticulo.value = null;
            
            try {
                // Llamar a la API para obtener el stock del artículo en todos los depósitos
                const response = await fetch(`/stock/calculado/articulo/${filtros.value.articuloVista}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                resultadoArticulo.value = await response.json();
                mostrarToast(`Se encontró el artículo en ${resultadoArticulo.value.depositos.length} depósitos`);
            } catch (error) {
                console.error('Error al buscar stock por artículo:', error);
                mostrarToast(`Error al calcular el stock del artículo: ${error.message}`, 'error');
            } finally {
                loadingArticulo.value = false;
            }
        };

        // Función para cargar stock global
        const cargarStockGlobal = async () => {
            loadingGlobal.value = true;
            busquedaGlobalRealizada.value = true;
            resultadoGlobal.value = null;

            try {
                const params = new URLSearchParams();
                params.append('pagina', filtros.value.paginaGlobal.toString());
                params.append('limite', filtros.value.limitGlobal.toString());

                const response = await fetch(`/stock/calculado/global?${params.toString()}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }

                const data = await response.json();
                console.log('Respuesta de la API:', data);

                // Validar estructura de la respuesta
                if (!data || !Array.isArray(data.articulos) || typeof data.total !== 'number') {
                    throw new Error('Respuesta inválida del servidor');
                }

                // Actualizar resultadoGlobal con los datos válidos
                resultadoGlobal.value = {
                    articulos: data.articulos,
                    total: data.total
                };

                mostrarToast(`Stock global cargado: ${data.articulos.length} artículos encontrados`);
            } catch (error) {
                console.error('Error al cargar stock global:', error);
                mostrarToast(`Error al cargar stock global: ${error.message}`, 'error');
                resultadoGlobal.value = {
                    articulos: [],
                    total: 0
                };
            } finally {
                loadingGlobal.value = false;
            }
        };

        // Función para exportar stock global
        const exportarStockGlobal = async () => {
            try {
                // Construir parámetros de consulta
                const params = new URLSearchParams();
                if (filtros.value.busquedaGlobal) params.append('busqueda', filtros.value.busquedaGlobal);
                params.append('orden', filtros.value.ordenGlobal);
                
                const response = await fetch(`/stock/calculado/global/exportar?${params.toString()}`, {
                    method: 'GET',
                    headers: {
                        'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                    }
                });
                
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                const fecha = new Date().toISOString().split('T')[0];
                a.download = `stock_global_${fecha}.xlsx`;
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                mostrarToast('Archivo exportado exitosamente');
            } catch (error) {
                console.error('Error al exportar stock global:', error);
                mostrarToast(`Error al exportar: ${error.message}`, 'error');
            }
        };

        // Función para cargar resumen ejecutivo
        const cargarResumenEjecutivo = async () => {
            loadingResumen.value = true;
            resumenEjecutivo.value = null;
            
            try {
                // Llamar a la API para obtener el resumen ejecutivo
                const resumenResponse = await fetch('/stock/calculado/global/resumen');
                
                if (!resumenResponse.ok) {
                    throw new Error(`Error en resumen: ${resumenResponse.status}`);
                }
                
                const resumenData = await resumenResponse.json();
                resumenEjecutivo.value = resumenData;
                
                mostrarToast('Resumen ejecutivo cargado exitosamente');
            } catch (error) {
                console.error('Error al cargar resumen ejecutivo:', error);
                mostrarToast(`Error al cargar resumen ejecutivo: ${error.message}`, 'error');
            } finally {
                loadingResumen.value = false;
            }
        };
        
        // Función para dibujar gráfico de comparación
        const dibujarGraficoComparacion = () => {
            if (!resultadoComparacion.value) return;
            
            const ctx = document.getElementById('comparisonChart').getContext('2d');
            
            // Destruir gráfico anterior si existe
            if (comparisonChart) {
                comparisonChart.destroy();
            }
            
            // Datos para el gráfico
            const stockAlmacenado = resultadoComparacion.value.stock_almacenado;
            const stockCalculado = resultadoComparacion.value.stock_calculado;
            
            comparisonChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: ['Stock Físico', 'Reservado', 'En Preparación', 'Bloqueado', 'Disponible'],
                    datasets: [
                        {
                            label: 'Stock Almacenado',
                            data: [
                                stockAlmacenado.fisico,
                                stockAlmacenado.reservado,
                                stockAlmacenado.preparado,
                                stockAlmacenado.bloqueado,
                                stockAlmacenado.disponible
                            ],
                            backgroundColor: 'rgba(59, 130, 246, 0.6)',
                            borderColor: 'rgba(59, 130, 246, 1)',
                            borderWidth: 1
                        },
                        {
                            label: 'Stock Calculado',
                            data: [
                                stockCalculado.fisico,
                                stockCalculado.reservado,
                                stockCalculado.preparado,
                                stockCalculado.bloqueado,
                                stockCalculado.disponible
                            ],
                            backgroundColor: 'rgba(16, 185, 129, 0.6)',
                            borderColor: 'rgba(16, 185, 129, 1)',
                            borderWidth: 1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        };
        
        // Limpiar gráficos al cambiar de tab
        watch(activeTab, (newTab) => {
            if (newTab !== 'comparacion' && comparisonChart) {
                comparisonChart.destroy();
                comparisonChart = null;
            }
        });
        
        // Función para obtener el nombre del depósito
        const obtenerNombreDeposito = (idDeposito) => {
            const deposito = depositos.value.find(d => d.id === idDeposito);
            return deposito ? deposito.descripcion : 'Desconocido';
        };

        // Función para calcular el porcentaje disponible
        const calcularPorcentajeDisponible = (disponible, fisico) => {
            if (fisico <= 0) return 0;
            const porcentaje = (disponible / fisico) * 100;
            return Math.min(Math.max(porcentaje, 0), 100); // Limitar entre 0 y 100
        };
        
        // Funciones de navegación para Vista Global
        const irPaginaAnterior = () => {
            if (filtros.value.paginaGlobal > 1) {
                filtros.value.paginaGlobal--;
                cargarStockGlobal();
            }
        };
        
        const irPaginaSiguiente = () => {
            if (resultadoGlobal.value && resultadoGlobal.value.tiene_siguiente) {
                filtros.value.paginaGlobal++;
                cargarStockGlobal();
            }
        };
        
        const irPagina = (numeroPagina) => {
            filtros.value.paginaGlobal = numeroPagina;
            cargarStockGlobal();
        };
        
        // Función para buscar artículos con stock
        const buscarArticulosConStock = async () => {
            if (!filtros.value.busquedaGlobal.trim()) {
                // Si no hay búsqueda, cargar todos
                cargarStockGlobal();
                return;
            }
            
            loadingGlobal.value = true;
            try {
                const params = new URLSearchParams();
                params.append('termino', filtros.value.busquedaGlobal);
                params.append('limit', filtros.value.limitGlobal.toString());
                params.append('offset', '0');
                
                const response = await fetch(`/stock/calculado/buscar?${params.toString()}`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                const data = await response.json();
                resultadoGlobal.value = data;
                filtros.value.paginaGlobal = 1; // Resetear a primera página
                mostrarToast(`Búsqueda completada: ${data.articulos.length} resultados`);
            } catch (error) {
                console.error('Error en búsqueda:', error);
                mostrarToast(`Error en búsqueda: ${error.message}`, 'error');
            } finally {
                loadingGlobal.value = false;
            }
        };
        
        // ====== FUNCIONES DE AUTOCOMPLETADO ======
        
        // Función para buscar sugerencias de artículos
        const buscarSugerenciasArticulos = async (termino, campo) => {
            if (!termino || termino.length < 2) {
                ocultarSugerencias();
                return;
            }

            loadingSugerencias.value = true;
            campoActivo.value = campo;
            
            try {
                const response = await fetch(`/articulos/autocompletar?termino=${encodeURIComponent(termino)}&limite=10`);
                if (!response.ok) {
                    throw new Error(`Error: ${response.status}`);
                }
                
                const data = await response.json();
                sugerenciasArticulos.value = data.sugerencias || [];
                mostrarSugerencias.value = sugerenciasArticulos.value.length > 0;
                sugerenciasIndices.value[campo] = -1; // Resetear índice de selección
            } catch (error) {
                console.error('Error al buscar sugerencias:', error);
                sugerenciasArticulos.value = [];
                mostrarSugerencias.value = false;
            } finally {
                loadingSugerencias.value = false;
            }
        };

        // Función para ocultar sugerencias
        const ocultarSugerencias = () => {
            mostrarSugerencias.value = false;
            sugerenciasArticulos.value = [];
            campoActivo.value = '';
        };        // Función para seleccionar una sugerencia
        const seleccionarSugerencia = (sugerencia) => {
            if (campoActivo.value) {
                // Actualizar el campo correspondiente
                if (campoActivo.value === 'articulo') {
                    filtros.value.articulo = sugerencia.codigo;
                } else if (campoActivo.value === 'articuloComp') {
                    filtros.value.articuloComp = sugerencia.codigo;
                } else if (campoActivo.value === 'articuloVista') {
                    filtros.value.articuloVista = sugerencia.codigo;
                } else if (campoActivo.value === 'busquedaGlobal') {
                    filtros.value.busquedaGlobal = sugerencia.codigo;
                }
                
                ocultarSugerencias();
                mostrarToast(`Artículo seleccionado: ${sugerencia.texto_mostrar}`, 'success');
                
                // Enfocar el siguiente elemento si existe
                setTimeout(() => {
                    const nextButton = document.querySelector(`[data-campo="${campoActivo.value}"] + * button, button[data-siguiente="${campoActivo.value}"]`);
                    if (nextButton) {
                        nextButton.focus();
                    }
                }, 100);
            }
        };

        // Función para manejar eventos de teclado en los campos de autocompletado
        const manejarTecladoAutocompletado = (event, campo) => {
            if (!mostrarSugerencias.value || sugerenciasArticulos.value.length === 0) return;

            const currentIndex = sugerenciasIndices.value[campo];
            
            switch (event.key) {
                case 'ArrowDown':
                    event.preventDefault();
                    sugerenciasIndices.value[campo] = Math.min(currentIndex + 1, sugerenciasArticulos.value.length - 1);
                    break;
                    
                case 'ArrowUp':
                    event.preventDefault();
                    sugerenciasIndices.value[campo] = Math.max(currentIndex - 1, -1);
                    break;
                    
                case 'Enter':
                    event.preventDefault();
                    if (currentIndex >= 0 && currentIndex < sugerenciasArticulos.value.length) {
                        seleccionarSugerencia(sugerenciasArticulos.value[currentIndex]);
                    }
                    break;
                    
                case 'Escape':
                    event.preventDefault();
                    ocultarSugerencias();
                    break;
            }
        };        // Watchers para autocompletado en tiempo real
        watch(() => filtros.value.articulo, (newValue) => {
            if (newValue && typeof newValue === 'string' && newValue.length >= 2) {
                buscarSugerenciasArticulos(newValue, 'articulo');
            } else if (!newValue || newValue.length < 2) {
                if (campoActivo.value === 'articulo') {
                    ocultarSugerencias();
                }
            }
        });

        watch(() => filtros.value.articuloComp, (newValue) => {
            if (newValue && typeof newValue === 'string' && newValue.length >= 2) {
                buscarSugerenciasArticulos(newValue, 'articuloComp');
            } else if (!newValue || newValue.length < 2) {
                if (campoActivo.value === 'articuloComp') {
                    ocultarSugerencias();
                }
            }
        });

        watch(() => filtros.value.articuloVista, (newValue) => {
            if (newValue && typeof newValue === 'string' && newValue.length >= 2) {
                buscarSugerenciasArticulos(newValue, 'articuloVista');
            } else if (!newValue || newValue.length < 2) {
                if (campoActivo.value === 'articuloVista') {
                    ocultarSugerencias();
                }
            }
        });

        watch(() => filtros.value.busquedaGlobal, (newValue) => {
            if (newValue && typeof newValue === 'string' && newValue.length >= 2) {
                buscarSugerenciasArticulos(newValue, 'busquedaGlobal');
            } else if (!newValue || newValue.length < 2) {
                if (campoActivo.value === 'busquedaGlobal') {
                    ocultarSugerencias();
                }
            }
        });

        // ====== FIN FUNCIONES DE AUTOCOMPLETADO ======

        // Función para cambiar límite de resultados
        const cambiarLimite = () => {
            filtros.value.paginaGlobal = 1; // Resetear a primera página
            cargarStockGlobal();
        };
        
        // Función para cambiar orden
        const cambiarOrden = () => {
            filtros.value.paginaGlobal = 1; // Resetear a primera página
            cargarStockGlobal();
        };
        
        // Función para formatear números
        const formatearNumero = (numero) => {
            if (numero === null || numero === undefined) return '0';
            return Number(numero).toLocaleString('es-ES');
        };
        
        // Función para formatear porcentajes
        const formatearPorcentaje = (valor) => {
            if (valor === null || valor === undefined) return '0%';
            return `${Number(valor).toFixed(1)}%`;
        };

        return {
            depositos,
            activeTab,
            filtros,
            resultadoConsulta,
            resultadoComparacion,
            resultadoDeposito,
            resultadoArticulo,
            resultadoGlobal,
            resumenEjecutivo,
            loading,
            loadingComparacion,
            loadingDeposito,
            loadingArticulo,
            loadingGlobal,
            loadingResumen,
            busquedaRealizada,
            busquedaDepositoRealizada,
            busquedaArticuloRealizada,
            busquedaGlobalRealizada,
            porcentajeDisponible,
            algunaDiferencia,
            paginasDisponibles,
            infoPaginacion,
            buscarStockIndividual,
            compararStock,
            buscarStockDeposito,
            buscarStockArticulo,
            cargarStockGlobal,
            exportarStockGlobal,
            cargarResumenEjecutivo,
            calcularPorcentajeDisponible,
            obtenerNombreDeposito,
            irPaginaAnterior,
            irPaginaSiguiente,
            irPagina,
            buscarArticulosConStock,
            cambiarLimite,
            cambiarOrden,
            formatearNumero,
            formatearPorcentaje,
            // Autocompletado
            sugerenciasArticulos,
            mostrarSugerencias,
            loadingSugerencias,
            campoActivo,
            sugerenciasIndices,
            buscarSugerenciasArticulos,
            ocultarSugerencias,
            seleccionarSugerencia,
            manejarTecladoAutocompletado
        };
    }
}).mount('#app');