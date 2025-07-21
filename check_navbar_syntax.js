const fs = require('fs');
const path = require('path');

// Leer el archivo navbar.html
const navbarPath = path.join(__dirname, 'sql_app', 'static', 'components', 'navbar.html');
const content = fs.readFileSync(navbarPath, 'utf8');

// Extraer solo el JavaScript del archivo
const scriptMatch = content.match(/<script>([\s\S]*?)<\/script>/);
if (scriptMatch) {
    const jsCode = scriptMatch[1];
    
    console.log('Verificando sintaxis del JavaScript del navbar...');
    
    try {
        // Intentar crear una función con el código JavaScript
        new Function(jsCode);
        console.log('✅ El JavaScript del navbar tiene sintaxis válida');
    } catch (error) {
        console.error('❌ Error de sintaxis en el JavaScript del navbar:');
        console.error(error.message);
        console.error('Línea aproximada:', error.lineNumber || 'desconocida');
        
        // Mostrar las líneas alrededor del error si es posible
        if (error.lineNumber) {
            const lines = jsCode.split('\n');
            const start = Math.max(0, error.lineNumber - 3);
            const end = Math.min(lines.length, error.lineNumber + 2);
            
            console.error('\nContexto del error:');
            for (let i = start; i < end; i++) {
                const marker = i === error.lineNumber - 1 ? '>>> ' : '    ';
                console.error(`${marker}${i + 1}: ${lines[i]}`);
            }
        }
    }
} else {
    console.error('❌ No se encontró script en el archivo navbar.html');
}
