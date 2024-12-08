
base_prompt_template = lambda alert_data, customer_data, transactions_df, playbook, alert_assessment: \
f"""Eres un sistema experto en monitoreo y análisis de transacciones bancarias para uno de los principales bancos en España. Tu objetivo es rastrear, analizar y documentar exhaustivamente las transacciones financieras para identificar y prevenir actividades fraudulentas o ilegales.

Para realizar esta tarea, recibirás información detallada sobre un caso que ha generado una alerta, incluyendo:
- Un archivo JSON con el detalle de la alerta generada.
- Un archivo JSON con información sobre el/los cliente(s) y/o empresa(s) implicados.
- Una tabla en formato Markdown con el histórico de transacciones bancarias del cliente.
- Documentación adicional obtenida durante la investigación del caso.

Tu tarea principal es escribir una narrativa clara y detallada sobre el caso a analizar para dar una recomendación al analista. Debes ayudar a los analistas respondiendo de manera clara y concisa las preguntas pertinentes a cada parte del caso usando únicamente información veraz y disponible sobre el caso.

Esta es información de la base de conocimiento del banco sobre gestión de alertas de Transaction Monitoring:
---
Información sobre el procedimiento y tareas de Gestión de Alertas de Transaction Monitoring:
{playbook}
 
Información sobre la tipología de la alerta referente al caso que se va a analizar:
{alert_assessment}
---

Recuerda mantener un tono profesional y objetivo en todo momento, y sustentar tus conclusiones con la información proporcionada.

A continuación, esta es la información base proporcionada sobre el caso:

---
INFORMACIÓN DE LA ALERTA GENERADA
{alert_data}

INFORMACIÓN DEL CLIENTE/S O EMPRESA(S)
{customer_data}

INFORMACIÓN DEL HISTÓRICO DE TRANSACCIONES BANCARIAS DEL CLIENTE
{transactions_df}
---
"""

naturaleza_alerta_template = \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- ¿Cuál es la naturaleza de la alerta?
Para responder esta pregunta, apóyate en analizar total o parcialmente algunos de los siguientes puntos:

- Indica si la alerta ha sido generada de forma manual o automática (se trata de manual cuando sea una alerta de empleado, oficio o requerimiento judicial. El resto son automáticas)
- Indica la naturaleza de la alerta
- Indica que día se generó la alerta
- Indica cual es el importe que generó la alerta
- Indica quien es el titular y el número de cuenta sobre el que se ha generado la alerta

Un ejemplo o plantilla de respuesta para esta pregunta es:

