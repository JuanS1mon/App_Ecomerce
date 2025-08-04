#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""



Módulo de integración con AFIP para facturación electrónica Argentina
Proporciona funciones para autenticación, generación de CAE, consulta de comprobantes, etc.
Basado en las especificaciones de WebServices de AFIP:
- WSAA (Autenticación)
- WSFEV1 (Factura Electrónica V1)
"""

import os
import logging
import tempfile
import subprocess
import datetime
import json
import base64
import xml.etree.ElementTree as ET
import requests
from zeep import Client
from zeep.transports import Transport
from zeep.exceptions import Fault
from OpenSSL import crypto
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException, status
from pathlib import Path
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Constantes de configuración
CERT_CONFIG = {
    'CERT_FILE': None,  # Path al certificado
    'PRIVATEKEY_FILE': None,  # Path a la clave privada
    'PASSPHRASE': None,  # Contraseña de la clave privada (si existe)
}

WSAA_CONFIG = {
    'WSDL_URL_PROD': 'https://wsaa.afip.gov.ar/ws/services/LoginCms?wsdl',
    'WSDL_URL_TEST': 'https://wsaahomo.afip.gov.ar/ws/services/LoginCms?wsdl',
    'SERVICE': 'wsfe',  # Servicio que se va a utilizar
    'TTL': 24 * 3600,   # Tiempo de validez del ticket (24 horas)
}

WSFE_CONFIG = {
    'WSDL_URL_PROD': 'https://servicios1.afip.gov.ar/wsfev1/service.asmx?WSDL',
    'WSDL_URL_TEST': 'https://wswhomo.afip.gov.ar/wsfev1/service.asmx?WSDL',
}

# Clase principal para integración con AFIP
class AfipIntegration:
    def __init__(self, test_mode=True, db=None, cuit=None):
        """
        Inicializa la integración con AFIP
        
        Args:
            test_mode (bool): Si True, se utiliza el entorno de homologación (testing)
            db: Conexión a la base de datos
            cuit (str): CUIT del emisor
        """
        self.test_mode = test_mode
        self.db = db
        self.cuit = cuit
        self.token = None
        self.sign = None
        self.expiration = None
        
        # Cargar configuración
        self.load_config()
        
        # URLs de servicios según el modo
        self.wsaa_url = WSAA_CONFIG['WSDL_URL_TEST'] if test_mode else WSAA_CONFIG['WSDL_URL_PROD']
        self.wsfe_url = WSFE_CONFIG['WSDL_URL_TEST'] if test_mode else WSFE_CONFIG['WSDL_URL_PROD']
        
        # Intentar cargar credenciales existentes
        self.load_credentials()
    
    def load_config(self):
        """Carga la configuración desde la base de datos o archivo de configuración"""
        try:
            if self.db:
                # Intentar cargar desde la base de datos
                query = text("""
                    SELECT clave, valor FROM configuracion
                    WHERE grupo = 'AFIP'
                """)
                result = self.db.execute(query).fetchall()
                
                config = {}
                for row in result:
                    config[row[0]] = row[1]
                
                # Asignar valores de configuración
                if 'CERT_FILE' in config:
                    CERT_CONFIG['CERT_FILE'] = config['CERT_FILE']
                if 'PRIVATEKEY_FILE' in config:
                    CERT_CONFIG['PRIVATEKEY_FILE'] = config['PRIVATEKEY_FILE']
                if 'PASSPHRASE' in config:
                    CERT_CONFIG['PASSPHRASE'] = config['PASSPHRASE']
                if 'CUIT' in config and not self.cuit:
                    self.cuit = config['CUIT']
            else:
                # Buscar archivo de configuración en el directorio de la aplicación
                config_file = Path(__file__).parent / 'afip_config.json'
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    # Asignar valores de configuración
                    if 'CERT_FILE' in config:
                        CERT_CONFIG['CERT_FILE'] = config['CERT_FILE']
                    if 'PRIVATEKEY_FILE' in config:
                        CERT_CONFIG['PRIVATEKEY_FILE'] = config['PRIVATEKEY_FILE']
                    if 'PASSPHRASE' in config:
                        CERT_CONFIG['PASSPHRASE'] = config['PASSPHRASE']
                    if 'CUIT' in config and not self.cuit:
                        self.cuit = config['CUIT']
        except Exception as e:
            logger.error(f"Error al cargar configuración AFIP: {e}")
    
    def load_credentials(self):
        """Carga las credenciales (token, sign) desde la base de datos o archivo"""
        try:
            if self.db:
                # Intentar cargar desde la base de datos
                query = text("""
                    SELECT token, sign, expiracion FROM afip_credenciales
                    WHERE servicio = :servicio
                    AND test_mode = :test_mode
                    AND expiracion > GETDATE()
                    ORDER BY expiracion DESC
                """)
                result = self.db.execute(query, {
                    'servicio': WSAA_CONFIG['SERVICE'],
                    'test_mode': 1 if self.test_mode else 0
                }).first()
                
                if result:
                    self.token = result[0]
                    self.sign = result[1]
                    self.expiration = result[2]
                    logger.info(f"Credenciales AFIP cargadas correctamente. Expiración: {self.expiration}")
            else:
                # Buscar archivo de credenciales en el directorio temporal
                cred_file = Path(tempfile.gettempdir()) / f"afip_credentials_{WSAA_CONFIG['SERVICE']}_{1 if self.test_mode else 0}.json"
                if cred_file.exists():
                    with open(cred_file, 'r') as f:
                        creds = json.load(f)
                    
                    # Verificar que las credenciales no hayan expirado
                    expiration = datetime.fromisoformat(creds['expiration'])
                    if expiration > datetime.now():
                        self.token = creds['token']
                        self.sign = creds['sign']
                        self.expiration = expiration
                        logger.info(f"Credenciales AFIP cargadas correctamente. Expiración: {self.expiration}")
        except Exception as e:
            logger.error(f"Error al cargar credenciales AFIP: {e}")
    
    def save_credentials(self):
        """Guarda las credenciales (token, sign) en la base de datos o archivo"""
        try:
            if self.db:
                # Guardar en la base de datos
                # Primero borrar credenciales anteriores
                query = text("""
                    DELETE FROM afip_credenciales
                    WHERE servicio = :servicio
                    AND test_mode = :test_mode
                """)
                self.db.execute(query, {
                    'servicio': WSAA_CONFIG['SERVICE'],
                    'test_mode': 1 if self.test_mode else 0
                })
                
                # Insertar nuevas credenciales
                query = text("""
                    INSERT INTO afip_credenciales (servicio, test_mode, token, sign, expiracion)
                    VALUES (:servicio, :test_mode, :token, :sign, :expiracion)
                """)
                self.db.execute(query, {
                    'servicio': WSAA_CONFIG['SERVICE'],
                    'test_mode': 1 if self.test_mode else 0,
                    'token': self.token,
                    'sign': self.sign,
                    'expiracion': self.expiration
                })
                self.db.commit()
            else:
                # Guardar en archivo temporal
                cred_file = Path(tempfile.gettempdir()) / f"afip_credentials_{WSAA_CONFIG['SERVICE']}_{1 if self.test_mode else 0}.json"
                with open(cred_file, 'w') as f:
                    json.dump({
                        'token': self.token,
                        'sign': self.sign,
                        'expiration': self.expiration.isoformat()
                    }, f)
        except Exception as e:
            logger.error(f"Error al guardar credenciales AFIP: {e}")
    
    def authenticate(self, force=False):
        """
        Autentica con AFIP para obtener el token y sign
        
        Args:
            force (bool): Si True, fuerza la autenticación aunque haya credenciales válidas
            
        Returns:
            bool: True si la autenticación fue exitosa
        """
        # Si ya tenemos credenciales válidas y no se fuerza autenticación, no hacer nada
        if not force and self.token and self.sign and self.expiration and datetime.now() < self.expiration:
            return True
        
        try:
            # Generar TRA (Ticket de Requerimiento de Acceso)
            tra = self._generar_tra()
            
            # Firmar el TRA
            cms = self._firmar_tra(tra)
            
            # Codificar el CMS en base64
            cms_base64 = base64.b64encode(cms).decode()
            
            # Consumir servicio WSAA
            client = Client(self.wsaa_url)
            result = client.service.loginCms(cms_base64)
            
            # Procesar respuesta
            if result:
                # Convertir respuesta XML a objeto
                response = ET.fromstring(result)
                
                # Extraer token y sign
                self.token = response.find('.//token').text
                self.sign = response.find('.//sign').text
                
                # Calcular expiración
                expiration_str = response.find('.//expirationTime').text
                self.expiration = datetime.strptime(expiration_str, '%Y-%m-%dT%H:%M:%S.%f%z').replace(tzinfo=None)
                
                # Guardar credenciales
                self.save_credentials()
                
                logger.info(f"Autenticación AFIP exitosa. Expiración: {self.expiration}")
                return True
            else:
                logger.error("No se obtuvo respuesta del servicio WSAA")
                return False
                
        except Exception as e:
            logger.error(f"Error en autenticación AFIP: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False
    
    def _generar_tra(self):
        """
        Genera el TRA (Ticket de Requerimiento de Acceso)
        
        Returns:
            bytes: XML del TRA en formato bytes
        """
        # Generar fechas
        now = datetime.now()
        expiration = now + timedelta(seconds=WSAA_CONFIG['TTL'])
        
        # Crear estructura XML
        tra = ET.Element('loginTicketRequest')
        tra.set('version', '1.0')
        
        header = ET.SubElement(tra, 'header')
        
        # Agregar datos al header
        uniqueId = ET.SubElement(header, 'uniqueId')
        uniqueId.text = str(int(now.timestamp()))
        
        generationTime = ET.SubElement(header, 'generationTime')
        generationTime.text = (now - timedelta(seconds=120)).strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        expirationTime = ET.SubElement(header, 'expirationTime')
        expirationTime.text = expiration.strftime('%Y-%m-%dT%H:%M:%S-03:00')
        
        # Agregar servicio
        service = ET.SubElement(tra, 'service')
        service.text = WSAA_CONFIG['SERVICE']
        
        # Convertir a string XML
        return ET.tostring(tra, encoding='UTF-8')
    
    def _firmar_tra(self, tra):
        """
        Firma el TRA con el certificado y clave privada
        
        Args:
            tra (bytes): XML del TRA en formato bytes
            
        Returns:
            bytes: CMS con el TRA firmado
        """
        # Verificar que existan certificado y clave privada
        if not CERT_CONFIG['CERT_FILE'] or not CERT_CONFIG['PRIVATEKEY_FILE']:
            raise Exception("No se configuraron certificado y clave privada")
        
        # Cargar certificado
        with open(CERT_CONFIG['CERT_FILE'], 'r') as cert_file:
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_file.read())
        
        # Cargar clave privada
        with open(CERT_CONFIG['PRIVATEKEY_FILE'], 'r') as key_file:
            if CERT_CONFIG['PASSPHRASE']:
                key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read(), 
                                             CERT_CONFIG['PASSPHRASE'].encode())
            else:
                key = crypto.load_privatekey(crypto.FILETYPE_PEM, key_file.read())
        
        # Crear PKCS7/CMS
        bio_in = crypto._new_mem_buf(tra)
        p7 = crypto._lib.PKCS7_sign(cert._x509, key._pkey, crypto._ffi.NULL, bio_in, crypto._lib.PKCS7_BINARY)
        bio_out = crypto._new_mem_buf()
        crypto._lib.i2d_PKCS7_bio(bio_out, p7)
        sigbio = crypto._bio_to_string(bio_out)
        
        return sigbio
    
    def get_client(self):
        """
        Obtiene un cliente SOAP para el servicio WSFEV1
        
        Returns:
            Client: Cliente SOAP de Zeep
        """
        # Verificar autenticación
        if not self.authenticate():
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="No se pudo autenticar con AFIP"
            )
        
        # Crear cliente
        try:
            client = Client(self.wsfe_url)
            return client
        except Exception as e:
            logger.error(f"Error al crear cliente WSFEV1: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al crear cliente WSFEV1: {str(e)}"
            )
    
    def get_server_status(self):
        """
        Consulta el estado de los servidores de AFIP
        
        Returns:
            dict: Estado de los servidores
        """
        try:
            client = self.get_client()
            result = client.service.FEDummy()
            
            return {
                'AppServer': result.AppServer,
                'DbServer': result.DbServer,
                'AuthServer': result.AuthServer
            }
        except Exception as e:
            logger.error(f"Error al consultar estado de servidores AFIP: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar estado de servidores AFIP: {str(e)}"
            )
    
    def get_tipos_comprobantes(self):
        """
        Obtiene los tipos de comprobantes disponibles
        
        Returns:
            list: Lista de tipos de comprobantes
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetTiposCbte({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if result.FECAEDetResponse and hasattr(result, 'ResultGet'):
                return [
                    {
                        'id': item.Id,
                        'descripcion': item.Desc,
                        'vigencia_desde': item.FchDesde,
                        'vigencia_hasta': item.FchHasta
                    }
                    for item in result.ResultGet.CbteTipo
                ]
            else:
                logger.warning(f"No se obtuvieron tipos de comprobantes. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tipos de comprobantes: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tipos de comprobantes: {str(e)}"
            )
    
    def get_tipos_conceptos(self):
        """
        Obtiene los tipos de conceptos disponibles
        
        Returns:
            list: Lista de tipos de conceptos
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetTiposConcepto({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if hasattr(result, 'ResultGet'):
                return [
                    {
                        'id': item.Id,
                        'descripcion': item.Desc,
                        'vigencia_desde': item.FchDesde,
                        'vigencia_hasta': item.FchHasta
                    }
                    for item in result.ResultGet.ConceptoTipo
                ]
            else:
                logger.warning(f"No se obtuvieron tipos de conceptos. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tipos de conceptos: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tipos de conceptos: {str(e)}"
            )
    
    def get_tipos_documentos(self):
        """
        Obtiene los tipos de documentos disponibles
        
        Returns:
            list: Lista de tipos de documentos
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetTiposDoc({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if hasattr(result, 'ResultGet'):
                return [
                    {
                        'id': item.Id,
                        'descripcion': item.Desc,
                        'vigencia_desde': item.FchDesde,
                        'vigencia_hasta': item.FchHasta
                    }
                    for item in result.ResultGet.DocTipo
                ]
            else:
                logger.warning(f"No se obtuvieron tipos de documentos. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tipos de documentos: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tipos de documentos: {str(e)}"
            )
    
    def get_tipos_iva(self):
        """
        Obtiene los tipos de IVA disponibles
        
        Returns:
            list: Lista de tipos de IVA
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetTiposIva({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if hasattr(result, 'ResultGet'):
                return [
                    {
                        'id': item.Id,
                        'descripcion': item.Desc,
                        'vigencia_desde': item.FchDesde,
                        'vigencia_hasta': item.FchHasta
                    }
                    for item in result.ResultGet.IvaTipo
                ]
            else:
                logger.warning(f"No se obtuvieron tipos de IVA. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tipos de IVA: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tipos de IVA: {str(e)}"
            )
    
    def get_tipos_monedas(self):
        """
        Obtiene los tipos de monedas disponibles
        
        Returns:
            list: Lista de tipos de monedas
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetTiposMonedas({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if hasattr(result, 'ResultGet'):
                return [
                    {
                        'id': item.Id,
                        'descripcion': item.Desc,
                        'vigencia_desde': item.FchDesde,
                        'vigencia_hasta': item.FchHasta
                    }
                    for item in result.ResultGet.Moneda
                ]
            else:
                logger.warning(f"No se obtuvieron tipos de monedas. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener tipos de monedas: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener tipos de monedas: {str(e)}"
            )
    
    def get_punto_venta(self):
        """
        Obtiene los puntos de venta disponibles
        
        Returns:
            list: Lista de puntos de venta
        """
        try:
            client = self.get_client()
            result = client.service.FEParamGetPtosVenta({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                }
            })
            
            if hasattr(result, 'ResultGet'):
                return [
                    {
                        'numero': item.Nro,
                        'emision_tipo': item.EmisionTipo,
                        'bloqueado': item.Bloqueado,
                        'fecha_baja': item.FchBaja
                    }
                    for item in result.ResultGet.PtoVenta
                ]
            else:
                logger.warning(f"No se obtuvieron puntos de venta. Respuesta: {result}")
                return []
                
        except Exception as e:
            logger.error(f"Error al obtener puntos de venta: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener puntos de venta: {str(e)}"
            )
    
    def get_ultimo_comprobante(self, punto_venta: int, tipo_comprobante: int):
        """
        Obtiene el último número de comprobante para un punto de venta y tipo de comprobante
        
        Args:
            punto_venta (int): Número de punto de venta
            tipo_comprobante (int): Tipo de comprobante
            
        Returns:
            int: Último número de comprobante
        """
        try:
            client = self.get_client()
            result = client.service.FECompUltimoAutorizado({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                },
                'PtoVta': punto_venta,
                'CbteTipo': tipo_comprobante
            })
            
            if hasattr(result, 'CbteNro'):
                return result.CbteNro
            else:
                logger.warning(f"No se obtuvo último comprobante. Respuesta: {result}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Error al obtener último comprobante: {result.Errors.Err.Msg if hasattr(result, 'Errors') else 'Error desconocido'}"
                )
                
        except Exception as e:
            logger.error(f"Error al obtener último comprobante: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al obtener último comprobante: {str(e)}"
            )
    
    def generar_cae(self, factura: Dict[str, Any]):
        """
        Genera un CAE (Código de Autorización Electrónica) para una factura
        
        Args:
            factura (dict): Datos de la factura
            
        Returns:
            dict: Resultado de la generación del CAE
        """
        try:
            # Verificar que tenemos todos los datos necesarios
            required_fields = [
                'tipo_comprobante', 'punto_venta', 'fecha_emision',
                'tipo_documento', 'nro_documento', 'importe_total',
                'items'
            ]
            
            for field in required_fields:
                if field not in factura:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Falta el campo {field} en la factura"
                    )
            
            # Obtener el próximo número de comprobante
            try:
                numero_comprobante = self.get_ultimo_comprobante(
                    factura['punto_venta'],
                    factura['tipo_comprobante']
                ) + 1
            except Exception as e:
                logger.warning(f"Error al obtener último comprobante: {e}. Se utilizará 1.")
                numero_comprobante = 1
            
            # Formatear fecha en formato AAAAMMDD
            if isinstance(factura['fecha_emision'], str):
                # Si es string, convertir a date
                fecha_emision = datetime.strptime(factura['fecha_emision'], '%Y-%m-%d').date()
            elif isinstance(factura['fecha_emision'], datetime):
                # Si es datetime, extraer date
                fecha_emision = factura['fecha_emision'].date()
            else:
                # Asumir que ya es date
                fecha_emision = factura['fecha_emision']
            
            fecha_str = fecha_emision.strftime('%Y%m%d')
            
            # Preparar datos para la solicitud
            # Encabezado
            encabezado = {
                'CantReg': 1,  # Cantidad de registros
                'PtoVta': factura['punto_venta'],
                'CbteTipo': factura['tipo_comprobante']
            }
            
            # Calcular importes
            importe_total = factura['importe_total']
            importe_neto = factura.get('importe_neto', 0)
            importe_iva = factura.get('importe_iva', 0)
            
            # Si no se proporcionó importe neto pero sí importe IVA, calcularlo
            if importe_neto == 0 and importe_iva > 0:
                # Asumir IVA 21% si no se especifica
                iva_porcentaje = factura.get('iva_porcentaje', 21)
                importe_neto = importe_total / (1 + iva_porcentaje/100)
                importe_neto = round(importe_neto, 2)
            # Si no se proporcionó importe IVA pero sí importe neto, calcularlo
            elif importe_iva == 0 and importe_neto > 0:
                importe_iva = importe_total - importe_neto
                importe_iva = round(importe_iva, 2)
            # Si no se proporcionaron ambos, asumir que el total incluye IVA al 21%
            elif importe_neto == 0 and importe_iva == 0:
                # Asumir IVA 21% si no se especifica
                iva_porcentaje = factura.get('iva_porcentaje', 21)
                importe_neto = importe_total / (1 + iva_porcentaje/100)
                importe_neto = round(importe_neto, 2)
                importe_iva = importe_total - importe_neto
                importe_iva = round(importe_iva, 2)
            
            # Preparar comprobante
            comprobante = {
                'Concepto': factura.get('concepto', 1),  # 1=Productos, 2=Servicios, 3=Productos y Servicios
                'DocTipo': factura['tipo_documento'],
                'DocNro': factura['nro_documento'],
                'CbteDesde': numero_comprobante,
                'CbteHasta': numero_comprobante,
                'CbteFch': fecha_str,
                'ImpTotal': round(importe_total, 2),
                'ImpTotConc': 0,  # Importe neto no gravado
                'ImpNeto': round(importe_neto, 2),
                'ImpOpEx': 0,  # Importe exento
                'ImpTrib': 0,  # Importe de tributos
                'ImpIVA': round(importe_iva, 2),
                'FchServDesde': factura.get('fecha_servicio_desde', None),
                'FchServHasta': factura.get('fecha_servicio_hasta', None),
                'FchVtoPago': factura.get('fecha_vencimiento_pago', None),
                'MonId': factura.get('moneda', 'PES'),  # PES=Pesos
                'MonCotiz': factura.get('cotizacion', 1)  # Cotización de la moneda
            }
            
            # Si el concepto incluye servicios (2 o 3), las fechas de servicio son obligatorias
            if comprobante['Concepto'] in [2, 3]:
                # Si no se proporcionaron fechas de servicio, usar fecha de emisión
                if not comprobante['FchServDesde']:
                    comprobante['FchServDesde'] = fecha_str
                if not comprobante['FchServHasta']:
                    comprobante['FchServHasta'] = fecha_str
                if not comprobante['FchVtoPago']:
                    comprobante['FchVtoPago'] = fecha_str
            
            # Preparar detalles de IVA (alícuotas)
            iva_items = []
            if factura.get('items'):
                # Agrupar items por alícuota de IVA
                iva_por_alicuota = {}
                for item in factura['items']:
                    alicuota = item.get('alicuota_iva', 21)
                    if alicuota not in iva_por_alicuota:
                        iva_por_alicuota[alicuota] = {
                            'base_imponible': 0,
                            'importe': 0
                        }
                    
                    # Sumar base imponible e importe
                    iva_por_alicuota[alicuota]['base_imponible'] += item.get('subtotal', 0)
                    iva_por_alicuota[alicuota]['importe'] += item.get('importe_iva', 0)
                
                # Convertir a formato requerido por AFIP
                for alicuota, datos in iva_por_alicuota.items():
                    # Mapear alícuota a código de AFIP
                    # Por ejemplo: 21% = 5, 10.5% = 4, 27% = 6, 0% = 3
                    codigo_alicuota = 5  # Default: 21%
                    if alicuota == 10.5:
                        codigo_alicuota = 4
                    elif alicuota == 27:
                        codigo_alicuota = 6
                    elif alicuota == 0:
                        codigo_alicuota = 3
                    
                    iva_items.append({
                        'Id': codigo_alicuota,
                        'BaseImp': round(datos['base_imponible'], 2),
                        'Importe': round(datos['importe'], 2)
                    })
            
            # Si no hay items, agregar una alícuota por defecto
            if not iva_items:
                iva_items.append({
                    'Id': 5,  # Default: 21%
                    'BaseImp': round(importe_neto, 2),
                    'Importe': round(importe_iva, 2)
                })
            
            # Crear cliente SOAP
            client = self.get_client()
            
            # Preparar datos para la solicitud
            request_data = {
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                },
                'FeCAEReq': {
                    'FeCabReq': encabezado,
                    'FeDetReq': {
                        'FECAEDetRequest': [comprobante]
                    }
                }
            }
            
            # Si hay alícuotas de IVA, agregarlas
            if iva_items:
                request_data['FeCAEReq']['FeDetReq']['FECAEDetRequest'][0]['Iva'] = {
                    'AlicIva': iva_items
                }
            
            # Enviar solicitud
            result = client.service.FECAESolicitar(**request_data)
            
            # Procesar respuesta
            if hasattr(result, 'FeDetResp') and result.FeDetResp.FECAEDetResponse:
                detalle = result.FeDetResp.FECAEDetResponse[0]
                
                # Verificar si hay errores
                errores = []
                if hasattr(result, 'Errors') and result.Errors:
                    for error in result.Errors.Err:
                        errores.append({
                            'codigo': error.Code,
                            'mensaje': error.Msg
                        })
                
                # Verificar si se generó el CAE
                if hasattr(detalle, 'CAE') and detalle.CAE:
                    # Calcular fecha de vencimiento del CAE
                    fecha_vto_cae = None
                    if hasattr(detalle, 'CAEFchVto'):
                        try:
                            # Convertir formato AAAAMMDD a YYYY-MM-DD
                            fecha_vto_str = detalle.CAEFchVto
                            fecha_vto_cae = f"{fecha_vto_str[0:4]}-{fecha_vto_str[4:6]}-{fecha_vto_str[6:8]}"
                        except:
                            fecha_vto_cae = detalle.CAEFchVto
                    
                    # Devolver resultado exitoso
                    return {
                        'cae': detalle.CAE,
                        'cae_vencimiento': fecha_vto_cae,
                        'numero_comprobante': numero_comprobante,
                        'resultado': detalle.Resultado,
                        'punto_venta': factura['punto_venta'],
                        'tipo_comprobante': factura['tipo_comprobante'],
                        'fecha_comprobante': fecha_str
                    }
                else:
                    # Si no hay CAE pero hay observaciones, incluirlas
                    observaciones = []
                    if hasattr(detalle, 'Observaciones') and hasattr(detalle.Observaciones, 'Obs'):
                        for obs in detalle.Observaciones.Obs:
                            observaciones.append({
                                'codigo': obs.Code,
                                'mensaje': obs.Msg
                            })
                    
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail={
                            'resultado': detalle.Resultado if hasattr(detalle, 'Resultado') else 'R',
                            'errores': errores,
                            'observaciones': observaciones
                        }
                    )
            else:
                # Si no hay detalle de respuesta, verificar si hay errores generales
                errores = []
                if hasattr(result, 'Errors') and result.Errors:
                    for error in result.Errors.Err:
                        errores.append({
                            'codigo': error.Code,
                            'mensaje': error.Msg
                        })
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        'resultado': 'R',
                        'errores': errores
                    }
                )
                
        except HTTPException:
            # Re-lanzar excepciones HTTP para mantener el status code
            raise
        except Exception as e:
            logger.error(f"Error al generar CAE: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al generar CAE: {str(e)}"
            )
    
    def consultar_comprobante(self, tipo_comprobante: int, punto_venta: int, numero_comprobante: int):
        """
        Consulta un comprobante emitido
        
        Args:
            tipo_comprobante (int): Tipo de comprobante
            punto_venta (int): Punto de venta
            numero_comprobante (int): Número de comprobante
            
        Returns:
            dict: Datos del comprobante
        """
        try:
            client = self.get_client()
            result = client.service.FECompConsultar({
                'Auth': {
                    'Token': self.token,
                    'Sign': self.sign,
                    'Cuit': self.cuit
                },
                'FeCompConsReq': {
                    'CbteTipo': tipo_comprobante,
                    'PtoVta': punto_venta,
                    'CbteNro': numero_comprobante
                }
            })
            
            if hasattr(result, 'ResultGet'):
                # Convertir fechas de formato AAAAMMDD a YYYY-MM-DD
                fecha_comprobante = None
                fecha_vto_cae = None
                fecha_serv_desde = None
                fecha_serv_hasta = None
                fecha_vto_pago = None
                
                if hasattr(result.ResultGet, 'CbteFch') and result.ResultGet.CbteFch:
                    fecha_str = result.ResultGet.CbteFch
                    fecha_comprobante = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
                
                if hasattr(result.ResultGet, 'FchVto') and result.ResultGet.FchVto:
                    fecha_str = result.ResultGet.FchVto
                    fecha_vto_cae = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
                
                if hasattr(result.ResultGet, 'FchServDesde') and result.ResultGet.FchServDesde:
                    fecha_str = result.ResultGet.FchServDesde
                    fecha_serv_desde = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
                
                if hasattr(result.ResultGet, 'FchServHasta') and result.ResultGet.FchServHasta:
                    fecha_str = result.ResultGet.FchServHasta
                    fecha_serv_hasta = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
                
                if hasattr(result.ResultGet, 'FchVtoPago') and result.ResultGet.FchVtoPago:
                    fecha_str = result.ResultGet.FchVtoPago
                    fecha_vto_pago = f"{fecha_str[0:4]}-{fecha_str[4:6]}-{fecha_str[6:8]}"
                
                # Procesar alícuotas de IVA
                iva_items = []
                if hasattr(result.ResultGet, 'Iva') and hasattr(result.ResultGet.Iva, 'AlicIva'):
                    for alicuota in result.ResultGet.Iva.AlicIva:
                        iva_items.append({
                            'codigo': alicuota.Id,
                            'base_imponible': alicuota.BaseImp,
                            'importe': alicuota.Importe
                        })
                
                # Devolver datos del comprobante
                return {
                    'tipo_comprobante': result.ResultGet.CbteTipo,
                    'punto_venta': result.ResultGet.PtoVta,
                    'numero_comprobante': result.ResultGet.CbteNro,
                    'fecha_comprobante': fecha_comprobante,
                    'cae': result.ResultGet.CodAutorizacion,
                    'cae_vencimiento': fecha_vto_cae,
                    'tipo_documento': result.ResultGet.DocTipo,
                    'nro_documento': result.ResultGet.DocNro,
                    'importe_total': result.ResultGet.ImpTotal,
                    'importe_neto': result.ResultGet.ImpNeto,
                    'importe_iva': result.ResultGet.ImpIVA,
                    'importe_tributos': result.ResultGet.ImpTrib,
                    'importe_exento': result.ResultGet.ImpOpEx,
                    'moneda': result.ResultGet.MonId,
                    'cotizacion': result.ResultGet.MonCotiz,
                    'concepto': result.ResultGet.Concepto,
                    'fecha_servicio_desde': fecha_serv_desde,
                    'fecha_servicio_hasta': fecha_serv_hasta,
                    'fecha_vencimiento_pago': fecha_vto_pago,
                    'resultado': result.ResultGet.Resultado,
                    'iva': iva_items
                }
            else:
                # Si no hay detalle de respuesta, verificar si hay errores
                errores = []
                if hasattr(result, 'Errors') and result.Errors:
                    for error in result.Errors.Err:
                        errores.append({
                            'codigo': error.Code,
                            'mensaje': error.Msg
                        })
                
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        'resultado': 'R',
                        'errores': errores
                    }
                )
                
        except Exception as e:
            logger.error(f"Error al consultar comprobante: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error al consultar comprobante: {str(e)}"
            )

