"""
Módulo para gestionar la comunicación con AFIP para facturación electrónica.
Permite autenticación, obtención de CAE y consulta de datos fiscales.
"""
import os
import logging
import json
import base64
import datetime
import hashlib
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
import requests
import zeep
from zeep.transports import Transport
from zeep.exceptions import Fault
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)

# Constantes para los servicios de AFIP
WSAA_URL_TESTING = "https://wsaahomo.afip.gov.ar/ws/services/LoginCms"
WSAA_URL_PRODUCTION = "https://wsaa.afip.gov.ar/ws/services/LoginCms"

WSFEV1_URL_TESTING = "https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL"
WSFEV1_URL_PRODUCTION = "https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL"

WSPADRON_URL_TESTING = "https://awshomo.afip.gov.ar/sr-padron/webservices/personaServiceA5?WSDL"
WSPADRON_URL_PRODUCTION = "https://aws.afip.gov.ar/sr-padron/webservices/personaServiceA5?WSDL"

# Mapa de tipos de comprobantes para AFIP
TIPO_COMPROBANTE_MAP = {
    "A": 1,  # Factura A
    "B": 6,  # Factura B
    "C": 11,  # Factura C
    "M": 51,  # Factura M
    "NCA": 3,  # Nota de Crédito A
    "NCB": 8,  # Nota de Crédito B
    "NCC": 13,  # Nota de Crédito C
    "NDA": 2,  # Nota de Débito A
    "NDB": 7,  # Nota de Débito B
    "NDC": 12,  # Nota de Débito C
}

# Mapa de tipos de documentos para AFIP
TIPO_DOCUMENTO_MAP = {
    "CUIT": 80,
    "CUIL": 86,
    "CDI": 87,
    "DNI": 96,
    "Pasaporte": 94,
    "CI Extranjera": 91,
    "Sin identificar": 99,
}

# Mapa de alícuotas de IVA para AFIP
ALICUOTA_IVA_MAP = {
    "0": 3,     # 0%
    "0.0": 3,
    "10.5": 4,  # 10.5%
    "21": 5,    # 21%
    "21.0": 5,
    "27": 6,    # 27%
}