### Naturaleza de la alerta
Se trata de una alerta generada de forma **[manual/automática]**, cuya naturaleza es **«XXXXX» (XXXXX)** generada el día **DD/MM/YYYY** por un importe de **XXXX €** en la cuenta titularidad de **[Nombre y Apellidos]** con número **[Código IBAN en formato XXXX XXXX XX XXXXXXXXXX]**.


Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como XXXX.
"""

principal_implicado_template = lambda informacion_externa: \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- ¿Quién es el principal implicado?
Para responder esta pregunta, apóyate en analizar total o parcialmente algunos de los siguientes puntos:
*Utiliza la siguiente información obtenida de proveedores externos o de búsquedas por internet, si esta disponible (puede estar vacía):
{informacion_externa}

Si es una persona física:
- Indica el nombre del interviniente principal
- Indica la fecha de alta del interviniente principal
- Indica el DNI/NIE/Pasaporte del interviniente principal
- Indica la edad en años y entre paréntesis la fecha de nacimiento del interviniente principal 
- Indica la nacionalidad (NO el país, sino la nacionalidad correcta) del interviniente principal y entre paréntesis el lugar de nacimiento en caso de ser un lugar distinto a la nacionalidad
- Indica el lugar de residencia del interviniente principal
- Indica la actividad laboral y los ingresos anuales del interviniente principal
- Indica la última fecha de actualización del KYC del interviniente principal
- Indica, sólo si existe, cualquier información relevante obtenida de proveedores externos (por ejemplo, Axesor, D&B o el Registro Mercantil) o de búsquedas en internet.

*Además, en caso de ser la persona física titular real de una mercantil cliente de la Entidad:
- En caso de ser titular real de una mercantil y que sea cliente de la Entidad indicar el nombre de la mercantil y que figura como titular real de la misma
- En caso de ser titular real de una mercantil y que no sea cliente de la Entidad, solamente indica el nombre de la mercantil de la cual es titular real
- Indica la fecha de alta de la mercantil 
- Indica la actividad social de la mercantil
- Indica los beneficios netos de la mercantil 
- Indica que la mercantil ha sido incluida como interviniente al ser el titular real el interviniente principal objeto de análisis

Si es una persona jurídica:
- Indica el nombre de la mercantil que es interviniente principal
- Indica la fecha de alta de la mercantil interviniente principal
- Indica la fecha de constitución de la mercantil interviniente principal
- Indica el CIF del interviniente principal
- Indica el domicilio social de la mercantil interviniente principal
- Indica la actividad social de la mercantil interviniente principal
- Indica los beneficios netos de la mercantil interviniente principal
- Indica el titular real de la mercantil interviniente principal
- Indica la última fecha de actualización del KYC del interviniente principal
- Indica, sólo si existe, cualquier información relevante obtenida de proveedores externos (por ejemplo, Axesor, D&B o el Registro Mercantil) o de búsquedas en internet.

*Además, en caso de ser el titular real cliente de la Entidad:
- En caso de que el titular real de la mercantil sea cliente de la Entidad indica su nombre y que es titular real de la mercantil 
- En caso de que el titular real de la mercantil no sea cliente de la Entidad indica solamente su nombre y que es el titular real de la mercantil
- Indica la fecha de alta del titular real
- Indica el DNI/NIE/Pasaporte del titular real 
- Indica la edad en años del titular real
- Indica la nacionalidad (NO el país, sino la nacionalidad correcta) y lugar de residencia del titular real
- Indica que ha sido incluido como interviniente al ser titular real de la mercantil interviniente objeto de análisis

Dos ejemplos diferentes o plantilla de respuesta para esta pregunta en función de si se trata de Persona Física o Persona Jurídica son:

### Principal implicado 
Opción 1:

El interviniente principal es **[Nombre y Apellidos]**, cliente de la Entidad desde el **DD/MM/YYYY**, con DNI/NIE/Pasaporte **XXXX**, de **XX** años (**[fecha de nacimiento]**), nacionalidad **[NO el nombre del país, sino la nacionalidad correcta]** (nacido en **[lugar]**) y residente en **[lugar]**. El interviniente declara ser **[actividad laboral]** con unos ingresos anuales estimados de **XX €**.
(Además, en caso de ser la persona física titular real de una mercantil cliente de la Entidad)
Figura como titular real de la mercantil **[nombre de la mercantil]**, cliente de la Entidad desde el **DD/MM/YYYY**, cuya actividad social es **[actividad social]** y con unos beneficios netos de **XX €** al año. La mercantil ha sido asimismo incluida como interviniente al ser el titular real el interviniente principal objeto de análisis.

La última fecha de actualización del KYC del interviniente principal es **DD/MM/YYYY*

(Resto de información a indicar si esta disponible)

Opción 2:

El interviniente principal es **[nombre de la mercantil]**, cliente de la Entidad desde el **DD/MM/YYYY **. Se trata de una mercantil constituida el **DD/MM/YYYY**, con domicilio social en **[domicilio social] **, cuya actividad social es **[actividad social] ** y con unos beneficios netos de **XX €** al año. Figura como titular real de la mercantil **[nombre de la mercantil] **.
(Además, en caso de ser el titular real cliente de la entidad)
Figura como titular real **XXXXX**, cliente de la Entidad desde el **DD/MM/YYYY**, con DNI/NIE/Pasaporte **XXXX**, de **XX años, nacionalidad **[NO el país, sino la nacionalidad correcta]** y residente en **XXXX**. Ha sido incluido asimismo como interviniente al ser titular real de la mercantil objeto de análisis.

La última fecha de actualización del KYC del interviniente principal es **DD/MM/YYYY*

(Resto de información a indicar si esta disponible)

---

Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como XXXX.
"""

contexto_historico_template = \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- ¿Cuál es el contexto histórico del cliente?
Para responder esta pregunta, apóyate en analizar total o parcialmente algunos de los siguientes puntos:

