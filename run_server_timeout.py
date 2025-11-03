import subprocess
import time
import signal
import os

def run_server_with_timeout():
    print('Starting server...')
    process = subprocess.Popen(
        ['python', 'main.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding='utf-8',
        errors='replace'  # Replace problematic characters
    )

    # Wait for server to start and show logs
    time.sleep(8)

    # Terminate the process
    try:
        process.terminate()
        process.wait(timeout=5)
    except:
        try:
            process.kill()
        except:
            pass

    # Read output
    output, _ = process.communicate()
    print('SERVER OUTPUT:')
    print('=' * 50)
    print(output)

if __name__ == '__main__':
    run_server_with_timeout()