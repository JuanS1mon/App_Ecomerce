// login_handler.js
// Este script maneja la redirección después del login

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(loginForm);
            const loginData = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(loginData)
                });

                if (response.ok) {
                    const data = await response.json();
                    const redirectUrl = data.redirect_url || '/index';
                    window.location.href = redirectUrl;
                } else {
                    console.error('Error en el login:', response.statusText);
                    alert('Error en el login. Por favor, verifica tus credenciales.');
                }
            } catch (error) {
                console.error('Error al procesar el login:', error);
                alert('Ocurrió un error al intentar iniciar sesión.');
            }
        });
    }
});