- Indica si se trata de un cliente con riesgo alto, medio o bajo
- Indica si se trata de un cliente activo o inactivo (se trata de un cliente inactivo cuando no haya operado en los últimos 4 meses)
- Indica la antigüedad del cliente en años o meses
- Indica el número total de cuentas del cliente
- Indica el número de cuenta analizado
- Indica el total de abonos de la cuenta durante el periodo analizado 
- Indica cuales son los principales abonos más relevantes de la cuenta (aquellos que conformen más de un 5% en la columna Porcentaje Total del importe de la tabla de Abonos), excepto los catalogados como “Otros”, ordenados de mayor a menor y entre paréntesis el total de cada uno de ellos (i.e. ingresos en efectivo (50.000 €)) 
- Indica el total de cargos de la cuenta durante el periodo analizado
- Indica cuales son los principales cargos más relevantes de la cuenta (aquellos que conformen más de un 5% en la columna Porcentaje Total del importe de la tabla de Cargos), excepto los catalogados como “Otros”, ordenados de mayor a menor y entre paréntesis el total de cada uno de ellos (i.e. transferencias nacionales emitidas (50.000 €))
*Puntos adicionales:
- Indica si el cliente es un PEP (Persona Expuesta Políticamente) en caso afirmativo
- Indica y describe brevemente los documentos disponibles en la biblioteca documental del cliente en caso de existir alguno
- Indica si el cliente ha sido objeto de oficios y en caso afirmativo el número de oficio, fecha del oficio y en qué consistió 
- Indica si el cliente ha sido objeto de alertas previas y en caso afirmativo el número de expediente realizado, fecha del expediente y la decisión de este

Un ejemplo o plantilla de respuesta para esta pregunta es:

### Contexto histórico del cliente

Se trata de un cliente de la Entidad con **riesgo [alto/medio/bajo]**, **[activo/inactivo]** y con una antigüedad en la Entidad de **XX [años/meses]**. El interviniente dispone de un total de **[cantidad de cuentas]** cuentas de su titularidad, observándose en la cuenta número **XXX** durante el periodo de análisis un total de abonos de **XXX €** principalmente provenientes de **XXX (XXX €)**, **XX** y **XXX**, así como un total de cargos por importe de **XX €** principalmente mediante **XX**, **XX** y ***XXX***. [TEXTO ADICIONAL correspondiente a los *Puntos adicionales]…

Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como XXXX.
"""

analisis_operativa_template = lambda tabla_abonos, tabla_cargos: \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- Análisis de la operativa del cliente
Para responder esta pregunta, apóyate en analizar los siguientes puntos, generando tres párrafos distintos (un párrafo sobre el total de abonos y cargos, la tabla de Abonos en formato Markdown, un párrafo sobre la descripción de abonos y uno para la descripción de cargos) y siguiendo un orden correcto para cada tipo de operativa (por ejemplo, hablar todo lo correspondientes a ingresos, luego todo lo correspondiente a transferencias, etc. sin saltar de un tema a otro):

+ Total de abonos y cargos:
- Indica el únicamente el total de abonos durante el periodo analizado 
- Indica el únicamente el total de cargos durante el periodo analizado
- NO es necesario indicar en qué consiste la principal operativa

+ Descripción abonos (sólo los principales más relevantes, es decir, aquellos que conformen más de un 5% en la columna Porcentaje Total del importe de la tabla de Abonos):
- IMPORTANTE: Muestra de manera exacta la siguiente tabla de Abonos en Markdown que te proporciono a continuación:
{tabla_abonos}

- Indica de mayor a menor los principales abonos, el número de operaciones de cada tipo de abono y entre paréntesis el importe de cada uno de ellos (i.e. 28 transferencias nacionales (88.000 €)). 
- Indica asimismo para las transferencias nacionales recibidas todos los ordenantes, el "Concepto" o "Descripción del movimiento" de las transacciones y entre paréntesis el importe de cada uno de ellos (si no se dispone información explícita de los principales ordenantes, inferir esa información de campos como el "Concepto" o "Descripción del movimiento" de las transacciones).
- Indica asimismo para las transferencias internacionales recibidas todos los ordenantes, el "Concepto" o "Descripción del movimiento" de las transacciones y países de origen de los fondos y entre paréntesis el importe de cada uno de ellos (si no se dispone información explícita de los principales ordenantes, inferir esa información de campos como el "Concepto" o "Descripción del movimiento" de las transacciones).
- Indica asimismo para los ingresos en efectivo quien los ha realizado principalmente, las oficinas donde se han realizado principalmente y donde se encuentran y en caso de haber agrupación de ingresos en alguno de los meses indicarlo, y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para los ingresos de nómina el ordenante y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para los préstamos el ordenante y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para los ingresos de cheque las principales cuentas de origen de los fondos y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para las órdenes de pago todos los ordenantes y países de origen en caso de no ser España, y entre paréntesis el importe de cada uno de ellos (si no se dispone información explícita de los principales ordenantes, inferir esa información de campos como el "Concepto" o "Descripción del movimiento" de las transacciones).

+ Descripción cargos (sólo los principales más relevantes, es decir, aquellos que conformen más de un 5% en la columna Porcentaje Total del importe de la tabla de Cargos):
- IMPORTANTE: Muestra de manera exacta la siguiente tabla de Cargos en Markdown que te proporciono a continuación:
{tabla_cargos}

- Indica de mayor a menor los principales cargos, el número de operaciones de cada tipo de abono y entre paréntesis el importe de cada uno de ellos (i.e. 28 retiradas de efectivo (88.000 €)). 
- Indica asimismo para las transferencias nacionales emitidas todos los beneficiarios, el "Concepto" o "Descripción del movimiento" de las transacciones y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para las transferencias internacionales emitidas todos los beneficiarios, el "Concepto" o "Descripción del movimiento" de las transacciones y países de destino de los fondos y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para las retiradas de efectivo las oficinas donde se han realizado principalmente y donde se encuentran y en caso de haber agrupación de retiradas de efectivo en alguno de los meses indicarlo, y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para las emisiones de cheque todos los beneficiarios de los fondos y las principales cuentas de destino de los fondos, y entre paréntesis el importe de cada uno de ellos.
- Indica asimismo para las órdenes de pago todos los beneficiarios y países de de destino en caso de no ser España, y entre paréntesis el importe de cada uno de ellos.

Un ejemplo o plantilla de respuesta para esta pregunta es:

### Análisis de la operativa del cliente

Durante el periodo analizado se observan unos abonos por importe total de **XX €** y unos cargos por importe total de **XX €**.  La principal operativa de abonos consiste en **XX**, **XX** y **XXX**; fondos que se disponen mediante **XX**, **XX** y **XXX**… La principal operativa de cargos consiste en…  


Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como XXXX.
"""

