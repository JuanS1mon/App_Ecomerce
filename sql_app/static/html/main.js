// Función para formatear la fecha
function formatearFecha(fecha) {
    return fecha.toISOString().slice(0,10).split("-").reverse().join("/");
}

// Función para recoger los valores de los inputs de fecha y convertirlos a formato dd/mm/aaaa
function obtenerFechasFormateadas(mesAnoDesde, mesAnoHasta) {
    var fechaDesde = new Date(mesAnoDesde + "-01");
    var fechaHasta = new Date(mesAnoHasta + "-01");
    fechaHasta.setMonth(fechaHasta.getMonth() + 1);
    fechaHasta.setDate(fechaHasta.getDate() - 1); // Último día del mes

    return {
        fechaDesdeFormateada: formatearFecha(fechaDesde),
        fechaHastaFormateada: formatearFecha(fechaHasta)
    };
}

// Función para recoger los checkboxes seleccionados
function obtenerSeleccionados() {
    var checkboxes = document.getElementsByClassName('rowCheckbox');
    var seleccionados = [];
    for (var i = 0; i < checkboxes.length; i++) {
        if (checkboxes[i].checked) {
            seleccionados.push({ clienteWeb: parseInt(checkboxes[i].value), sucursal: 1 });
        }
    }
    return seleccionados;
}

document.addEventListener('DOMContentLoaded', (event) => {
    document.getElementById('exportar').addEventListener('click', function(event) {
        event.preventDefault(); // Evitar que la página se recargue

        var mesAnoDesde = document.getElementById('mesAnoDesde').value;
        var mesAnoHasta = document.getElementById('mesAnoHasta').value;

        var fechas = obtenerFechasFormateadas(mesAnoDesde, mesAnoHasta);
        var seleccionados = obtenerSeleccionados();

        var datos = {
            mesAnoDesde: fechas.fechaDesdeFormateada,
            mesAnoHasta: fechas.fechaHastaFormateada,
            seleccionados: seleccionados
        };

        // Aquí va el código para enviar los datos
        // ...
    });

    document.getElementById('cargar').addEventListener('click', function(event) {
        event.preventDefault(); // Evitar que la página se recargue

        var mesAnoDesde = document.getElementById('mesAnoDesde').value;
        var mesAnoHasta = document.getElementById('mesAnoHasta').value;

        var fechas = obtenerFechasFormateadas(mesAnoDesde, mesAnoHasta);

        // Aquí va el código para cargar los datos
        // ...
    });
});