class AfipManager:
    """
    Clase para gestionar la comunicación con los web services de AFIP.
    """
    def __init__(self, modo_produccion: bool = False):
        """
        Inicializa el gestor de AFIP.
        
        Args:
            modo_produccion: Si es True, se conecta a los servicios de producción. 
                            Si es False, se conecta a los servicios de homologación.
        """
        self.modo_produccion = modo_produccion
        self.wsaa_url = WSAA_URL_PRODUCTION if modo_produccion else WSAA_URL_TESTING
        self.wsfev1_url = WSFEV1_URL_PRODUCTION if modo_produccion else WSFEV1_URL_TESTING
        self.wspadron_url = WSPADRON_URL_PRODUCTION if modo_produccion else WSPADRON_URL_TESTING
        
        # Ruta base para certificados y tokens
        self.base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "certificados")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
        
        # Archivos para guardar tickets de acceso
        self.access_token_file = os.path.join(self.base_path, "token_wsfev1.json")
        self.padron_token_file = os.path.join(self.base_path, "token_wspadron.json")
        
        # Rutas de certificados y claves privadas
        self.cert_file = os.path.join(self.base_path, "certificado.crt")
        self.privatekey_file = os.path.join(self.base_path, "clave_privada.key")
        
        # Verificar existencia de certificados
        self._check_certificates()
    
    def _check_certificates(self) -> None:
        """
        Verifica si existen los certificados necesarios.
        Lanza excepción si no se encuentran.
        """
        if not os.path.exists(self.cert_file):
            logger.error(f"No se encontró el certificado en {self.cert_file}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Certificado de AFIP no encontrado. Contacte al administrador."
            )
        
        if not os.path.exists(self.privatekey_file):
            logger.error(f"No se encontró la clave privada en {self.privatekey_file}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Clave privada de AFIP no encontrada. Contacte al administrador."
            )
    
    def _get_service_client(self, url: str) -> zeep.Client:
        """
        Obtiene un cliente SOAP para el web service especificado.
        
        Args:
            url: URL del WSDL del servicio.
            
        Returns:
            Cliente SOAP configurado.
        """
        try:
            transport = Transport(timeout=30)
            return zeep.Client(url, transport=transport)
        except Exception as e:
            logger.error(f"Error al crear cliente SOAP: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al conectar con servicio de AFIP: {str(e)}"
            )
    
    def _create_tra(self, service: str, ttl: int = 24) -> str:
        """
        Crea un Ticket de Requerimiento de Acceso (TRA) para la autenticación con WSAA.
        
        Args:
            service: Nombre del servicio para el que se solicita acceso (wsfev1, wspadron, etc).
            ttl: Tiempo de vida del ticket en horas.
            
        Returns:
            XML del TRA como string.
        """
        now = datetime.utcnow() - timedelta(hours=3)  # Buenos Aires timezone (GMT-3)
        expiration = now + timedelta(hours=ttl)
        
        # Formato específico requerido por AFIP
        gen_time_str = now.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        exp_time_str = expiration.strftime("%Y-%m-%dT%H:%M:%S-03:00")
        
        # Crear XML del TRA
        tra = ET.Element('loginTicketRequest', version="1.0")
        header = ET.SubElement(tra, 'header')
        
        ET.SubElement(header, 'uniqueId').text = str(int(datetime.now().timestamp()))
        ET.SubElement(header, 'generationTime').text = gen_time_str
        ET.SubElement(header, 'expirationTime').text = exp_time_str
        
        ET.SubElement(tra, 'service').text = service
        
        return ET.tostring(tra, encoding='utf-8').decode('utf-8')
    
    def _sign_tra(self, tra_str: str) -> str:
        """
        Firma el TRA con el certificado y clave privada.
        
        Args:
            tra_str: XML del TRA como string.
            
        Returns:
            TRA firmado en formato base64.
        """
        try:
            # Crear archivo temporal con el TRA
            tra_file = os.path.join(self.base_path, "tmp_tra.xml")
            with open(tra_file, "w") as f:
                f.write(tra_str)
            
            # Firmar el TRA usando OpenSSL (requiere openssl instalado en el sistema)
            signed_file = os.path.join(self.base_path, "tmp_tra.cms")
            cmd = f'openssl cms -sign -in {tra_file} -out {signed_file} -signer {self.cert_file} -inkey {self.privatekey_file} -outform PEM -nodetach'
            
            import subprocess
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr = proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode('utf-8', 'ignore')
                logger.error(f"Error al firmar TRA: {error_msg}")
                raise Exception(f"Error al firmar TRA: {error_msg}")
            
            # Leer archivo firmado y codificarlo en base64
            with open(signed_file, "r") as f:
                signed_content = f.read()
            
            # Limpiar archivos temporales
            try:
                os.remove(tra_file)
                os.remove(signed_file)
            except:
                pass
            
            # Extraer el contenido entre los delimitadores y codificar en base64
            begin = "-----BEGIN PKCS7-----"
            end = "-----END PKCS7-----"
            content = signed_content.split(begin)[1].split(end)[0].replace("\n", "")
            
            return content
            
        except Exception as e:
            logger.error(f"Error al firmar TRA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al firmar ticket de acceso: {str(e)}"
            )
    
    def _call_wsaa(self, service: str) -> Dict[str, Any]:
        """
        Llama al servicio WSAA para obtener un ticket de acceso.
        
        Args:
            service: Nombre del servicio para el que se solicita acceso.
            
        Returns:
            Diccionario con el token y sign de acceso.
        """
        try:
            # Crear y firmar TRA
            tra = self._create_tra(service)
            cms = self._sign_tra(tra)
            
            # Llamar al servicio WSAA
            client = self._get_service_client(self.wsaa_url + "?WSDL")
            result = client.service.loginCms(cms)
            
            # Parsear respuesta XML
            response_xml = ET.fromstring(result)
            
            credentials = {
                "token": response_xml.find(".//token").text,
                "sign": response_xml.find(".//sign").text,
                "expiration": (datetime.now() + timedelta(hours=23)).isoformat(),
                "generation": datetime.now().isoformat(),
                "service": service
            }
            
            # Guardar en archivo según el servicio
            if service == "wsfe":
                token_file = self.access_token_file
            elif service == "ws_sr_padron_a5":
                token_file = self.padron_token_file
            else:
                token_file = os.path.join(self.base_path, f"token_{service}.json")
            
            with open(token_file, "w") as f:
                json.dump(credentials, f)
            
            return credentials
            
        except Fault as f:
            logger.error(f"Error SOAP al llamar WSAA: {f}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error en autenticación con AFIP: {str(f)}"
            )
        except Exception as e:
            logger.error(f"Error al llamar WSAA: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener ticket de acceso: {str(e)}"
            )
    
    def _get_credentials(self, service: str) -> Dict[str, str]:
        """
        Obtiene credenciales para el servicio especificado.
        Si no existen o están expiradas, las solicita nuevamente.
        
        Args:
            service: Nombre del servicio (wsfe o ws_sr_padron_a5).
            
        Returns:
            Diccionario con token y sign.
        """
        if service == "wsfe":
            token_file = self.access_token_file
        elif service == "ws_sr_padron_a5":
            token_file = self.padron_token_file
        else:
            token_file = os.path.join(self.base_path, f"token_{service}.json")
        
        # Verificar si existe el archivo de credenciales
        if os.path.exists(token_file):
            with open(token_file, "r") as f:
                credentials = json.load(f)
            
            # Verificar si las credenciales están vigentes
            expiration = datetime.fromisoformat(credentials["expiration"])
            if datetime.now() < expiration:
                return {"token": credentials["token"], "sign": credentials["sign"]}
        
        # Si no hay credenciales o están expiradas, obtener nuevas
        credentials = self._call_wsaa(service)
        return {"token": credentials["token"], "sign": credentials["sign"]}
    
    def consultar_puntos_venta(self, cuit: str) -> List[Dict[str, Any]]:
        """
        Consulta los puntos de venta habilitados para el CUIT.
        
        Args:
            cuit: CUIT del emisor.
            
        Returns:
            Lista de puntos de venta habilitados.
        """
        try:
            # Obtener credenciales
            credentials = self._get_credentials("wsfe")
            
            # Llamar al servicio WSFEV1
            client = self._get_service_client(self.wsfev1_url)
            
            auth = {
                "Token": credentials["token"],
                "Sign": credentials["sign"],
                "Cuit": cuit
            }
            
            result = client.service.FEParamGetPtosVenta(auth)
            
            if result.ResultGet is None:
                return []
            
            # Convertir a lista de diccionarios
            puntos_venta = []
            for pto in result.ResultGet.PtoVenta:
                punto = {
                    "nro": pto.Nro,
                    "emisionTipo": pto.EmisionTipo,
                    "bloqueado": pto.Bloqueado,
                    "fechaBaja": pto.FchBaja if hasattr(pto, "FchBaja") else None
                }
                puntos_venta.append(punto)
            
            return puntos_venta
            
        except Fault as f:
            logger.error(f"Error SOAP al consultar puntos de venta: {f}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar puntos de venta en AFIP: {str(f)}"
            )
        except Exception as e:
            logger.error(f"Error al consultar puntos de venta: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar puntos de venta: {str(e)}"
            )
    
    def consultar_tipos_comprobante(self, cuit: str) -> List[Dict[str, Any]]:
        """
        Consulta los tipos de comprobantes habilitados para el CUIT.
        
        Args:
            cuit: CUIT del emisor.
            
        Returns:
            Lista de tipos de comprobantes habilitados.
        """
        try:
            # Obtener credenciales
            credentials = self._get_credentials("wsfe")
            
            # Llamar al servicio WSFEV1
            client = self._get_service_client(self.wsfev1_url)
            
            auth = {
                "Token": credentials["token"],
                "Sign": credentials["sign"],
                "Cuit": cuit
            }
            
            result = client.service.FEParamGetTiposCbte(auth)
            
            if result.ResultGet is None:
                return []
            
            # Convertir a lista de diccionarios
            tipos_comprobante = []
            for tc in result.ResultGet.CbteTipo:
                tipo = {
                    "id": tc.Id,
                    "descripcion": tc.Desc,
                    "fechaDesde": tc.FchDesde,
                    "fechaHasta": tc.FchHasta
                }
                tipos_comprobante.append(tipo)
            
            return tipos_comprobante
            
        except Fault as f:
            logger.error(f"Error SOAP al consultar tipos de comprobante: {f}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar tipos de comprobante en AFIP: {str(f)}"
            )
        except Exception as e:
            logger.error(f"Error al consultar tipos de comprobante: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar tipos de comprobante: {str(e)}"
            )
    
    def consultar_ultimo_comprobante(self, cuit: str, punto_venta: int, tipo_comprobante: str) -> int:
        """
        Consulta el último número de comprobante para un punto de venta y tipo.
        
        Args:
            cuit: CUIT del emisor.
            punto_venta: Número de punto de venta.
            tipo_comprobante: Tipo de comprobante (A, B, C, etc).
            
        Returns:
            Último número de comprobante.
        """
        try:
            # Obtener credenciales
            credentials = self._get_credentials("wsfe")
            
            # Llamar al servicio WSFEV1
            client = self._get_service_client(self.wsfev1_url)
            
            auth = {
                "Token": credentials["token"],
                "Sign": credentials["sign"],
                "Cuit": cuit
            }
            
            # Convertir tipo de comprobante a código numérico
            tipo_cbte_id = TIPO_COMPROBANTE_MAP.get(tipo_comprobante, 0)
            if tipo_cbte_id == 0:
                raise ValueError(f"Tipo de comprobante inválido: {tipo_comprobante}")
            
            result = client.service.FECompUltimoAutorizado(auth, punto_venta, tipo_cbte_id)
            
            if hasattr(result, "Errors") and result.Errors is not None:
                error_msg = "; ".join([f"{e.Code}: {e.Msg}" for e in result.Errors.Err])
                logger.error(f"Error en consulta de último comprobante: {error_msg}")
                return 0
            
            return result.CbteNro
            
        except Fault as f:
            logger.error(f"Error SOAP al consultar último comprobante: {f}")
            if "602: Sin datos" in str(f):
                # Si no hay comprobantes anteriores, devuelve 0
                return 0
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar último comprobante en AFIP: {str(f)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error al consultar último comprobante: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar último comprobante: {str(e)}"
            )
    
    def consultar_datos_contribuyente(self, cuit: str) -> Dict[str, Any]:
        """
        Consulta los datos de un contribuyente por su CUIT.
        
        Args:
            cuit: CUIT del contribuyente a consultar.
            
        Returns:
            Diccionario con los datos del contribuyente.
        """
        try:
            # Obtener credenciales para el padrón
            credentials = self._get_credentials("ws_sr_padron_a5")
            
            # Llamar al servicio de consulta de padrón
            client = self._get_service_client(self.wspadron_url)
            
            # Limpiar CUIT (eliminar guiones)
            cuit_limpio = cuit.replace("-", "")
            
            result = client.service.getPersona(
                credentials["token"],
                credentials["sign"],
                20000000000,  # CUIT del solicitante (debe ser el autorizado)
                cuit_limpio
            )
            
            if not hasattr(result, "persona"):
                return {
                    "error": "Contribuyente no encontrado",
                    "encontrado": False
                }
            
            persona = result.persona
            
            # Construir respuesta
            datos = {
                "encontrado": True,
                "tipoClave": "CUIT",
                "numeroDocumento": persona.idPersona,
                "tipoPersona": "FISICA" if persona.tipoPersona == "F" else "JURIDICA",
                "razonSocial": persona.nombre,
                "apellido": persona.apellido if hasattr(persona, "apellido") else None,
                "nombre": persona.nombrePersona if hasattr(persona, "nombrePersona") else None,
                "domicilios": [],
                "impuestos": [],
                "categoriaMonotributo": None,
                "actividadesEconomicas": []
            }
            
            # Agregar domicilios
            if hasattr(persona, "domicilio"):
                for dom in persona.domicilio:
                    domicilio = {
                        "direccion": f"{dom.direccion}, {dom.localidad}",
                        "localidad": dom.localidad,
                        "codPostal": dom.codPostal,
                        "provincia": dom.descripcionProvincia,
                        "tipoDomicilio": dom.tipoDomicilio
                    }
                    datos["domicilios"].append(domicilio)
            
            # Agregar categoría monotributo e impuestos
            if hasattr(persona, "datosMonotributo"):
                datos["categoriaMonotributo"] = persona.datosMonotributo.categoriaMonotributo.descripcionCategoria
            
            if hasattr(persona, "impuesto"):
                for imp in persona.impuesto:
                    impuesto = {
                        "id": imp.idImpuesto,
                        "descripcion": imp.descripcionImpuesto,
                        "periodo": imp.periodo if hasattr(imp, "periodo") else None
                    }
                    datos["impuestos"].append(impuesto)
            
            # Agregar actividades económicas
            if hasattr(persona, "actividadEconomica"):
                for act in persona.actividadEconomica:
                    actividad = {
                        "id": act.idActividad,
                        "descripcion": act.descripcionActividad,
                        "nomenclador": act.nomenclador,
                        "orden": act.orden,
                        "periodo": act.periodo if hasattr(act, "periodo") else None
                    }
                    datos["actividadesEconomicas"].append(actividad)
            
            return datos
            
        except Fault as f:
            logger.error(f"Error SOAP al consultar contribuyente: {f}")
            if "El cuit solicitado no existe en el padrón" in str(f):
                return {
                    "error": "Contribuyente no encontrado",
                    "encontrado": False
                }
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar contribuyente en AFIP: {str(f)}"
            )
        except Exception as e:
            logger.error(f"Error al consultar contribuyente: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar contribuyente: {str(e)}"
            )
    
    def _format_date_for_afip(self, date_str: str) -> str:
        """
        Formatea una fecha para AFIP (YYYYMMDD).
        
        Args:
            date_str: Fecha en formato ISO (YYYY-MM-DD).
            
        Returns:
            Fecha formateada para AFIP.
        """
        if isinstance(date_str, (datetime, datetime.date)):
            return date_str.strftime("%Y%m%d")
        else:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%Y%m%d")
    
    def solicitar_cae(self, factura_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Solicita un CAE para una factura.
        
        Args:
            factura_data: Datos de la factura.
            
        Returns:
            Respuesta de AFIP con el CAE.
        """
        try:
            # Obtener credenciales
            credentials = self._get_credentials("wsfe")
            
            # Extraer datos principales de la factura
            cuit_emisor = factura_data["emisor_cuit"].replace("-", "")
            tipo_cbte = TIPO_COMPROBANTE_MAP.get(factura_data["tipo_comprobante"], 0)
            if tipo_cbte == 0:
                raise ValueError(f"Tipo de comprobante inválido: {factura_data['tipo_comprobante']}")
            
            punto_venta = int(factura_data["punto_venta"])
            nro_factura = int(factura_data["nrofactura"])
            
            # Fecha en formato AFIP (YYYYMMDD)
            fecha_cbte = self._format_date_for_afip(factura_data["fecha_emision"])
            
            # Configuración de importes
            imp_total = float(factura_data["total"])
            imp_neto = float(factura_data["subtotal_neto"]) if "subtotal_neto" in factura_data else imp_total / (1 + float(factura_data["iva_porcentaje"]) / 100)
            imp_iva = float(factura_data["iva_importe"]) if "iva_importe" in factura_data else imp_total - imp_neto
            imp_trib = float(factura_data.get("otros_impuestos", 0))
            
            # Datos del cliente
            tipo_doc = TIPO_DOCUMENTO_MAP.get(factura_data["receptor_tipo_documento"], 99)
            nro_doc = factura_data["receptor_nro_documento"].replace("-", "")
            nombre_cliente = factura_data["receptor_razon_social"]
            
            # Configuración de moneda
            moneda_id = "PES"  # Pesos argentinos
            moneda_cotiz = 1.0  # Cotización 1:1 para pesos argentinos
            
            # Llamar al servicio WSFEV1
            client = self._get_service_client(self.wsfev1_url)
            
            # Preparar información sobre IVA
            if factura_data.get("items"):
                # Agrupar por alícuota de IVA
                alicuotas_iva = {}
                for item in factura_data["items"]:
                    alicuota = str(item.get("alicuota_iva", "21"))
                    if alicuota not in alicuotas_iva:
                        alicuotas_iva[alicuota] = {
                            "base_imp": 0.0,
                            "importe": 0.0
                        }
                    alicuotas_iva[alicuota]["base_imp"] += float(item.get("subtotal", 0))
                    alicuotas_iva[alicuota]["importe"] += float(item.get("importe_iva", 0))
                
                iva_data = []
                for alicuota, valores in alicuotas_iva.items():
                    iva_data.append({
                        "Id": ALICUOTA_IVA_MAP.get(alicuota, 5),  # 5 es 21%
                        "BaseImp": valores["base_imp"],
                        "Importe": valores["importe"]
                    })
            else:
                # Si no hay items detallados, usar los totales generales
                iva_data = [{
                    "Id": ALICUOTA_IVA_MAP.get(str(factura_data["iva_porcentaje"]), 5),
                    "BaseImp": imp_neto,
                    "Importe": imp_iva
                }]
            
            # Preparar datos de factura
            fecae_data = {
                "FeCabReq": {
                    "CantReg": 1,
                    "PtoVta": punto_venta,
                    "CbteTipo": tipo_cbte
                },
                "FeDetReq": {
                    "FECAEDetRequest": [{
                        "Concepto": 1,  # 1: Productos, 2: Servicios, 3: Productos y Servicios
                        "DocTipo": tipo_doc,
                        "DocNro": int(nro_doc) if nro_doc.isdigit() else 0,
                        "CbteDesde": nro_factura,
                        "CbteHasta": nro_factura,
                        "CbteFch": fecha_cbte,
                        "ImpTotal": imp_total,
                        "ImpTotConc": 0,  # Importe neto no gravado
                        "ImpNeto": imp_neto,
                        "ImpOpEx": 0,  # Importe exento
                        "ImpIVA": imp_iva,
                        "ImpTrib": imp_trib,
                        "MonId": moneda_id,
                        "MonCotiz": moneda_cotiz,
                        "Iva": iva_data
                    }]
                }
            }
            
            # Si hay tributos (otros impuestos), agregarlos
            if imp_trib > 0:
                tributos = [{
                    "Id": 99,  # Otros
                    "BaseImp": imp_neto,
                    "Alic": (imp_trib / imp_neto) * 100 if imp_neto > 0 else 0,
                    "Importe": imp_trib
                }]
                fecae_data["FeDetReq"]["FECAEDetRequest"][0]["Tributos"] = tributos
            
            # Completar datos de autorización
            auth = {
                "Token": credentials["token"],
                "Sign": credentials["sign"],
                "Cuit": int(cuit_emisor)
            }
            
            # Solicitar CAE
            result = client.service.FECAESolicitar(auth, fecae_data)
            
            # Verificar errores
            if hasattr(result, "Errors") and result.Errors is not None:
                error_msg = "; ".join([f"{e.Code}: {e.Msg}" for e in result.Errors.Err])
                logger.error(f"Error en solicitud de CAE: {error_msg}")
                return {"error": error_msg, "resultado": "R"}
            
            # Verificar observaciones
            observaciones = []
            if hasattr(result.FeDetResp.FECAEDetResponse[0], "Observaciones") and result.FeDetResp.FECAEDetResponse[0].Observaciones is not None:
                for obs in result.FeDetResp.FECAEDetResponse[0].Observaciones.Obs:
                    observaciones.append(f"{obs.Code}: {obs.Msg}")
            
            # Obtener el CAE y su fecha de vencimiento
            cae = result.FeDetResp.FECAEDetResponse[0].CAE
            cae_vto = result.FeDetResp.FECAEDetResponse[0].CAEFchVto
            
            # Formatear fecha de vencimiento
            cae_vto_date = f"{cae_vto[0:4]}-{cae_vto[4:6]}-{cae_vto[6:8]}"
            
            return {
                "cae": cae,
                "cae_vencimiento": cae_vto_date,
                "resultado": result.FeDetResp.FECAEDetResponse[0].Resultado,
                "observaciones": observaciones,
                "punto_venta": punto_venta,
                "tipo_comprobante": tipo_cbte,
                "numero_comprobante": nro_factura
            }
            
        except Fault as f:
            logger.error(f"Error SOAP al solicitar CAE: {f}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al solicitar CAE en AFIP: {str(f)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error al solicitar CAE: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al solicitar CAE: {str(e)}"
            )
    
    def consultar_comprobante(self, cuit: str, tipo_comprobante: str, punto_venta: int, numero: int) -> Dict[str, Any]:
        """
        Consulta un comprobante específico en AFIP.
        
        Args:
            cuit: CUIT del emisor.
            tipo_comprobante: Tipo de comprobante (A, B, C, etc).
            punto_venta: Número de punto de venta.
            numero: Número de comprobante.
            
        Returns:
            Información del comprobante.
        """
        try:
            # Obtener credenciales
            credentials = self._get_credentials("wsfe")
            
            # Llamar al servicio WSFEV1
            client = self._get_service_client(self.wsfev1_url)
            
            auth = {
                "Token": credentials["token"],
                "Sign": credentials["sign"],
                "Cuit": cuit
            }
            
            # Convertir tipo de comprobante a código numérico
            tipo_cbte_id = TIPO_COMPROBANTE_MAP.get(tipo_comprobante, 0)
            if tipo_cbte_id == 0:
                raise ValueError(f"Tipo de comprobante inválido: {tipo_comprobante}")
            
            result = client.service.FECompConsultar(auth, tipo_cbte_id, punto_venta, numero)
            
            # Verificar errores
            if hasattr(result, "Errors") and result.Errors is not None:
                error_msg = "; ".join([f"{e.Code}: {e.Msg}" for e in result.Errors.Err])
                logger.error(f"Error en consulta de comprobante: {error_msg}")
                
                if "602: Sin datos" in error_msg:
                    return {"encontrado": False, "error": "Comprobante no encontrado"}
                
                return {"encontrado": False, "error": error_msg}
            
            # Si no hay resultado, devolver no encontrado
            if not hasattr(result, "ResultGet"):
                return {"encontrado": False, "error": "Comprobante no encontrado"}
            
            comprobante = result.ResultGet
            
            # Formatear fechas
            fecha_cbte = f"{comprobante.CbteFch[0:4]}-{comprobante.CbteFch[4:6]}-{comprobante.CbteFch[6:8]}"
            cae_vto = None
            if hasattr(comprobante, "CAEFchVto") and comprobante.CAEFchVto:
                cae_vto = f"{comprobante.CAEFchVto[0:4]}-{comprobante.CAEFchVto[4:6]}-{comprobante.CAEFchVto[6:8]}"
            
            # Construir respuesta
            result = {
                "encontrado": True,
                "tipo_comprobante": tipo_comprobante,
                "punto_venta": punto_venta,
                "numero": numero,
                "fecha": fecha_cbte,
                "importe_total": comprobante.ImpTotal,
                "importe_neto": comprobante.ImpNeto,
                "importe_iva": comprobante.ImpIVA,
                "cae": comprobante.CAE if hasattr(comprobante, "CAE") else None,
                "cae_vencimiento": cae_vto,
                "resultado": comprobante.Resultado if hasattr(comprobante, "Resultado") else None,
                "concepto": comprobante.Concepto,
                "tipo_documento_receptor": comprobante.DocTipo,
                "numero_documento_receptor": comprobante.DocNro
            }
            
            # Agregar información de IVA si está disponible
            if hasattr(comprobante, "Iva") and comprobante.Iva is not None:
                iva_items = []
                for iva in comprobante.Iva.AlicIva:
                    iva_items.append({
                        "id": iva.Id,
                        "base_imponible": iva.BaseImp,
                        "importe": iva.Importe
                    })
                result["iva_detalle"] = iva_items
            
            return result
            
        except Fault as f:
            logger.error(f"Error SOAP al consultar comprobante: {f}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar comprobante en AFIP: {str(f)}"
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Error al consultar comprobante: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar comprobante: {str(e)}"
            )

# Crear una instancia para uso general
afip_manager = AfipManager(modo_produccion=False)  # Cambiar a True para producción