documentacion_adicional_template = lambda documentacion_adicional: \
f"""Dada la siguiente INFORMACIÓN DE LA DOCUMENTACIÓN APORTADA y COMUNICACIONES CON LA OFICINA DEL BANCO:
{documentacion_adicional}

Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- Documentación y explicaciones aportadas
Para responder a esta pregunta, analiza la documentación y las explicaciones proporcionadas por el cliente, así como cualquier comunicación relevante con la oficina del banco. Genera dos secciones distintas: una para la documentación aportada y otra para las comunicaciones con la oficina.

### Documentación aportada (si existe y procede):
- Lista y describe la documentación adicional proporcionada por el cliente para justificar su operativa (por ejemplo, contratos, facturas, extractos bancarios, etc.).
- Indica cómo cada documento respalda las explicaciones del cliente.
- Si es relevante, añade fragmentos o citas de los documentos que clarifiquen la operativa del cliente.
- No mencionar qué documentación se ha solicitado por parte de la entidad en esta sección.

### Comunicaciones con la oficina del banco por orden cronológico (si existe y procede):
IMPORTANTE: Ordenar las comunicaciones por orden cronológico (de la comunicación más antigua con la oficina del banco a la más reciente)
- Resume las comunicaciones relevantes entre el analista y la oficina del banco por orden cronológico (de más antiguo a más reciente).
- Indica el nombre y apellidos de las personas con las que se ha comunicado el analista, sin proporcionar direcciones de correo electrónico.
- Indica cualquier explicación adicional proporcionada indirectamente por el cliente a través de estas comunicaciones.
- Incluye detalles sobre las fechas de las comunicaciones y el contenido clave que apoye o contradiga las explicaciones del cliente.

Un ejemplo o plantilla de respuesta para esta pregunta es:

### Documentación y explicaciones aportadas

##### Documentación aportada:
El cliente ha proporcionado los siguientes documentos para justificar su operativa:
- **Contrato de compraventa**: Este documento respalda la transacción de **XX €** indicando que **[detalle del contrato]**.
- **Factura de servicios**: La factura justifica el abono de **XX €** recibido el **DD/MM/YYYY**, mostrando que **[detalle de la factura]**.
- **Extracto bancario**: El extracto muestra **[detalle del extracto]**, coincidiendo con las transacciones sospechosas.

##### Comunicaciones con la oficina del banco:
- En las comunicaciones con la oficina del banco, se ha mencionado que el cliente **[explicación adicional]**. La oficina ha indicado que **[detalle de la comunicación]**. Estas comunicaciones ocurrieron principalmente entre **[fecha]** y **[fecha]**.
- En una comunicación más reciente, el director de la oficina ha mencionado que **[detalle de la comunicación]**, contradiciendo la explicación del cliente.
- En la última comunicación, el analista ha solicitado **[detalle de la solicitud]**, a la espera de una respuesta por parte de la oficina.


Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como XXXX.
"""

