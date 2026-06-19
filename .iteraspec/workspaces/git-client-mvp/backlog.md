# Task Catalog

### T01 - Scaffold de proyecto Electron y estructura Clean Architecture
- Created At: 2026-06-18T22:04:10-04:00
- Requirement: RNF04, RNF05
- Assignees: Lucas Rios
- Description: Inicializar la aplicación Electron base e implementar la estructura de directorios orientada a Casos de Uso. Adicionalmente, establecer la separación estricta entre la lógica de presentación (JS/TS) y los archivos visuales (HTML/CSS).
- Acceptance Criteria: El proyecto compila, la ventana se abre y la estructura aísla la UI, la lógica y la infraestructura, garantizando que el diseño (HTML/CSS) esté desacoplado de la lógica de vistas.
- Dependencies: None

### T02 - Infraestructura Git y Caso de Uso: Extraer historial de commits
- Created At: 2026-06-18T22:04:10-04:00
- Requirement: RF02
- Assignees: Lucas Rios
- Description: Implementar el Caso de Uso en Node.js (Main Process) que invoca asíncronamente a la CLI local de git para obtener el log de commits y parsearlo en objetos estructurados.
- Acceptance Criteria: El caso de uso retorna una lista asíncrona de commits (Hash, Mensaje, Autor, Fecha) al invocarse, cumpliendo con la exigencia de no bloquear el hilo (RNF01).
- Dependencies: T01

### T03 - UI y Caso de Uso: Pantalla de inicio y selección de repositorio
- Created At: 2026-06-18T22:04:10-04:00
- Requirement: RF01
- Assignees: Lucas Rios
- Description: Construir la pantalla inicial y el Caso de Uso encargado de abrir el diálogo nativo del sistema para seleccionar el directorio del repositorio local.
- Acceptance Criteria: El usuario ve una interfaz con diseño "premium" (dark mode) y puede abrir exitosamente el diálogo para capturar la ruta del repositorio.
- Dependencies: T01

### T04 - UI: Visualización dinámica del historial de commits
- Created At: 2026-06-18T22:04:10-04:00
- Requirement: RF03, RNF05
- Assignees: Lucas Rios
- Description: Diseñar y construir el panel principal de la aplicación que procesa y renderiza la lista de commits, manteniendo la lógica de actualización separada del diseño base.
- Acceptance Criteria: La UI despliega cada commit correctamente y el código garantiza que el diseño (CSS/HTML) pueda ser modificado sin afectar el script que inyecta los datos (RNF05).
- Dependencies: T02, T03

### T05 - UI: Navegación para cambiar de repositorio
- Created At: 2026-06-18T22:04:10-04:00
- Requirement: RF04
- Assignees: TBD
- Description: Añadir a la interfaz principal un control que permita al usuario cerrar el historial actual y volver a la pantalla de selección o elegir otra ruta.
- Acceptance Criteria: El usuario puede cambiar a otro repositorio y visualizar el nuevo historial sin tener que reiniciar la aplicación.
- Dependencies: T04
