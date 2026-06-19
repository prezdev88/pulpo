# Pulpo (Git Client MVP)

Pulpo es un cliente de Git gráfico construido con **Electron** y **Node.js**. Está diseñado para ofrecer una experiencia rápida, minimalista y con un fuerte énfasis en las buenas prácticas de arquitectura de software.

## Características (MVP)
- **Selección de Repositorios**: Interfaz premium para explorar y seleccionar cualquier repositorio Git local.
- **Historial de Commits**: Visualización en formato de árbol (lineal) de los commits de la rama actual.
- **Diseño Desacoplado**: El diseño de la interfaz (HTML/CSS) está estrictamente separado de la lógica de presentación (JS), permitiendo un rediseño total sin afectar el comportamiento subyacente.
- **Modo Oscuro / Premium**: Estética moderna utilizando técnicas de Glassmorphism.
- **Panel Redimensionable**: El árbol de commits se despliega en un menú lateral ajustable tipo VS Code.

## Arquitectura

El proyecto sigue un acercamiento basado en **Clean Architecture**:

- `src/main/`: Contiene el código del **Main Process** de Electron (interacción con el sistema operativo y puente seguro).
- `src/core/`: Define los **Casos de Uso** (lógica de negocio asíncrona que invoca a la CLI de git localmente sin bloquear el hilo principal).
- `src/renderer/`: Contiene la lógica del **Renderer Process** (interacción con el DOM y comunicación con el Main Process).
- `src/renderer/ui/`: Almacena de manera puramente aislada el HTML y CSS (Vistas y templates), cumpliendo la regla de que el equipo de diseño puede trabajar de forma paralela sin tocar JavaScript.

## Requisitos Previos
- Node.js (probado en v26.3.1)
- NVM (opcional, pero recomendado)
- NPM

## Instalación y Ejecución

1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   npm install
   ```
3. Iniciar la aplicación:
   ```bash
   npm start
   ```
   *Nota: Se provee un archivo `run.sh` en la raíz del proyecto para desarrolladores en Linux/macOS que carga NVM automáticamente antes de ejecutar el inicio.*

## Testing

El proyecto se desarrolló bajo la metodología **TDD (Test-Driven Development)** utilizando Jest.
Para ejecutar la suite de pruebas:

```bash
npm test
```

## Próximos Pasos (Roadmap)
- Implementación de un renderizado de SVG/Canvas para mostrar visualmente bifurcaciones y uniones de ramas.
- Detalles del commit (archivos modificados, diff) en el panel derecho de la interfaz.
