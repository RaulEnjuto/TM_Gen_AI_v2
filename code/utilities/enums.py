from enum import Enum


class QuestionsTypes(Enum):
    NATURALEZA_ALERTA = "Naturaleza de la alerta"
    PRINCIPAL_IMPLICADO = "Principal implicado"
    CONTEXTO_HISTORICO = "Contexto histórico del cliente"
    ANALISIS_OPERATIVA = "Análisis de la operativa del cliente"
    RECOMENDACION_INICIAL = "Recomendación inicial"
    CONCLUSION_FINAL = "Conclusión final"
    # 
    INTERVINIENTES_ADICIONALES = "Intervinientes adicionales"
    DOCUMENTACION_ADICIONAL = "Documentación adicional"
    GRAFO_INTERVINIENTES = "Grafo de intervinientes"


class QuestionsTypesSAR(Enum):
    """
    Enum for SAR questions
    """
    RESUMEN_EJECUTIVO = "Resumen ejecutivo"
    IDENTIFICACION_INTERVINIENTE = "Identificación del interviniente"
    DESCRIPCION_OPERACIONES = "Descripción de las operaciones"
    INDICIO_BLANQUEO = "Indicios de blanqueo de capitales"
    GESTIONES_COMPROBACIONES = "Gestiones y comprobaciones realizadas"
    DOCUMENTACION_REMITIDA = "Documentación remitida"


class TemplateNameSAR(Enum):
    """
    Enum for SAR questions
    """
    RESUMEN_EJECUTIVO = "ResumenEjecutivo"
    IDENTIFICACION_INTERVINIENTE = "IdentificacionDelInterviniente"
    DESCRIPCION_OPERACIONES = "DescripcionDeLasOperaciones"
    INDICIO_BLANQUEO = "IndiciosDeBlanqueoDeCapitales"
    GESTIONES_COMPROBACIONES = "GestionesyComprobacionesRealizadas"
    DOCUMENTACION_REMITIDA = "DocumentacionRemitida"

class CaseTypes(Enum):
    """
    Enum for case typologies
    """
    ALL = 'Todos'
    COS = 'Comunicación de operativa sospechosa desde oficina'
    UE = 'Uso de efectivo'
    TI = 'Transferencias internacionales'
    CNC = 'Clientes de nueva captación'
    CL = 'Cuentas vulnerables'

    @classmethod
    def get(cls, value) -> str:
        for member in cls:
            if member.value == value:
                return str(member.name)
        return ''
    
    @classmethod
    def get_value(cls, name: str) -> str:
        try:
            return cls[name].value
        except KeyError:
            return ''