# Funciones de utilidad para ser llamadas desde otros módulos

def inicializar_afip(db=None, test_mode=True, cuit=None):
    """
    Inicializa la integración con AFIP
    
    Args:
        db: Conexión a la base de datos
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        AfipIntegration: Instancia de AfipIntegration
    """
    return AfipIntegration(test_mode=test_mode, db=db, cuit=cuit)

def solicitar_cae(db=None, factura_data=None, test_mode=True, cuit=None):
    """
    Solicita un CAE para una factura
    
    Args:
        db: Conexión a la base de datos
        factura_data (dict): Datos de la factura
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        dict: Resultado de la solicitud del CAE
    """
    if not factura_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se proporcionaron datos de la factura"
        )
    
    afip = inicializar_afip(db=db, test_mode=test_mode, cuit=cuit)
    return afip.generar_cae(factura_data)

def obtener_ultimo_comprobante(db=None, punto_venta=None, tipo_comprobante=None, test_mode=True, cuit=None):
    """
    Obtiene el último número de comprobante para un punto de venta y tipo de comprobante
    
    Args:
        db: Conexión a la base de datos
        punto_venta (int): Número de punto de venta
        tipo_comprobante (int): Tipo de comprobante
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        int: Último número de comprobante
    """
    if not punto_venta or not tipo_comprobante:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere punto de venta y tipo de comprobante"
        )
    
    afip = inicializar_afip(db=db, test_mode=test_mode, cuit=cuit)
    return afip.get_ultimo_comprobante(punto_venta, tipo_comprobante)

