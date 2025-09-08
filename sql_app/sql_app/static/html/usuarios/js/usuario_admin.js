document.addEventListener('DOMContentLoaded', function() {
    // Cargar componentes (navbar, breadcrumb, etc.)
    if (window.loadComponents) {
        loadComponents();
    } else {
        console.error("La función loadComponents no está disponible");
    }
    
    // Validación de contraseñas
    const passwordField = document.getElementById('password');
    const confirmField = document.getElementById('confirm_password');
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        if (passwordField.value && passwordField.value !== confirmField.value) {
            event.preventDefault();
            alert('Las contraseñas no coinciden');
            confirmField.focus();
        }
    });
});