intervinientes_adicionales_template = lambda json_interviniente_cliente, transactions_interviniente_df, tabla_abonos_interviniente, tabla_cargos_interviniente: \
f"""Dada la siguiente información sobre los intervinientes adicionales, proporcionada en formato JSON:
{json_interviniente_cliente}

Si no se ha proporcionado uno o más JSONs de intervinientes adicionales en este punto del mensaje, indica que no se han identificado intervinientes adicionales como respuesta a esta sección.

Y el histórico de transacciones de los intervinientes adicionales (ten en cuenta que los intervinientes adicionales cada uno tendrá una cuenta y un nombre):
{transactions_interviniente_df}

Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta a continuación:
- **Análisis de la operativa de intervinientes adicionales**

El análisis debe incluir las siguientes secciones:

### Total de abonos y cargos:
- Indica de manera clara el total de abonos durante el periodo analizado.
- Indica de manera clara el total de cargos durante el periodo analizado.
- No es necesario detallar la operativa en esta sección, solo los totales globales de abonos y cargos.

### Descripción de los abonos:
- Proporciona un análisis detallado de los principales abonos (aquellos que representen más de un 5% del total de abonos).
- Incluye la siguiente tabla de Abonos en formato Markdown:
{tabla_abonos_interviniente}

- Para cada tipo de abono relevante, incluye la siguiente información:
  1. **Transferencias recibidas:** Detalla los ordenantes, el concepto o descripción de la transacción, y entre paréntesis el importe de cada transacción.
  2. **Ingresos en efectivo:** Describe quién ha realizado estos ingresos, las principales oficinas donde se efectuaron y cualquier concentración de ingresos por meses.
  3. **Ingresos de nómina, préstamos y cheques:** Especifica el ordenante y el importe de cada una de estas transacciones.

### Descripción de los cargos:
- Proporciona un análisis detallado de los principales cargos (aquellos que representen más de un 5% del total de cargos).
- Incluye la siguiente tabla de Cargos en formato Markdown:
{tabla_cargos_interviniente}

- Para cada tipo de cargo relevante, incluye la siguiente información:
  1. **Transferencias emitidas:** Detalla los beneficiarios, el concepto o descripción de la transacción, y entre paréntesis el importe de cada transacción.
  2. **Retiradas de efectivo:** Describe las principales oficinas donde se realizaron y si hubo concentración de retiradas en ciertos meses.
  3. **Emisión de cheques y órdenes de pago:** Indica los beneficiarios y las cuentas de destino de los fondos, así como los países si no son España.

### Relación entre intervinientes adicionales y principal implicado:
- Explica brevemente la posible relación entre el interviniente adicional y el principal implicado, basándote en las transacciones o conexiones observadas.
- Incluye detalles relevantes que puedan sugerir algún tipo de vínculo (p. ej., transferencias frecuentes entre ambos, compartición de oficinas, actividad similar, etc.).
- Si no se ha detectado una relación directa, pero existen patrones operativos similares, menciónalo.
- Si no se ha identificado ninguna relación significativa, indícalo claramente.

**Un ejemplo de respuesta podría ser:**

### Análisis de la operativa de intervinientes adicionales

Durante el periodo analizado del interviniente adicional **[Nombre]**, se observan abonos por un total de **XX €** y cargos por un total de **XX €**.

#### Descripción de los abonos:
| Tipo de Abono | Número de Transacciones | Importe Total (€) |
| ------------- | ----------------------- | ----------------- |
| Transferencias Nacionales | 28 | 88,000 |
| Ingresos en Efectivo | 12 | 50,000 |
(… incluir tabla detallada y descripciones de transacciones)

#### Descripción de los cargos:
| Tipo de Cargo | Número de Transacciones | Importe Total (€) |
| ------------- | ----------------------- | ----------------- |
| Transferencias Nacionales Emitidas | 18 | 75,000 |
| Retiradas de Efectivo | 9 | 40,000 |
(… incluir tabla detallada y descripciones de transacciones)

### Ejemplo: Relación con el principal implicado:
Se ha detectado que el interviniente adicional **[Nombre]** ha realizado múltiples transferencias hacia la cuenta del principal implicado, lo que sugiere una conexión operativa significativa. Las transferencias tienen un patrón recurrente, especialmente en los meses de **[Mes]** y **[Mes]**.
"""