def consultar_comprobante(db=None, tipo_comprobante=None, punto_venta=None, numero_comprobante=None, test_mode=True, cuit=None):
    """
    Consulta un comprobante emitido
    
    Args:
        db: Conexión a la base de datos
        tipo_comprobante (int): Tipo de comprobante
        punto_venta (int): Punto de venta
        numero_comprobante (int): Número de comprobante
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        dict: Datos del comprobante
    """
    if not tipo_comprobante or not punto_venta or not numero_comprobante:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requiere tipo de comprobante, punto de venta y número de comprobante"
        )
    
    afip = inicializar_afip(db=db, test_mode=test_mode, cuit=cuit)
    return afip.consultar_comprobante(tipo_comprobante, punto_venta, numero_comprobante)

def verificar_estado_servidores(db=None, test_mode=True, cuit=None):
    """
    Verifica el estado de los servidores de AFIP
    
    Args:
        db: Conexión a la base de datos
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        dict: Estado de los servidores
    """
    afip = inicializar_afip(db=db, test_mode=test_mode, cuit=cuit)
    return afip.get_server_status()

def obtener_parametricas(db=None, test_mode=True, cuit=None):
    """
    Obtiene todas las tablas paramétricas de AFIP
    
    Args:
        db: Conexión a la base de datos
        test_mode (bool): Si True, se utiliza el entorno de homologación
        cuit (str): CUIT del emisor
        
    Returns:
        dict: Tablas paramétricas
    """
    afip = inicializar_afip(db=db, test_mode=test_mode, cuit=cuit)
    
    return {
        'tipos_comprobantes': afip.get_tipos_comprobantes(),
        'tipos_conceptos': afip.get_tipos_conceptos(),
        'tipos_documentos': afip.get_tipos_documentos(),
        'tipos_iva': afip.get_tipos_iva(),
        'tipos_monedas': afip.get_tipos_monedas(),
        'puntos_venta': afip.get_punto_venta()
    }