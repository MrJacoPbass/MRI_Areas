# MRI_Areas
Graphical tool to analyse MRI-related images.

2025/05/20 - Gerard Villarroya (JacoPbass)
v1.1

IMPORTANTE: No borrar el archivo "Default.tif". Si no lo encuentra el programa no se inicia. 

light_install.py proporciona una manera ligera de generar un ejecutable a partir del código.
Backbone.py implementa la funcionalidad numérica mientras que MRI_Areas se ocupa de lo relacionado con la integración GUI.

EJECUTAR: Idealmente, ejecutar el archivo MRI_Areas.py

Instrucciones básicas:

	- Open: Abrir una nueva imagen
	- Save: Guardar la imagen mostrada
	- Select slice: Selecciona la capa a analizar si el formato es nifti
	- 2 Sliders (-20 y 20): Ajuste fino manual de los límites para el análisis del área relevante.
	- Rotate: Rota la imagen 90º en sentido antihorario.
	- Miniatura: Muestra la imagen que se está analizando
		Para mover el zoom, haz click sobre la miniatura y arrastra.
	- Image dimensions: Si las dimensiones de la imagen son conocidas y se introducen aquí, se calcula el área real de la zona analizada en blanco.
	- Areas: Retorna los valores de las áreas de las zonas analizadas en blanco.
	- Imagen: Muestra la imagen. En las esquinas hay 4 puntos que se pueden mover para tener más precisión en la zona que se quiere analizar.
	- Zoom (+ deslizador): Mueve el deslizador para cambiar el zoom. Click y arrastra en la miniatura para mover el zoom.
	- Reset: Devuelve el sistema al estado original. Si no funciona hay un reset más efectivo que es cerrar y reabrir la aplicación :)
	- Analyse: Ejecuta el análisis de la zona resaltada en la imagen principal.

NOTAS: En desarrollo, dudas, cuestiones, sugerencias y problemas a uo244753@uniovi.es.

_______________________________________________________________________________________________________________________________________

IMPORTANT: Don't remove "Default.tif" as the program expects it to run.

light_install.py provides a script to build the python code into an executable.
Backbone.py implements the numerical functionality while MRI_Areas.py takes care of the GUI integration and functionality.

TO_RUN: Ideally run the MRI_Areas.py

Instructions:

    - Open: Opens a new image.
    - Save: Saves the image showing on the main panel.
    - Select slice: For .nifti files, this slider selects the slide.
    - 2 Sliders (-20 and 20): Manual fine-tuning for the relevant areas to be analysed.
    - Rotate: Rotates the image 90º counter-clockwise.
    - Miniature: Shows the image that is being analysed.
        To move the zoomed iamge, click and draw on top of the miniature.
    - Image dimensions: If the image scale is known, these boxes allow for the computation of the real area that has been selected.
    - Areas: Returns the values computed for the white-selected areas.
    - Imagen: Shows the main image. Each of the four corners have handles to select more precisely the region to be analysed.
    - Zoom (+ slider): Click and drag on the miniature to move the zoomed image. The slider changes the zoom value.
    - Reset: Returns the image to the original state. If something went wrong and this button does't work properly a hard reset should solve
    it, close and reopen the tool.
    - Analyse: Performs the analysis of the area selected in the main image.

NOTES: Developing the tool, questions, doubts and problems at uo244753@uniovi.es
