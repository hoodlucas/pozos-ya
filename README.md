<img width="1144" height="631" alt="image" src="https://github.com/user-attachments/assets/cf02cd72-7f45-4b6c-b92d-3aaae9e9e609" />

https://hoodlucas.pythonanywhere.com/nuevo/
Este es el link al proyecto, si te está caído pueden descargar el proyecto!

Pozos Ya   
Plataforma Integral de Gestión de Baches en Lomas de Zamora

Pozos Ya es una aplicación web desarrollada en Django que permite a los vecinos del Municipio de Lomas de Zamora reportar baches y problemas viales, y al Municipio gestionar esos reclamos de forma centralizada, transparente y basada en datos.
El proyecto nació como iniciativa personal de un estudiante y vecino de Lomas de Zamora, con el objetivo de acercar una herramienta simple pero potente para mejorar la comunicación ciudadano–municipio y contribuir a una ciudad más segura y ordenada.

1. ⚙️ Funcionalidades Principales
El sistema se divide en dos perfiles de usuario principales, cada uno con funcionalidades específicas:
Perfil Vecino (Usuario Registrado)
•	Registro y Seguridad: Alta de cuenta con verificación de email (código de 6 dígitos) y funcionalidad de recuperación de contraseña.
•	Carga de Reclamos: Permite registrar baches con título, descripción, datos de ubicación (calle, altura, barrio) y geolocalización (lat/long). Acepta la subida de múltiples imágenes y se define la severidad del daño.
•	Visualización y Mapa: Listado de baches filtrable y un Mapa interactivo (Leaflet) con marcadores. El mapa muestra el estado, severidad e imagen al hacer clic en un marcador.
•	Sistema de Votos (Upvotes): Los vecinos pueden apoyar reclamos existentes para que el Municipio los use como criterio de priorización.
•	Gestión Personal: Sección "Mis baches" (con listado y mapa personal) y "Datos personales" (edición de DNI, teléfono, domicilio, etc.).
Perfil Municipio (Rol "municipio")
•	Panel de Gestión: Panel responsivo con vista tabular de todos los reclamos. Incluye filtros avanzados (estado, severidad, barrio, búsqueda) y ordenamiento por fecha, así como por la cantidad de votos (más/menos votados).
•	Actualización Masiva: Permite la edición en lote, facilitando el cambio de estado y la adición/modificación de comentarios para múltiples baches a la vez.
o	Automático: Cada cambio guarda un Historial de modificaciones y genera Notificaciones automáticas (por sistema y email) para el vecino reportante.
•	Reportes y Exportaciones: Capacidad de exportar el listado de baches (respetando filtros y ordenamiento) a formatos CSV, Excel y PDF.
•	Dashboard Gráfico: Presenta un Gráfico tipo torta (Chart.js) que muestra la distribución geográfica de los reclamos por barrio, con el tamaño proporcional a la cantidad de baches reportados en esa zona.

2. Tecnologías Clave
Componente	Tecnologías Utilizadas
Backend	Python, Django
Base de Datos	SQLite (para desarrollo)
Frontend	HTML5, CSS3, JavaScript (vanilla)
Mapeo	Leaflet (para mapas interactivos)
Gráficos	Chart.js (para el Dashboard)
Otros	Plantillas de Django, Envío de emails vía SMTP (Gmail)

    Modelos Principales de Datos
Los modelos de la base de datos se centran en la gestión del reclamo y la seguridad del usuario:
•	Bache: Contiene todos los datos del reclamo (título, descripción, severidad, estado, lat/long, referencia al vecino, etc.).
•	ImagenBache: Almacena las imágenes asociadas al bache.
•	Perfil: Extiende el usuario, conteniendo el rol (vecino / municipio) y datos personales (DNI, teléfono, domicilio).
•	HistorialBache: Registra cada cambio en el estado o comentario de un bache.
•	Notificacion: Mensajes del sistema enviados al vecino sobre el progreso de su reclamo.
•	CodigoEmail / PasswordResetCode: Modelos dedicados a la seguridad y verificación (alta de cuenta y recuperación de contraseña).

Instalación y puesta en marcha
1. Clonar el repositorio
2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate
3. Instalar dependencias
pip install -r requirements.txt
Si no existe todavía el requirements.txt, se puede generar con:
pip freeze > requirements.txt
5. Aplicar migraciones
python manage.py migrate
6. Crear superusuario
python manage.py createsuperuser
Seguí las instrucciones (usuario, email y password).
7. Crear usuario con rol “municipio”
Desde el admin de Django:
1.	Iniciar servidor:
2.	python manage.py runserver
3.	Ir a http://127.0.0.1:8000/admin/.
4.	Iniciar sesión con el superusuario.
5.	Crear un User común o usar uno existente.
6.	Crear un Perfil asociado a ese usuario y setear:
o	rol = "municipio".
Con eso, ese usuario podrá entrar al Panel Municipio.
