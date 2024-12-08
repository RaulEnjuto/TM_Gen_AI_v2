"""
This module contains the Prompts class, which provides static methods to generate templates for narratives and SAR (Suspicious Activity Reports). 
It serves as a central point for constructing prompts used in the application.
"""

from utilities.prompts_templates.narratives import (
    base_prompt_template,
    naturaleza_alerta_template,
    principal_implicado_template,
    analisis_operativa_template,
    recomendacion_prenarrativa_template,
    contexto_historico_template,
    conclusion_final_template,
    documentacion_adicional_template,
    intervinientes_adicionales_template,
    grafo_intervinientes_template,
)
from utilities.prompts_templates.SAR import (
    base_prompt_SAR_template,
    resumen_ejecutivo_template,
    identificacion_interviniente_template,
    descripcion_operaciones_template,
    blanqueo_capitales_template,
    gestiones_comprobaciones_template,
    documentacion_remitida_template,
)


class Prompts:
    """
    A class containing static methods to construct various prompts used in generating narratives and SARs.

    This class provides methods to format templates for different sections of a pre-narrative or SAR.
    """

    def __init__(self):
        pass

    @staticmethod
    def base_prompt(alert_data, customer_data, transactions_df, playbook: str = "", alert_assessment: str = ""):
        """
        Generate the base prompt for narrative generation.

        Args:
            alert_data (str): Data related to the alert.
            customer_data (str): Data related to the customer (KYC).
            transactions_df (str): Transaction data in string format.
            playbook (str, optional): Additional playbook information. Defaults to "".
            alert_assessment (str, optional): Alert assessment details. Defaults to "".

        Returns:
            str: The formatted base prompt.
        """
        return base_prompt_template(alert_data, customer_data, transactions_df, playbook, alert_assessment)

    @staticmethod
    def naturaleza_alerta():
        """
        Get the template for the "Nature of the Alert" section.

        Returns:
            str: The narrative template for nature of the alert.
        """
        return naturaleza_alerta_template

    @staticmethod
    def principal_implicado(informacion_externa: str = ""):
        """
        Get the template for the "Principal Implicated" section.

        Args:
            informacion_externa (str, optional): External information to include in the section. Defaults to "".

        Returns:
            str: The formatted template for principal implicated.
        """
        return principal_implicado_template(informacion_externa)

    @staticmethod
    def contexto_historico():
        """
        Get the template for the "Historical Context" section.

        Returns:
            str: The narrative template for historical context.
        """
        return contexto_historico_template

    @staticmethod
    def analisis_operativa(tabla_abonos: str = "", tabla_cargos: str = ""):
        """
        Get the template for the "Operational Analysis" section.

        Args:
            tabla_abonos (str, optional): Data for credit tables. Defaults to "".
            tabla_cargos (str, optional): Data for debit tables. Defaults to "".

        Returns:
            str: The formatted template for operational analysis.
        """
        return analisis_operativa_template(tabla_abonos, tabla_cargos)

    @staticmethod
    def recomendacion_prenarrativa():
        """
        Get the template for the "Pre-narrative Recommendation" section.

        Returns:
            str: The narrative template for recommendations.
        """
        return recomendacion_prenarrativa_template

    @staticmethod
    def conclusion_final():
        """
        Get the template for the "Final Conclusion" section.

        Returns:
            str: The narrative template for final conclusion.
        """
        return conclusion_final_template

    @staticmethod
    def documentacion_adicional(documentacion_adicional: str):
        """
        Get the template for the "Additional Documentation" section.

        Args:
            documentacion_adicional (str): Additional documentation details.

        Returns:
            str: The formatted template for additional documentation.
        """
        return documentacion_adicional_template(documentacion_adicional)

    @staticmethod
    def intervinientes_adicionales(
        json_interviniente_cliente: str = "",
        transactions_interviniente_df: str = "",
        tabla_abonos_interviniente: str = "",
        tabla_cargos_interviniente: str = ""
    ):
        """
        Get the template for the "Additional Participants" section.

        Args:
            json_interviniente_cliente (str, optional): JSON data of additional participants. Defaults to "".
            transactions_interviniente_df (str, optional): Transactions of additional participants. Defaults to "".
            tabla_abonos_interviniente (str, optional): Credit table for additional participants. Defaults to "".
            tabla_cargos_interviniente (str, optional): Debit table for additional participants. Defaults to "".

        Returns:
            str: The formatted template for additional participants.
        """
        return intervinientes_adicionales_template(
            json_interviniente_cliente,
            transactions_interviniente_df,
            tabla_abonos_interviniente,
            tabla_cargos_interviniente
        )

    @staticmethod
    def grafo_intervinientes():
        """
        Get the template for the "Graph of Participants" section.

        Returns:
            str: The narrative template for the graph of participants.
        """
        return grafo_intervinientes_template

    @staticmethod
    def base_prompt_SAR(alert_data: str, customer_data: str, transactions_df: str, narrative_output: str):
        """
        Generate the base prompt for SAR generation.

        Args:
            alert_data (str): Data related to the alert.
            customer_data (str): Data related to the customer.
            transactions_df (str): Transaction data in string format.
            narrative_output (str): Narrative output to include in the SAR.

        Returns:
            str: The formatted base prompt for SAR.
        """
        return base_prompt_SAR_template(alert_data, customer_data, transactions_df, narrative_output)

    @staticmethod
    def resumen_ejecutivo(template: str):
        """
        Get the template for the "Executive Summary" section of SAR.

        Args:
            template (str): SAR template for the executive summary.

        Returns:
            str: The formatted template for executive summary.
        """
        return resumen_ejecutivo_template(template)

    @staticmethod
    def identificacion_interviniente(template: str):
        """
        Get the template for the "Participant Identification" section of SAR.

        Args:
            template (str): SAR template for participant identification.

        Returns:
            str: The formatted template for participant identification.
        """
        return identificacion_interviniente_template(template)

    @staticmethod
    def descripcion_operaciones(template: str):
        """
        Get the template for the "Operations Description" section of SAR.

        Args:
            template (str): SAR template for operations description.

        Returns:
            str: The formatted template for operations description.
        """
        return descripcion_operaciones_template(template)

    @staticmethod
    def indicios_blanqueo(template: str):
        """
        Get the template for the "Money Laundering Indications" section of SAR.

        Args:
            template (str): SAR template for money laundering indications.

        Returns:
            str: The formatted template for money laundering indications.
        """
        return blanqueo_capitales_template(template)

    @staticmethod
    def gestiones_comprobaciones(template: str):
        """
        Get the template for the "Checks and Verifications" section of SAR.

        Args:
            template (str): SAR template for checks and verifications.

        Returns:
            str: The formatted template for checks and verifications.
        """
        return gestiones_comprobaciones_template(template)

    @staticmethod
    def documentacion_remitida(template: str):
        """
        Get the template for the "Submitted Documentation" section of SAR.

        Args:
            template (str): SAR template for submitted documentation.

        Returns:
            str: The formatted template for submitted documentation.
        """
        return documentacion_remitida_template(template)
