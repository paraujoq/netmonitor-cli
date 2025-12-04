import sys
from pathlib import Path

# Agregar src al path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Importar y ejecutar
from netmonitor.main import main

if __name__ == "__main__":
    main()
    