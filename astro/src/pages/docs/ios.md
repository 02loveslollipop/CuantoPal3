---
layout: ../../layouts/DocsLayout.astro
title: Cuanto pal 3 en iOS
description: Guia de instalacion de Cuanto pal 3 en iOS
---

# Cuanto pal 3 en iOS
Cuanto pal 3 no esta disponible en la App Store, pero puedes compilarlo tu mismo si cuentas con Xcode y un dispositivo iOS.

# Opcion alternativa: Usar Cuanto pal 3 web como aplicacion nativa
Si no deseas compilar la aplicacion, puedes usar Cuanto pal 3 web como una aplicacion nativa. Para ello, sigue estos pasos:
1. Abre Safari en tu dispositivo iOS.
2. Accede a la [cuantopal3.02loveslollipop.uk](https://cuantopal3.02loveslollipop.uk).
3. Toca el icono de compartir (el cuadrado con una flecha hacia arriba).
4. Selecciona "Agregar a la pantalla de inicio".
5. Asigna un nombre a la aplicacion (por ejemplo, "Cuanto pal 3") y toca "Agregar".
6. La aplicacion se agregara a tu pantalla de inicio y podras usarla como una aplicacion nativa.    

# Compilando Cuanto pal 3 para iOS
Si deseas correr Cuanto pal 3 en tu dispositivo iOS de forma nativa, puedes compilarlo tu mismo.

## Requisitos
- Un dispositivo iOS con iOS 14 o superior.
- Un Mac con Xcode instalado. 
> Tu version de xcode debe poder compilar para tu version de iOS``
- Un Apple ID para crear un certificado de desarrollador.
> Puedes usar tu cuenta de iCloud pero seria necesario crear nuevos certificados cada semana``
- Un cable USB para conectar tu dispositivo iOS al Mac.
- Un poco de paciencia y ganas de aprender.

## Pasos para compilar Cuanto pal 3
1. Clona el repositorio de Cuanto pal 3 desde Github:
   ```
   git clone https://github.com/02loveslollipop/CuantoPal3
   ```

2. Ejecuta el script the build para instalar las dependencias y compilar la aplicacion:

    ```bash
    cd CuantoPal3
    ./init.sh
    ```

3. Abre el proyecto en Xcode:
    ```
    cd CuantoPal3/capacitor-ios/ios/App
    open App.xcworkspace
    ```

4. Configura tus certificados de desarrollador:
   - En Xcode, ve a "Xcode" > "Preferencias" > "Cuentas".
   - Agrega tu Apple ID y selecciona tu cuenta.
   - Selecciona "Crear un certificado de desarrollador" si no tienes uno.

> Si no tienes un certificado de desarrollador, puedes seguir esta guia para crearlo: [https://steemit.com/xcode/@ktsteemit/xcode-free-provisioning](https://steemit.com/xcode/@ktsteemit/xcode-free-provisioning) (Credit to the author)


5. Conecta tu dispositivo iOS al Mac con un cable USB.
6. Presiona "Confiar" cuando aparezca el mensaje "¿Confiar en esta computadora?" en tu dispositivo iOS.
7. En Xcode, selecciona tu dispositivo iOS en la parte superior izquierda de la ventana.
8. Presiona el botón "Ejecutar" (el triángulo) en Xcode para compilar y ejecutar la aplicación en tu dispositivo iOS.
9. Si todo va bien, la aplicación se instalará y se abrirá en tu dispositivo iOS.
10. Si ves un mensaje de error relacionado con la firma del código, asegúrate de que tu dispositivo esté conectado y que hayas configurado correctamente tus certificados de desarrollador en Xcode.


