# Documento de Especificaciones: Cliente Gráfico de Git (MVP)

## Descripción General
El objetivo de este proyecto es construir un cliente gráfico de Git de alta calidad, como alternativa gratuita a herramientas de pago como GitKraken. Orientado a programadores, esta primera iteración (MVP) se enfoca en establecer la base tecnológica gráfica y ofrecer la funcionalidad esencial de abrir un repositorio local y visualizar su historial de commits.

## Decisiones Tecnológicas y Arquitectura
- **Plataforma y Framework**: Electron (Aplicación de Escritorio). La aplicación funcionará como un monolito local sin backend remoto.
- **Arquitectura Interna**: Estructuración modular aplicando principios de **Clean Architecture**. El código (paquetes/directorios) se organizará y separará explícitamente guiado por **Casos de Uso** (Use Cases). A pesar de ser un monolito, se aislará estrictamente la capa de presentación (Renderer/UI), la capa de lógica de negocio (Use Cases) y la capa de infraestructura (Main Process/CLI de Git).
- **Stack Tecnológico**: HTML, CSS Vanilla (diseño premium, dark mode, glassmorphism) y JavaScript/TypeScript moderno.
- **Interacción con Git**: Invocación de la CLI local de `git` mediante procesos asíncronos en Node.js (Main Process de Electron) para garantizar que la interfaz se mantenga fluida.

## Requerimientos Funcionales
- **RF01**: La aplicación debe incluir una pantalla de inicio que permita al usuario abrir la ruta de un repositorio de Git local a través de un diálogo del sistema operativo o ingresando la ruta.
- **RF02**: La aplicación debe extraer asíncronamente el historial de commits de la rama actual del repositorio seleccionado.
- **RF03**: La aplicación debe mostrar una lista visual del historial de commits, detallando para cada uno: Hash (abreviado), Mensaje del commit, Autor y Fecha.
- **RF04**: La interfaz principal debe permitir cambiar de repositorio de manera sencilla, volviendo al diálogo de selección.

## Requerimientos No Funcionales
- **RNF01**: **Rendimiento UI**: La lectura y renderizado del historial de commits debe realizarse de forma asíncrona sin bloquear la interfaz de usuario.
- **RNF02**: **Diseño y Estética**: La aplicación debe contar con un diseño moderno, profesional y "premium", utilizando paletas oscuras, tipografías modernas y micro-animaciones para competir visualmente con herramientas del mercado.
- **RNF03**: **Compatibilidad Multiplataforma**: La arquitectura debe mantenerse agnóstica para permitir su ejecución en Linux, Windows y macOS gracias a Electron.
- **RNF04**: **Mantenibilidad**: El código debe seguir una separación estricta de responsabilidades (Clean Architecture), asegurando que el acoplamiento sea mínimo a pesar de ser un monolito.
- **RNF05**: **Desacoplamiento Visual**: La estructura gráfica (HTML) y los estilos (CSS) deben estar completamente aislados y separados de la lógica del frontend (JavaScript/TypeScript). Esto permitirá desechar o reemplazar el diseño visual sin afectar el funcionamiento del cliente.
