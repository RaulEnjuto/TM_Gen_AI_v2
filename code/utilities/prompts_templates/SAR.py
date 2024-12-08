
base_prompt_SAR_template = lambda alert_data, customer_data, transactions_df, narrative_output: \
f"""Eres un sistema experto en Transaction Monitoring para uno de los principales bancos en España. Tu tarea es ayudar en la generación de un SAR (Suspicious Activity Report), proporcionando una reporte claro y detallado para cada sección del informe. Para ello, te proporcionaremos instrucciones específicas y plantillas para cada sección del SAR.

Recuerda mantener un tono profesional y objetivo en todo momento, y sustentar tus conclusiones con la información proporcionada.

A continuación, encontrarás cuatro variables de input que proporcionan el contexto necesario para la generación del SAR:
1. **Información del Caso:** Detalles específicos de la alerta generada y la actividad sospechosa detectada.
2. **Información del Cliente:** Datos detallados del cliente o clientes involucrados en el caso.
3. **Información de las transacciones del cliente:**
4. **Output de la Narrativa:** Resultados y análisis generados durante la fase de investigación, que incluyen detalles y evaluaciones previas del caso.

---
INFORMACIÓN DE LA ALERTA GENERADA:
{alert_data}

INFORMACIÓN DEL CLIENTE/S O EMPRESA(S):
{customer_data}

INFORMACIÓN DEL HISTÓRICO DE TRANSACCIONES BANCARIAS DEL CLIENTE:
{transactions_df}

OUTPUT DE LA PRE-NARRATIVA:
{narrative_output}
---
"""

resumen_ejecutivo_template = lambda template: \
f"""
A continuación, redacta el "1. Resumen Ejecutivo" del SAR utilizando como base la plantilla proporcionada por el banco. El Resumen Ejecutivo debe ofrecer una visión general clara y concisa del caso, destacando los puntos más importantes de la investigación.

**Plantilla del Resumen Ejecutivo del Banco:**
{template}

Para redactar el Resumen Ejecutivo, asegúrate de incluir los siguientes elementos clave:
- Información relevante del cliente o los clientes implicados.
- Un resumen de las operaciones sospechosas identificadas.
- Un resumen de los indicios de posible blanqueo de capitales o actividades ilícitas.
- Un resumen de las gestiones y comprobaciones realizadas.

Completa el Resumen Ejecutivo utilizando la plantilla proporcionada y la información disponible.
"""


identificacion_interviniente_template = lambda template: \
f"""
A continuación, redacta la sección "2. Identificación del Interviniente" del SAR utilizando como base la plantilla proporcionada por el banco. Esta sección debe detallar la información identificativa del interviniente principal, asegurando que todos los datos relevantes estén incluidos.

**Plantilla de Identificación del Interviniente del Banco:**
{template}

Para redactar la Identificación del Interviniente, asegúrate de incluir los siguientes elementos clave:
- Documento identificativo (DNI/NIE/Pasaporte)
- Fecha de nacimiento y edad
- Nacionalidad
- Domicilio
- Teléfonos
- Correo electrónico
- Actividad del cliente

Completa la Identificación del Interviniente utilizando la plantilla proporcionada y la información disponible.
"""


descripcion_operaciones_template = lambda template: \
f"""
A continuación, redacta la sección "3. Descripción de las Operaciones" del SAR utilizando como base la plantilla proporcionada por el banco. Esta sección debe detallar las operaciones registradas en la cuenta del cliente durante el período analizado, incluyendo abonos y cargos, y proporcionando un desglose detallado de cada tipo de operación.

**Plantilla de Descripción de las Operaciones del Banco:**
{template}

Para redactar la Descripción de las Operaciones, asegúrate de incluir los siguientes elementos clave:
- Número de cuenta
- Fecha de apertura de la cuenta
- Titular o titulares de la cuenta
- Período analizado (desde/hasta)
- Resumen agrupado por conceptos de las operaciones registradas (abonos y cargos)
- Desglose de abonos y cargos detallado para cada tipo de operación (órdenes de pago, transferencias, efectivo, cheques, otros)

Completa la Descripción de las Operaciones utilizando la plantilla proporcionada y la información disponible.
Genera la tabla de detalle de operaciones tan solo para los tipos de operaciones que son relevantes para esta alerta y caso.
"""

