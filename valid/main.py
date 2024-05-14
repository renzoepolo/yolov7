import subprocess

def main():
    # Lista de scripts a ejecutar
    scripts = ['download.py','labelling.py', 'tif2jpg.py']
    
    # Ejecutar cada script de manera consecutiva
    for script in scripts:
        result = subprocess.run(['python', script], capture_output=True, text=True)
        
        # Imprimir la salida y errores de cada script
        print(f"Ejecutando {script}...")
        print("Salida:")
        print(result.stdout)
        print("Errores:")
        print(result.stderr)
        print(f"{script} finalizado con código de salida {result.returncode}\n")
    
        # Verificar si hubo un error y detener la ejecución si es necesario
        if result.returncode != 0:
            print(f"Error al ejecutar {script}. Deteniendo la ejecución.")
            break

if __name__ == "__main__":
    main()