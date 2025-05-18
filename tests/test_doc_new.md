<!-- filepath: c:\Users\Katana GF66 11UC\Documents\cp3\CuantoPal3\tests\test_doc.md -->
# Documentación de Pruebas Selenium

Este documento detalla las pruebas Selenium creadas para la aplicación React, basadas en las historias de usuario.

## Historia de Usuario 01: Registro de Calificaciones

**Objetivo:** Probar la capacidad del sistema para permitir a los usuarios ingresar calificaciones y sus pesos porcentuales correspondientes, incluyendo validaciones de entrada.

**Nota Importante:** Todas las pruebas para esta historia de usuario comienzan con un paso de configuración inicial (`_initial_setup`) que maneja la alerta de primer uso (si aparece), navega a la página de configuración y luego regresa a la página principal para asegurar que el formulario de calificaciones esté accesible.

*   **Prueba 1.1: Añadir una única calificación y porcentaje válidos.** (Corresponde a `test_us01_add_single_valid_grade`)
    *   **Descripción:**
        *   Localizar el campo de entrada de la calificación (usando el selector: `input.home__input[placeholder="0.0"][type="number"]`).
        *   Ingresar una calificación válida (ej., "4.0").
        *   Localizar el campo de entrada del porcentaje (usando el selector: `input.home__input[placeholder="0"][type="number"]`).
        *   Ingresar un porcentaje válido (ej., "20").
        *   Localizar y hacer clic en el botón "Agregar nota" (usando el selector: `button.home__add-button`).
        *   Verificar que la calificación y el porcentaje ingresados se reflejen en un aumento en el número de filas de calificación en la lista (contenida en `div.home__grades-container > div.home__grade-row`). La prueba verifica que el contador de filas aumente en 1.

*   **Prueba 1.2: Añadir múltiples calificaciones y porcentajes válidos.** (Corresponde a `test_us01_add_multiple_valid_grades`)
    *   **Descripción:**
        *   Repetir los pasos de la Prueba 1.1 varias veces con diferentes entradas válidas (ej., Calificación: "4.5", Porcentaje: "25%"; Calificación: "3.0", Porcentaje: "30%"). Se utiliza el último par de campos de entrada disponibles en la lista de calificaciones para cada nueva entrada.
        *   Verificar que todas las calificaciones y porcentajes añadidos se reflejen correctamente en un incremento adecuado del número de filas en la lista. La prueba verifica que el contador de filas aumente en 1 por cada par añadido.

*   **Prueba 1.3: Validar entrada de calificación - por debajo del rango válido.** (Corresponde a `test_us01_validate_grade_input_below_range`)
    *   **Descripción:**
        *   Ingresar una calificación inválida (ej., "-1.0", asumiendo rango válido 0.0-5.0) en el campo de entrada de calificación (`input.home__input[placeholder="0.0"][type="number"]`).
        *   Ingresar un porcentaje válido (ej., "20") en el campo de porcentaje (`input.home__input[placeholder="0"][type="number"]`).
        *   Hacer clic en el botón "Agregar nota" (`button.home__add-button`).
        *   Verificar que se muestre un mensaje de error apropiado para la entrada de calificación (el sistema de validación del navegador o un mensaje específico de la aplicación si existe).
        *   Verificar que la calificación inválida no cause un incremento no deseado en la lista de calificaciones o que la aplicación maneje la entrada inválida según lo esperado (ej., no añadiendo la fila o mostrando un error).

*   **Prueba 1.4: Validar entrada de calificación - por encima del rango válido.** (Corresponde a `test_us01_validate_grade_input_above_range`)
    *   **Descripción:**
        *   Ingresar una calificación inválida (ej., "6.0", asumiendo rango válido 0.0-5.0) en el campo de entrada de calificación (`input.home__input[placeholder="0.0"][type="number"]`).
        *   Ingresar un porcentaje válido (ej., "20") en el campo de porcentaje (`input.home__input[placeholder="0"][type="number"]`).
        *   Hacer clic en el botón "Agregar nota" (`button.home__add-button`).
        *   Verificar que se muestre un mensaje de error apropiado.
        *   Verificar que la calificación inválida no se procese incorrectamente.