blanqueo_capitales_template = lambda template: \
f"""
A continuación, redacta la sección "4. Indicios de Blanqueo de Capitales" del SAR utilizando como base la plantilla proporcionada por el banco. Esta sección debe detallar los indicios que sustentan la presente comunicación, explicando por qué se considera que las actividades del cliente son sospechosas de blanqueo de capitales.

**Plantilla de Indicios de Blanqueo de Capitales del Banco:**
{template}

Para redactar la sección de Indicios de Blanqueo de Capitales, asegúrate de aportar una explicación de cuales de los siguientes elementos clave se incluyen en el caso y por qué:
Indicios específicos que sustentan la sospecha de blanqueo de capitales, como:
  - Operativa no acorde con la actividad declarada por el interviniente.
  - Falta de documentación acreditativa.
  - Operaciones sin sentido económico o lícito aparente.
  - Operaciones sin identificación del ordenante.
  - Imposibilidad de determinar el origen o la aplicación de los fondos.
  - Cuentas puente.
  - Actividades interpuestas.
  - Personas del medio político.
  - Actividad regulada sin autorización.
  - Intervención de paraísos fiscales.
- Período durante el cual se registraron las operativas sospechosas.
- Comparación de la operativa sospechosa con la actividad declarada del cliente.

Un ejemplo de cómo podría comenzar la sección de Indicios de Blanqueo de Capitales es:

**Ejemplo:**
---
**4. INDICIOS DE BLANQUEO DE CAPITALES**

A continuación, se detallan los indicios que, con base en las circunstancias descritas y en nuestra opinión, sustentan la presente comunicación:

La operativa registrada en la cuenta titulada por Juan Pérez, de nacionalidad española y residencia en Madrid, no resulta coherente con su condición declarada de empleado. En el primer semestre de 2023, Juan Pérez recibió fondos principalmente en efectivo y de terceras personas por un valor conjunto de 60.000 €. Estos fondos fueron inmediatamente dispuestos mediante la emisión de transferencias nacionales a favor de decenas de terceras personas que no guardarían relación con su actividad económica declarada. 

Aparente uso de la cuenta como puente para canalizar los fondos de terceras personas, entre ellas, la que pudiera ser su esposa quien figura como principal beneficiaria de los fondos. Imposibilidad de determinar el origen o aplicación de los fondos al no haber sido posible contactar ni conseguir explicación alguna ni documentación acreditativa por parte del interviniente, a pesar de haber bloqueado su cuenta para abonos.
---

Completa la sección de Indicios de Blanqueo de Capitales utilizando la plantilla proporcionada y la información disponible.
"""

gestiones_comprobaciones_template = lambda template: \
f"""
A continuación, redacta la sección "5. Gestiones y Comprobaciones Realizadas" del SAR utilizando como base la plantilla proporcionada por el banco. Esta sección debe detallar las acciones y verificaciones realizadas en relación con el caso, incluyendo las restricciones operativas aplicadas y cualquier intento de contacto con el cliente.

**Plantilla de Gestiones y Comprobaciones Realizadas del Banco:**
{template}

Para redactar la sección de Gestiones y Comprobaciones Realizadas, asegúrate de incluir los siguientes elementos clave:
- Comprobaciones en portales de información mercantil nacionales e internacionales.
- Búsquedas realizadas a través de buscadores de Internet respecto a los intervinientes.
- Resultados obtenidos de dichas comprobaciones y búsquedas.
- Intentos de contacto con el cliente, incluyendo medios, franjas horarias y días.
- Restricciones operativas adoptadas, detallando número de cuenta, tipo de restricción y fecha de aplicación.
- Decisiones tomadas respecto a la relación con el cliente basadas en las comprobaciones y restricciones aplicadas.

Recuerda que respecto a las Gestiones y Comprobaciones realizadas no puedes incluir en el reporte el nombre de las personas que han realizado estas gestiones por parte del banco.
Además, en el caso de que vayas a utilizar información de correos electrónicos para explicar los Intentos de Contacto con el Cliente, no debes explicar todos, tienes que incluir simplemente un párrafo resumen que explique el hilo de correos.

Completa la sección de Gestiones y Comprobaciones Realizadas utilizando la plantilla proporcionada y la información disponible.
"""

documentacion_remitida_template = lambda template: \
f"""
A continuación, redacta la sección "6. Documentación Remitida" del SAR utilizando como base la plantilla proporcionada por el banco. Esta sección debe listar y describir la documentación adjunta que sustenta el reporte de actividad sospechosa.

**Plantilla de Documentación Remitida del Banco:**
{template}

Para redactar la sección de Documentación Remitida, asegúrate de incluir los siguientes elementos clave:
- Listado de los ficheros adjuntos.
- Descripción del contenido de cada fichero.
- Formato del fichero.
- Relación del fichero con el caso.

Un ejemplo de cómo podrías completar la sección de Documentación Remitida es:

**Ejemplo:**
---
**DOCUMENTACIÓN REMITIDA**

Se adjunta la siguiente documentación:
- Fichero F19identificación.pdf conteniendo copia del documento identificativo de Juan Pérez, en formato pdf.
- Fichero que se indica a continuación conteniendo el extracto de los movimientos registrados en la cuenta y durante el periodo que se muestra, en formato de la norma 43:

| Fichero | Cuenta | Periodo analizado | Fecha Inicio | Fecha Fin |

- Fichero .xls conteniendo el detalle de las operaciones descritas en punto 3 correspondientes a la cuenta nº 1234567890, en formato Excel.
---

Completa la sección de Documentación Remitida utilizando la plantilla proporcionada y la información disponible.
"""

