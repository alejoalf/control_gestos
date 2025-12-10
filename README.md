# control_gestos
# Mouse Controlado por Gestos con IA

Controla el mouse de tu computadora usando gestos de mano capturados por tu cámara web. Este proyecto utiliza **OpenCV** y **MediaPipe** para el seguimiento de manos en tiempo real y **PyAutoGUI** para el control del mouse.

## Características

- **Control del Cursor**: Mueve el cursor moviendo tu dedo índice.
- **Clic Izquierdo**: Pellizca juntando tu **Dedo Índice** y **Pulgar**.
    - Incluye soporte para arrastrar y soltar (mantener pellizcado).
- **Clic Derecho**: Pellizca juntando tu **Dedo Medio** y **Pulgar**.
- **Desplazamiento (Scroll)**: Levanta ambos dedos **Índice** y **Medio**.
    - Mantén la mano en la mitad superior de la pantalla para subir (Scroll UP).
    - Mantén la mano en la mitad inferior de la pantalla para bajar (Scroll DOWN).
- **Seguimiento Suave**: Suavizado exponencial para un movimiento preciso del cursor.
- **Estabilidad**: Histéresis implementada para prevenir clics accidentales o "parpadeo".

## Requisitos

- **Python 3.11** (Requerido para compatibilidad con MediaPipe en Windows)
- Cámara Web

## Instalación

1.  Clona este repositorio.
2.  Instala las dependencias requeridas:
    ```bash
    pip install -r requirements.txt
    ```
    *Nota: Si tienes múltiples versiones de Python, asegúrate de estar usando Python 3.11.*

## Uso

Ejecuta el script usando Python 3.11:

```bash
py -3.11 main.py
```

### Guía de Gestos

| Acción | Gesto | Indicador Visual |
| :--- | :--- | :--- |
| **Mover Cursor** | Apuntar con **Dedo Índice** | Círculo Púrpura |
| **Clic Izquierdo** | Pellizcar **Índice** + **Pulgar** | Círculo Verde |
| **Arrastrar** | Pellizcar **Índice** + **Pulgar** y mantener | Círculo Verde |
| **Clic Derecho** | Pellizcar **Medio** + **Pulgar** | Círculo Azul |
| **Scroll** | Levantar dedos **Índice** + **Medio** | Texto "Scroll UP/DOWN" |

## Solución de Problemas

- **La cámara no abre**: Verifica si otra aplicación está usando la cámara. El script intenta automáticamente los índices 0-3.
- **Cursor tembloroso**: Asegúrate de tener buena iluminación. El script usa suavizado, pero la mala iluminación afecta la estabilidad de la detección.
- **Error de MediaPipe**: Asegúrate de usar **Python 3.11**. Python 3.12+ aún no es totalmente compatible con MediaPipe.

## Licencia