*   **Prueba 1.5: Validar entrada de porcentaje - valor negativo.** (Corresponde a `test_us01_validate_percentage_input_negative`)
    *   **Descripción:**
        *   Ingresar una calificación válida (ej., "4.0") en el campo de calificación (`input.home__input[placeholder="0.0"][type="number"]`).
        *   Ingresar un porcentaje inválido (ej., "-10") en el campo de entrada de porcentaje (`input.home__input[placeholder="0"][type="number"]`).
        *   Hacer clic en el botón "Agregar nota" (`button.home__add-button`).
        *   Verificar que se muestre un mensaje de error apropiado.
        *   Verificar que la entrada inválida no se procese incorrectamente.

*   **Prueba 1.6: Validar entrada de porcentaje - valor no numérico.** (Corresponde a `test_us01_validate_percentage_input_non_numeric`)
    *   **Descripción:**
        *   Ingresar una calificación válida (ej., "3.0") en el campo de calificación (`input.home__input[placeholder="0.0"][type="number"]`).
        *   Intentar ingresar texto no numérico (ej., "abc") en la entrada de porcentaje (`input.home__input[placeholder="0"][type="number"]`).
        *   Hacer clic en el botón "Agregar nota" (`button.home__add-button`).
        *   Verificar el manejo de errores apropiado (el input type="number" debería prevenir la entrada directa de "abc", pero el test puede verificar el comportamiento si se intenta forzar o si el valor queda vacío/inválido).
        *   Verificar que la entrada inválida no se procese incorrectamente.

## Historia de Usuario 02: Edición y Eliminación de Calificaciones

**Objetivo:** Probar la funcionalidad para editar y eliminar calificaciones previamente ingresadas.

**Nota Importante:** Todas las pruebas para esta historia de usuario comienzan con el `_initial_setup` y asumen que la aplicación está en la página principal de ingreso de calificaciones.

*   **Prueba 2.1: Editar el valor de una calificación existente.** (Corresponde a `test_us02_edit_existing_grade_value`)
    *   **Descripción:**
        *   Añadir una calificación inicial (ej., "3.0", Porcentaje: "20%") usando el método `_add_grade_and_percentage`.
        *   Localizar la primera fila de calificación en la lista (`div.home__grades-container > div.home__grade-row`).
        *   Dentro de esta fila, localizar el campo de entrada de la calificación (usando el selector: `input.home__input[placeholder="0.0"][type="number"]`).
        *   Limpiar el campo existente y luego ingresar un nuevo valor de calificación (ej., "4.5").
        *   Verificar que el atributo `value` del campo de calificación se haya actualizado correctamente al nuevo valor.
        *   Verificar que el número total de filas de calificación permanezca igual después de la edición del valor.

*   **Prueba 2.2: Editar el valor de un porcentaje existente.** (Corresponde a `test_us02_edit_existing_percentage_value`)
    *   **Descripción:**
        *   Añadir una calificación inicial (ej., "3.0", Porcentaje: "20%") usando `_add_grade_and_percentage`.
        *   Localizar la primera fila de calificación en la lista.
        *   Dentro de esta fila, localizar el campo de entrada del porcentaje (usando el selector: `input.home__input[placeholder="0"][type="number"]`).
        *   Limpiar el campo existente y luego ingresar un nuevo valor de porcentaje (ej., "35").
        *   Verificar que el atributo `value` del campo de porcentaje se haya actualizado correctamente al nuevo valor.
        *   Verificar que el número total de filas de calificación permanezca igual después de la edición del valor.

*   **Prueba 2.3: Eliminar una entrada de calificación.** (Corresponde a `test_us02_delete_grade_entry`)
    *   **Descripción:**
        *   Añadir dos calificaciones distintas usando `_add_grade_and_percentage` (ej., "3.0" con "20%", y luego "4.0" con "30%"). Esto establece un escenario con múltiples filas, incluyendo las que contienen datos y las plantillas vacías generadas por la aplicación.
        *   Obtener el número inicial de filas de calificación.
        *   Identificar la fila específica que se desea eliminar. Dado el comportamiento de la aplicación, si se añadieron dos calificaciones, la segunda calificación ingresada residirá en la fila con índice 2 (la tercera fila en la lista general de elementos `div.home__grade-row`).
        *   Dentro de la fila seleccionada para eliminación, localizar y hacer clic en el botón de eliminar (usando el selector: `button.home__remove-button`).
        *   Esperar un breve momento para que la interfaz de usuario se actualice.
        *   Verificar que el número total de filas de calificación haya disminuido en 1 en comparación con el conteo antes de la eliminación.

