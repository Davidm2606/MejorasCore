BancoWebUDLA
BancoWebUDLA es un proyecto web desarrollado utilizando HTML, CSS y Bootstrap para crear una interfaz de usuario interactiva para un sistema bancario. Este proyecto sigue los principios SOLID y utiliza patrones de diseño para mejorar la estructura y modularidad del código.

Características
Diseño responsivo utilizando Bootstrap.
Plantilla base reutilizable.
Barra de navegación extensible.
Carrusel de imágenes en la página principal.
Cumplimiento con principios SOLID y patrones de diseño.
Estructura del Proyecto
La estructura del proyecto es la siguiente:

css
Copy code
BancoWebUDLA/
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   ├── banner.png
│   │   ├── image1.jpg
│   │   ├── image3.jpg
│   │   └── image4.webp
│   └── js/
│       └── main.js
├── templates/
│   ├── base.html
│   ├── operaciones.html
│   └── otras páginas HTML
└── README.md
Instalación
Clona el repositorio en tu máquina local:

bash
Copy code
git clone https://github.com/tu-usuario/BancoWebUDLA.git
Navega al directorio del proyecto:

bash
Copy code
cd BancoWebUDLA
Uso
Abre base.html en un navegador para ver la plantilla base y las páginas asociadas. Puedes extender las páginas creando nuevos archivos HTML y utilizando la estructura definida en base.html.

Ejemplo de Extensión:

Para crear una nueva página llamada nueva_pagina.html:

Crea el archivo nueva_pagina.html en el directorio templates/ con el siguiente contenido:

html
Copy code
{% extends "base.html" %}

{% block navigation %}
<li class="nav-item">
    <a class="nav-link" href="retiros.html">Retiros</a>
</li>
<li class="nav-item">
    <a class="nav-link" href="depositos.html">Depositos</a>
</li>
<li class="nav-item">
    <a class="nav-link" href="transferencias.html">Transferencias</a>
</li>
<li class="nav-item">
    <a class="nav-link" href="nueva_pagina.html">Nueva Página</a>
</li>
{% endblock %}

{% block content %}
<h1>Bienvenido a la Nueva Página</h1>
<p>Contenido de la nueva página aquí.</p>
{% endblock %}
Abre nueva_pagina.html en tu navegador para ver la nueva página extendida de la plantilla base.

Principios y Patrones de Diseño
Este proyecto implementa los siguientes principios y patrones de diseño:

Principio SOLID:
Open/Closed Principle (OCP): La plantilla base permite la extensión sin modificar el código base.
Patrones de Diseño:
Composite: La barra de navegación trata elementos individuales y compuestos de manera uniforme, permitiendo una fácil extensión.
Template: La plantilla base (base.html) define la estructura general, permitiendo la reutilización y extensión en páginas específicas.