recomendacion_prenarrativa_template = \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:

### Recomendación inicial para el caso

Para responder, analiza los siguientes puntos de manera total o parcial:

- Indica si se recomienda **archivar** el expediente si se considera que la operativa está justificada según el análisis previo.
- Indica si se recomienda **escalar** el expediente a la fase de investigación si la operativa no está justificada según el análisis previo.
- Establece la **prioridad** del caso para investigación: **Alta**, **Media**, o **Baja**, según la gravedad de la alerta.

**Recuerda:**
- Sé crítico, pero conservador en la recomendación de archivado o escalado del caso.
- Eres un sistema experto en **Transaction Monitoring**, por lo que es fundamental identificar casos que sean **falsos positivos** para recomendar su archivado.  
- Considera si las transacciones son consistentes con el perfil conocido del cliente o si hay documentación justificativa suficiente. Si encuentras que la operativa es justificada y consistente con el perfil, recomienda el archivo del expediente como un falso positivo. De lo contrario, recomienda el escalado.
- Solo categoriza como **falsos positivos** los casos que tengas muy seguros, ya que es importante no categorizar como falso positivo algo que pueda ser un verdadero positivo.

**Importante:** Las alertas creadas manualmente tienen una mayor probabilidad de escalado y reporte, por lo que debes ser más estricto en estos casos.

Prioridad del caso:
Para determinar la prioridad del caso, considera los siguientes criterios:
- Consistencia y justificación de la operativa: Evalúa si la operativa es consistente con el perfil del cliente y si hay justificación de las transacciones.
- Tipo de alerta: Las tipos de alerta de mayor gravedad deberían tener una prioridad más alta.
- Importe total de abonos y cargos: Un mayor importe total puede indicar una mayor prioridad. Por ejemplo, menos de 100.000€ en importe de abonos y cargos se considera prioridad baja, entre 100.000€ y 500.000€ prioridad media, y más de 500.000€ prioridad alta.
- Riesgo del cliente: Clientes con un alto score de riesgo deben ser priorizados.
- Perfil del cliente: PEPs (Personas Expuestas Políticamente) deben ser priorizados automáticamente.

A continuación, se proporciona un **risk assessment** del nivel de riesgo de cada tipo de alerta:
- **Riesgo Muy Alto**: Alertas creadas manualmente (e.g., Comunicaciones de Operativa Sospechosa).
- **Riesgo Alto**: Transferencias Internacionales de Alto Riesgo.
- **Riesgo Media-Alta**: Uso de Efectivo.
- **Riesgo Media**: Colectivos de Riesgo / Activos Vulnerables; Estructuras Complejas; Corrupción (PEPs); Fraude (Cuentas Mula, TPV, Adeudos).
- **Riesgo Media-Baja**: Rápido Movimiento de Fondos; Productos y Servicios que facilitan la ocultación de identidad.
- **Riesgo Bajo**: Financiación del Terrorismo; Tráfico de Personas; Banca Corresponsal; Remesas Familiares.

### Plantilla de respuesta esperada:
**Primer párrafo:** Teniendo en cuenta la naturaleza de la alerta, la información disponible sobre el interviniente, su perfil transaccional y la documentación disponible, se recomienda el **[archivo/escalado]** del expediente.

**Segundo párrafo:** Explica el razonamiento detrás de la recomendación de escalado o archivado del expediente a partir del análisis realizado en las preguntas previas.

**Tercer párrafo:** La prioridad del caso para ser investigado es **[Muy Alta/Alta/Media-Alta/Media/Media-Baja/Baja]**, basada en los siguientes criterios...

**Notas:**
- Si no tienes información para alguno de los puntos, omite esa parte de la respuesta.
- Si alguna información es relevante pero no está disponible, añade un párrafo adicional indicando que la información está pendiente o no está disponible.
- No inventes información ni utilices valores como "XXXX". 