## Historia de Usuario 03: Alerta por Suma de Porcentajes Inválida

**Objetivo:** Verificar que la aplicación muestre una alerta apropiada cuando el usuario intente realizar un cálculo si la suma de los porcentajes de las notas ingresadas excede el 100%.

**Nota Importante:** Todas las pruebas para esta historia de usuario comienzan con el `_initial_setup` y asumen que la aplicación está en la página principal de ingreso de calificaciones.

*   **Prueba 3.1: Verificar alerta por suma de porcentajes mayor a 100%.** (Corresponde a `test_us03_verify_percentage_sum_alert`)
    *   **Descripción:**
        *   **Añadir Calificaciones con Porcentajes Excesivos:**
            *   Añadir una primera calificación con un peso porcentual alto (ej., Calificación: "3.0", Porcentaje: "70%") utilizando el método `_add_grade_and_percentage`.
            *   Añadir una segunda calificación con otro peso porcentual que, sumado al anterior, exceda el 100% (ej., Calificación: "4.0", Porcentaje: "40%"). La suma total de porcentajes sería 110%.
        *   **Intentar Calcular:**
            *   Localizar y hacer clic en el botón "Calcular" (usando el selector: `button.home__calculate-button`).
        *   **Verificar Alerta:**
            *   Esperar a que aparezca una alerta.
            *   Verificar que el título de la alerta sea "La suma de los porcentajes es mayor al 100%" (usando el selector `div.alert__title`).
            *   Verificar que el mensaje de la alerta sea "Por favor verifica los porcentajes de las notas ingresadas, para que la suma sea menor o igual a 100%." (usando el selector `div.alert__message`).
        *   **Cerrar Alerta:**
            *   Hacer clic en el botón de confirmación de la alerta (ej., "Ok") para cerrarla.
            *   Verificar que la alerta ya no esté visible.

## Historia de Usuario 04: Cálculo del Promedio Ponderado Actual

**Objetivo:** Verificar que la aplicación calcule y muestre correctamente el promedio ponderado actual en la pantalla de resultados, basándose en las calificaciones y porcentajes ingresados.

**Nota Importante:** Todas las pruebas para esta historia de usuario comienzan con el `_initial_setup` y asumen que la aplicación está en la página principal de ingreso de calificaciones. Las pruebas implican navegar a la pantalla de resultados después de hacer clic en "Calcular".

*   **Prueba 4.1: Verificar el cálculo y la visualización del promedio ponderado actual.** (Corresponde a `test_us04_verify_calculation_of_current_weighted_average`)
    *   **Descripción:**
        *   **Paso 1: Añadir primera calificación y calcular.**
            *   Asegurarse de estar en la página principal.
            *   Añadir una primera calificación y su porcentaje (ej., Calificación: "4.5", Porcentaje: "20%") usando el método `_add_grade_and_percentage`.
            *   Localizar y hacer clic en el botón "Calcular" (usando el selector: `button.home__calculate-button`).
            *   Esperar la navegación a la página de resultados (URL debe contener `/result`).
            *   Localizar el elemento que muestra el promedio ponderado actual en la página de resultados (usando el selector: `p.result__card-current`).
            *   Extraer el valor del promedio del texto (ej., de "Actualmente tienes un promedio de 0.9 en el 20% de la materia.", extraer "0.9").
            *   Calcular el promedio esperado: `(4.5 * 20) / 100 = 0.9`.
            *   Verificar que el promedio mostrado coincida con el promedio esperado.
        *   **Paso 2: Añadir segunda calificación y recalcular.**
            *   Navegar de regreso a la página principal usando el botón de navegación "atrás" (utilizando múltiples estrategias de selección para mayor robustez):
                *   Intentar primero con un selector CSS simple: `nav.nav-bar > button.nav-bar__button:first-child`
                *   Si falla, intentar con XPath: `//button[contains(@class, 'nav-bar__button') and .//span[contains(@class, 'back-icon')]/svg[contains(@class, 'lucide-chevron-left')]]`
                *   Si ambos fallan, buscar la barra de navegación y seleccionar el primer botón en ella
            *   Añadir una segunda calificación y su porcentaje (ej., Calificación: "3.0", Porcentaje: "30%").
            *   Hacer clic nuevamente en el botón "Calcular".
            *   Esperar la navegación a la página de resultados.
            *   Localizar y extraer el nuevo promedio ponderado.
            *   Calcular el promedio esperado: `(4.5 * 20 + 3.0 * 30) / 100 = (90 + 90) / 100 = 1.8`.
            *   Verificar que el promedio mostrado coincida con el nuevo promedio esperado.
        *   **Paso 3: Añadir tercera calificación y recalcular.**
            *   Navegar de regreso a la página principal usando la misma estrategia robusta para encontrar el botón de navegación.
            *   Añadir una tercera calificación y su porcentaje (ej., Calificación: "5.0", Porcentaje: "50%").
            *   Hacer clic nuevamente en el botón "Calcular".
            *   Esperar la navegación a la página de resultados.
            *   Localizar y extraer el nuevo promedio ponderado.
            *   Calcular el promedio esperado: `(4.5 * 20 + 3.0 * 30 + 5.0 * 50) / 100 = (90 + 90 + 250) / 100 = 430 / 100 = 4.3`.
            *   Verificar que el promedio mostrado coincida con el nuevo promedio esperado.
    
    *   **Mejoras de Robustez:**
        *   La prueba incluye varias estrategias para localizar el botón de navegación, incrementando la confiabilidad en entornos CI.
        *   Se toman capturas de pantalla en momentos clave para facilitar la depuración en caso de fallos.
        *   Se implementa un manejo de errores mejorado con mensajes de registro detallados.
        *   La función `_add_grade_and_percentage` verifica si es necesario crear una nueva fila o utilizar una existente, evitando problemas con la acumulación de calificaciones.
        *   La extracción del promedio incluye métodos alternativos para mayor confiabilidad.

