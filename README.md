# 🌐 NetMonitor CLI

Herramienta de línea de comandos para análisis de logs de equipos de red (routers, switches, etc.).

**Desarrollado por:** Pedro Araujo Quintero  
**Tecnologías:** Python 3.12+, Typer, Pydantic, Rich

---

## ✨ Características

- ✅ **Parser robusto** con validación Pydantic
- 📊 **Análisis estadístico** de logs
- 🎨 **Output colorido** en terminal con Rich
- 📁 **Múltiples formatos** de reporte (texto, JSON, HTML)
- 🧪 **Tests unitarios** con pytest
- 🔍 **Type hints completos** para mejor autocompletado
- ⚡ **Performance** optimizado con análisis eficiente

---

## 🚀 Instalación

### Requisitos
- Python 3.12 o superior
- `uv` (gestor de paquetes moderno)

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/netmonitor-cli.git
cd netmonitor-cli

# 2. Crear entorno virtual e instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# 3. Verificar instalación
netmonitor --help
```

---

## 📖 Uso

### Comando Básico

```bash
# Analizar un archivo de logs
netmonitor analyze sample_logs/network.log
```

### Opciones Avanzadas

```bash
# Guardar reporte en archivo
netmonitor analyze logs/router.log -o report.txt

# Generar reporte en JSON
netmonitor analyze logs/router.log -o report.json -f json

# Generar reporte en HTML
netmonitor analyze logs/router.log -o report.html -f html
```

### Demo

```bash
# Ver una demostración rápida
netmonitor demo
```

---

## 📝 Formato de Logs Esperado

El parser espera logs en el siguiente formato:

```
YYYY-MM-DD HH:MM:SS LEVEL [DEVICE] MESSAGE
```

**Ejemplo:**
```
2024-10-05 14:30:45 ERROR [Router-01] Connection timeout to 192.168.1.1
2024-10-05 14:31:12 WARNING [Switch-Core-01] High CPU utilization: 85%
2024-10-05 14:32:00 CRITICAL [Router-02] Power supply failure
```

**Niveles soportados:** DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🧪 Testing

```bash
# Ejecutar todos los tests
pytest

# Con coverage
pytest --cov=netmonitor --cov-report=html

# Tests específicos con verbose
pytest tests/test_parser.py -v
```

---

## 🛠️ Desarrollo

### Linting y Formatting

```bash
# Formatear código con Ruff
ruff format src/

# Linting
ruff check src/

# Type checking con mypy
mypy src/
```

### Estructura del Proyecto

```
netmonitor-cli/
├── src/
│   └── netmonitor/
│       ├── __init__.py
│       ├── main.py          # CLI principal
│       ├── parser.py        # Parser de logs
│       ├── analyzer.py      # Análisis estadístico
│       └── reporter.py      # Generación de reportes
├── tests/
│   └── test_parser.py       # Tests unitarios
├── sample_logs/
│   └── network.log          # Logs de ejemplo
├── pyproject.toml           # Configuración del proyecto
└── README.md
```

---

## 📊 Ejemplo de Salida

```
📊 Reporte de Análisis de Logs

╭─────────────────── Resumen General ───────────────────╮
│ Total de Entradas: 50                                 │
│ Período: 2024-10-05 08:15 → 2024-10-05 09:03         │
│ Duración: 0.8 horas                                   │
│ Tasa de Errores: 32.00%                               │
╰───────────────────────────────────────────────────────╯

         Distribución por Nivel          
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Nivel    ┃ Cantidad ┃ Porcentaje ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ INFO     │       20 │     40.0%  │
│ ERROR    │       14 │     28.0%  │
│ WARNING  │       12 │     24.0%  │
│ CRITICAL │        3 │      6.0%  │
│ DEBUG    │        1 │      2.0%  │
└──────────┴──────────┴────────────┘
```

---

## 🎓 Conceptos de Python Moderno Aplicados

Este proyecto utiliza las mejores prácticas de Python moderno:

1. **Type Hints Completos**: Mejora el autocompletado y detección de errores
2. **Pydantic V2**: Validación de datos declarativa y eficiente
3. **Dataclasses**: Estructuras de datos inmutables y eficientes
4. **Pattern Matching**: (Python 3.10+) Para lógica condicional clara
5. **f-strings**: Formateo de strings moderno y legible
6. **Context Managers**: Manejo automático de recursos
7. **Comprehensions**: Código conciso y pythonic
8. **Property Decorators**: Atributos calculados elegantes

---

## 🔄 Próximas Mejoras

- [ ] Soporte para logs en JSON y syslog
- [ ] Análisis de tendencias temporales
- [ ] Alertas automáticas por umbrales
- [ ] Dashboard web interactivo
- [ ] Integración con sistemas de monitoreo (Prometheus, Grafana)
- [ ] Soporte para logs comprimidos (gzip)
- [ ] Filtrado avanzado por regex

---

## 📚 Recursos de Aprendizaje

- [Typer Documentation](https://typer.tiangolo.com/)
- [Pydantic V2 Docs](https://docs.pydantic.dev/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Python Type Hints Cheatsheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)

---

## 📄 Licencia

MIT License - ver archivo LICENSE para detalles

---

## 👤 Autor

**Pedro Araujo Quintero**
- LinkedIn: [linkedin.com/in/pcaq](https://www.linkedin.com/in/pcaq)
- Email: pedro.araujoq@gmail.com
- Ubicación: Santiago, Chile

---

## 🤝 Contribuciones

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: amazing feature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

**¿Encontraste un bug?** Abre un issue en GitHub con detalles y pasos para reproducirlo.
