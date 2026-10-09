# Portapapeles de Omarchy con selección múltiple

Permite marcar varios textos del historial y pegarlos como un bloque, en el
orden de marcado y separados por un salto de línea. Mantiene la interfaz del
gestor nativo de Omarchy.

## Instalación

Probado en Omarchy 4.0.4. Requiere Omarchy Shell, sus comandos nativos de
portapapeles, Quickshell, `wl-clipboard` y `wtype`.

```bash
omarchy plugin add https://github.com/felix-antonio-sl/omarchy-clipboard-multiselect.git --enable
```

El identificador del plugin es `felix-antonio-sl.clipboard-multiselect`. Omarchy
lo reconoce como copia de `omarchy.clipboard` y conserva el atajo habitual.

## Uso

1. Abre el historial con **Super + Ctrl + V**. En un teclado Mac, Super suele
   corresponder a Command.
2. Marca los textos con **Ctrl + clic**, o mueve el foco con las flechas y usa
   **Ctrl + Espacio**.
3. Comprueba los números que indican el orden y la vista previa del bloque.
4. Pulsa **Enter** para pegarlo o **Shift + Enter** para copiarlo.

La búsqueda conserva las marcas. Cada apertura nueva comienza sin selección.
Escape primero limpia la búsqueda y, cuando ya está vacía, cierra el gestor.

Los textos se copian completos, aunque la vista previa limite los caracteres
mostrados. Las imágenes y los archivos se seleccionan de manera individual: si
el foco está sobre uno de ellos, Enter o Shift + Enter usa su acción nativa.

## Actualizaciones

La instalación queda bajo `~/.config/omarchy/plugins/`, en una carpeta propia
del usuario. Las actualizaciones normales de Omarchy conservan esos archivos.
El plugin se actualiza por separado:

```bash
omarchy plugin update felix-antonio-sl.clipboard-multiselect
```

Una versión mayor de Omarchy que cambie la API de plugins puede requerir una
adaptación. La copia local conserva el código, pero no garantiza compatibilidad
con todas las versiones futuras.

Para volver al portapapeles original, conservando la instalación personalizada:

```bash
omarchy plugin disable felix-antonio-sl.clipboard-multiselect
```

## Pruebas y procedencia

Desde la carpeta del repositorio:

```bash
node --test tests/selection.test.cjs
python3 tests/check-qml.py
```

La segunda prueba requiere Omarchy y Quickshell. Ejecuta los manejadores reales
en un motor Qt aislado y envía el resultado a archivos de prueba. No modifica el
portapapeles ni envía teclas a las aplicaciones del escritorio.

El plugin deriva del gestor nativo de Omarchy 4.0.4. Conserva su licencia MIT y
la atribución de su código original en `LICENSE` y `NOTICE.md`.