## Historia de Usuario 05: Cálculo de la Nota Mínima Necesaria

**Objetivo:** Verificar que la aplicación calcule y muestre correctamente la nota mínima necesaria para aprobar la materia basándose en las calificaciones actuales, sus porcentajes y la nota de aprobación configurada.

**Nota Importante:** Todas las pruebas para esta historia de usuario comienzan con el `_initial_setup` y aseguran que la nota de aprobación esté configurada en 3.0 (valor predeterminado).

*   **Prueba 5.1: Calcular la nota necesaria para aprobación.** (Corresponde a `test_us05_calculate_required_grade_for_approval`)
    *   **Descripción:**
        *   Configurar la nota de aprobación en 3.0 (valor predeterminado).
        *   Añadir una calificación con un porcentaje que no complete el 100% (ej., Calificación: "2.0", Porcentaje: "50%").
        *   Hacer clic en el botón "Calcular" para navegar a la página de resultados.
        *   Localizar el elemento que muestra la nota necesaria en el porcentaje restante.
        *   Verificar que la nota necesaria mostrada coincida con la esperada (4.0 en este caso).
        *   Fórmula para calcular la nota necesaria: `(Nota aprobación * 100 - Suma de (nota actual * porcentaje)) / porcentaje restante`
        *   Para este ejemplo: `(3.0 * 100 - (2.0 * 50)) / 50 = (300 - 100) / 50 = 200 / 50 = 4.0`

*   **Prueba 5.2: Verificar escenario de imposibilidad de aprobación.** (Corresponde a `test_us05_impossible_to_approve_scenario`)
    *   **Descripción:**
        *   Configurar la nota de aprobación en 3.0 (valor predeterminado).
        *   Añadir una calificación baja con un alto porcentaje que matemáticamente haga imposible alcanzar la nota de aprobación incluso con nota máxima en el porcentaje restante (ej., Calificación: "1.0", Porcentaje: "80%").
        *   Hacer clic en el botón "Calcular" para navegar a la página de resultados.
        *   Verificar que se muestre un mensaje indicando que no es posible aprobar la materia.

*   **Prueba 5.3: Verificar escenario de materia ya aprobada.** (Corresponde a `test_us05_already_approved_scenario`)
    *   **Descripción:**
        *   Configurar la nota de aprobación en 3.0 (valor predeterminado).
        *   Añadir una calificación que por sí sola ya garantice la aprobación de la materia (ej., Calificación: "4.0", Porcentaje: "80%").
        *   Hacer clic en el botón "Calcular" para navegar a la página de resultados.
        *   Verificar que se muestre un mensaje indicando que ya se ha aprobado la materia.