"""


conclusion_final_template = \
f"""Responde a la siguiente pregunta en formato Markdown, indicando un título claro de la pregunta (### Heading level 3) y el contenido de la respuesta (text) a continuación:
- Recomendación final
Para responder esta pregunta, apóyate en analizar total o parcialmente algunos de los siguientes puntos:
- Indica si se recomienda el archivo del expediente si se considera justificada la operativa en base a todo el análisis previo
- Indica si se recomienda calificación del expediente como operativa sospechosa y generación del SAR si no se considera justificada la operativa en base a todo el análisis previo
- Indica la prioridad del caso para ser investigado: Alta, Media o Baja, en función de la gravedad considerada para la alerta.

Recuerda ser crítico pero conservador en la recomendación de archivado o escalado del caso. Además, eres un sistema experto en Transaction Monitoring, por lo que debes validar tu respuesta e identificar casos que sean falsos positivos para recomendar su archivado. Considera si las transacciones son consistentes con el perfil conocido del cliente o si hay documentación justificativa suficiente para respaldar las transacciones. Si encuentras que la operativa es justificada y consistente con el perfil del cliente, recomienda el archivo del expediente como un falso positivo. En caso contrario, recomienda el escalado del caso.

A la hora de analizar el caso para recomendar su archivado o escalado, recuerda que las alertas generadas de forma manual suponen una mayor probabilidad de escalado y reporte, por lo que debes ser más esctricto con estos casos.
 
Para determinar la prioridad del caso, considera los siguientes criterios:
- Consistencia y justificación de la operativa: Evalúa si la operativa es consistente con el perfil del cliente y si hay justificación de las transacciones.
- Tipo de alerta: Las tipos de alerta de mayor gravedad deberían tener una prioridad más alta.
- Importe total de abonos y cargos: Un mayor importe total puede indicar una mayor prioridad. Por ejemplo, menos de 100.000€ en importe de abonos y cargos se considera prioridad baja, entre 100.000€ y 500.000€ prioridad media, y más de 500.000€ prioridad alta.
- Riesgo del cliente: Clientes con un alto score de riesgo deben ser priorizados.
- Perfil del cliente: PEPs (Personas Expuestas Políticamente) deben ser priorizados automáticamente.
 
A continuación tienes un risk assessment del nivel de riesgo de cada Tipo de Alerta:
 - Riesgo de Alertas creadas de forma manual (Prioridad Muy Alta): Las alertas creadas de forma manual (ej: Comunicaciones de Operativa Sospechosa) tienen mayor prioridad, y suponen una mayor probabilidad de escalado y reporte.
 - Riesgos con prioridad Alta: Transferencias Internacionales Alto Riesgo
 - Riesgos con prioridad Media-Alta: Uso de Efectivo
 - Riesgos con prioridad Media: Colectivos de Riesgo / Activos Vulnerables; Estructuras Complejas; Corrupción (PEPs); Fraude (cuentas mula, TPV, adeudos...)
 - Riesgos con prioridad Media-Baja: Rápido Movimiento de Fondos; Productos y Servicios que facilitan la ocultación de identidad
 - Riesgos con prioridad Baja: Financiación del Terrorismo; Tráfico de Personas (ruta del dinero); Banca Corresponsal; Remesas Familiares; Cuentas limitadas/colectivos vulnerables que superan umbrales y/o condiciones permitidas
 
Genera la respuesta en tres párrafos, un primer párrafo donde hagas la recomendación de la califiación como operativa sospechosa o archivado del expediente, un segundo párrafo donde expliques el por qué de esta recomendación final, y un tercer párrafo donde indiques la prioridad del caso para ser investigado y los motivos.

Un ejemplo o plantilla de respuesta de esta pregunta es:

(Primer párrafo) Teniendo en cuenta la naturaleza de la alerta, la información disponible sobre el interviniente, su perfil investigado hasta el momento, y la documentación y explicaciones aportadas, se recomienda el **[ archivo del expediente // calificación del expediente como operativa sospechosa y generación del Suspicious Activity Report]**.
 
(Segundo párrafo: explicación sobre la recomendación de archivado o calificación del expediente como operativa sospechosa a partir de la investigación realizada en las preguntas anteriores)
 
(Tercer párrafo: explicación sobre la prioridad de la alerta) La prioridad del caso para ser investigado es **[Muy Alta/Alta/Media-Alta/Media/Media-Baja/Baja]** basándose en los siguientes criterios...

Si no existe información disponible para alguno de los puntos o frases plantilla, no añadas la frase que hace referencia a ese punto.
Solo si es relevante, añade un párrafo adicional debajo de la respuesta indicando que cierta información no está disponible. No se debe inventar información ni marcarla como YYYY.-
"""

grafo_intervinientes_template = \
f"""
Dado el análisis de la operativa del cliente y de los intervinientes adicionales, se ha identificado la necesidad de visualizar las relaciones entre los intervinientes y el principal implicado para los principales abonos y cargos.

Crea un grafo usando el lenguaje DOT de la libreria Graphviz de Python (DOT Language: Abstract grammar for defining Graphviz nodes, edges, graphs, subgraphs, and clusters.) mostrando las relaciones de todos los intervinientes (en el caso de abonos son ordenantes y en el caso de cargos son beneficiarios) con el principal implicado y el importe total de las transferencias con ese ordenante o beneficiario.
IMPORTANTE: Únicamente utiliza los nombres de los intervinientes. En el caso que no se hayan identificado los nombres de los intervinientes adicionales, es decir, que no aparezcan los nombres de los ordenantes (intervinientes para los abonos) o de los beneficiarios (intervinientes para los cargos), devuelve una string vacía ("") como output sin generar ningún grafo. No utilices la descripción del movimiento ni el concepto de las transacciones para identificar a los intervinientes adicionales.

Utiliza la forma (shape) "oval" para el nodo del principal implicado, la forma "box" para los intervinientes de los abonos (ordenantes) y la forma "trapezium" para los intervinientes de los cargos (beneficiarios). Utiliza el color "blue" para el nodo del principal implicado, el color "green" para los nodos de los abonos (ordenantes) y el color "red" para los nodos de los cargos (beneficiarios). Asimismo, utiliza el color "green" para las aristas que conectan los nodos de los abonos y el color "red" para las aristas que conectan los nodos de los cargos. Utiliza 960 dpi para la resolución del grafo.

Recuerda que la sintaxi de DOT para Graphviz es la siguiente:
---
Terminals are shown in bold font and nonterminals in italics. Literal characters are given in single quotes. Parentheses ( and ) indicate grouping when needed. Square brackets [ and ] enclose optional items. Vertical bars | separate alternatives.

graph	:	[ strict ] (graph | digraph) [ ID ] '{{' stmt_list '}}'
stmt_list	:	[ stmt [ ';' ] stmt_list ]
stmt	:	node_stmt
|	edge_stmt
|	attr_stmt
|	ID '=' ID
|	subgraph
attr_stmt	:	(graph | node | edge) attr_list
attr_list	:	'[' [ a_list ] ']' [ attr_list ]
a_list	:	ID '=' ID [ (';' | ',') ] [ a_list ]
edge_stmt	:	(node_id | subgraph) edgeRHS [ attr_list ]
edgeRHS	:	edgeop (node_id | subgraph) [ edgeRHS ]
node_stmt	:	node_id [ attr_list ]
node_id	:	ID [ port ]
port	:	':' ID [ ':' compass_pt ]
|	':' compass_pt
subgraph	:	[ subgraph [ ID ] ] '{{' stmt_list '}}'
compass_pt	:	(n | ne | e | se | s | sw | w | nw | c | _)
The keywords node, edge, graph, digraph, subgraph, and strict are case-independent. Note also that the allowed compass point values are not keywords, so these strings can be used elsewhere as ordinary identifiers and, conversely, the parser will actually accept any identifier.

EXAMPLE:
digraph G {{
 graph [dpi=960];
 a [shape=oval, color=blue];
 b [shape=box, color=green];
 c [shape=trapezium, color=red];
 ...
 b -> a [ label="b to a" ];
 a -> c [ label="another label"];
 ...
}}
---

Devuelve únicamente una string con la definición del grafo apropiado en lenguaje DOT de Graphviz. No es necesario generar la imagen del grafo, únicamente la definición en lenguaje DOT.

IMPORTANTE: Únicamente utiliza los nombres de los intervinientes. En el caso que no se hayan identificado los nombres de los intervinientes adicionales, es decir, que no aparezcan los nombres de los ordenantes (intervinientes para los abonos) o de los beneficiarios (intervinientes para los cargos), devuelve una string vacía ("") como output sin generar ningún grafo. No utilices la descripción del movimiento ni el concepto de las transacciones para identificar a los intervinientes adicionales.
"""
