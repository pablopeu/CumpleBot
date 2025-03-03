# -*- coding: utf-8 -*-
# Copyright 2025 Pablo Untroib (PEU)
#
# X: https://x.com/PEU_AR   Instagram: https://www.instagram.com/peu_ar/
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import datetime
import logging
import telebot
import time
import os
from pathlib import Path

# Configuración del logging con codificación UTF-8
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot_cumpleanos.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Cargar configuración desde config.txt
def cargar_configuracion():
    try:
        with open('config.txt', 'r') as file:
            lineas = file.readlines()
            config = {}
            for linea in lineas:
                if ':' in linea:
                    clave, valor = linea.strip().split(':', 1)
                    config[clave.strip()] = valor.strip()
            if 'token' not in config or 'chat_id' not in config:
                raise ValueError("El archivo config.txt debe contener 'token' y 'chat_id'")
            return config
    except Exception as e:
        logger.error(f"Error al cargar la configuración: {e}")
        raise

# Cargar datos de cumpleaños desde cumpleanos.csv
def cargar_cumpleanos():
    cumpleanos = []
    try:
        with open('cumpleanos.csv', 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                if len(row) >= 3:
                    nombre = row[0].strip()
                    dia = int(row[1].strip())
                    mes = int(row[2].strip())
                    anio = int(row[3].strip()) if len(row) > 3 and row[3].strip() else 1900
                    cumpleanos.append({"nombre": nombre, "dia": dia, "mes": mes, "anio": anio})
        return cumpleanos
    except Exception as e:
        logger.error(f"Error al cargar los cumpleaños: {e}")
        raise

# Verificar si hay cumpleaños hoy
def verificar_cumpleanos_hoy():
    fecha_actual = datetime.datetime.now()
    dia_actual = fecha_actual.day
    mes_actual = fecha_actual.month
    anio_actual = fecha_actual.year
    
    cumpleanos = cargar_cumpleanos()
    cumpleaneros_hoy = []
    
    for persona in cumpleanos:
        if persona["dia"] == dia_actual and persona["mes"] == mes_actual:
            if persona["anio"] == 1900:
                cumpleaneros_hoy.append({"nombre": persona["nombre"], "edad": None})
            else:
                edad = anio_actual - persona["anio"]
                if (mes_actual, dia_actual) < (persona["mes"], persona["dia"]):
                    edad -= 1
                cumpleaneros_hoy.append({"nombre": persona["nombre"], "edad": edad})
    
    return cumpleaneros_hoy

# Enviar mensaje de cumpleaños al chat configurado
def enviar_mensaje_cumpleanos():
    try:
        config = cargar_configuracion()
        token = config['token']
        chat_id = config['chat_id']
        
        bot = telebot.TeleBot(token)
        cumpleaneros = verificar_cumpleanos_hoy()
        
        if cumpleaneros:
            mensajes = []
            for persona in cumpleaneros:
                if persona["edad"] is None:
                    mensajes.append(f"¡Hoy es el cumpleaños de {persona['nombre']}!")
                else:
                    mensajes.append(f"¡Hoy es el cumpleaños de {persona['nombre']}, quien cumple {persona['edad']} años!")
            mensaje_final = "\n".join(mensajes)
            bot.send_message(chat_id, mensaje_final)
            logger.info(f"Mensaje de cumpleaños enviado para: {', '.join([p['nombre'] for p in cumpleaneros])}")
        else:
            logger.info("Hoy no hay cumpleaños para celebrar.")
    except Exception as e:
        logger.error(f"Error al enviar mensaje de cumpleaños: {e}")

# Generar lista de cumpleaños
def lista_cumpleanos():
    cumpleanos = cargar_cumpleanos()
    lista = []
    for persona in cumpleanos:
        if persona["anio"] == 1900:
            lista.append(f"{persona['nombre']}: {persona['dia']:02d}/{persona['mes']:02d}")
        else:
            lista.append(f"{persona['nombre']}: {persona['dia']:02d}/{persona['mes']:02d}/{persona['anio']}")
    return "\n".join(lista) if lista else "No hay cumpleaños registrados."

# Validar fecha, permitiendo 1900 como excepción
def validar_fecha(dia, mes, anio):
    if anio != 1900 and anio < 1950:
        return False
    try:
        if anio != 1900:
            datetime.datetime(anio, mes, dia)
        return True
    except ValueError:
        return False

def modificar_cumpleanos(nombre, dia, mes, anio):
    cumpleanos = cargar_cumpleanos()
    nombre_lower = nombre.lower()
    encontrado = False
    
    # Verificar si el nombre ingresado termina con "QEPD-"
    eliminar_qepd = nombre_lower.endswith(' qepd-')
    if eliminar_qepd:
        # Eliminar "QEPD-" del nombre ingresado para la búsqueda
        nombre_busqueda = nombre[:-6].strip()  # Quitar " QEPD-"
    else:
        nombre_busqueda = nombre
    
    # Buscar coincidencia con los dos primeros nombres
    nombres_ingresados = nombre_busqueda.split()[:2]
    for persona in cumpleanos:
        persona_nombres = persona["nombre"].split()
        if len(persona_nombres) >= 2 and ' '.join(persona_nombres[:2]).lower() == ' '.join(nombres_ingresados).lower():
            if eliminar_qepd:
                # Eliminar "QEPD" si está presente al final del nombre
                if persona["nombre"].lower().endswith(' qepd'):
                    persona["nombre"] = ' '.join(persona["nombre"].split()[:-1])
                # No agregar "QEPD" de nuevo, ya que se especificó "QEPD-"
            else:
                # Si se agrega "QEPD" (sin guion) y no está presente
                if nombre_lower.endswith(' qepd') and not persona["nombre"].lower().endswith(' qepd'):
                    persona["nombre"] = persona["nombre"] + ' QEPD'
            # Actualizar la fecha
            persona["dia"] = dia
            persona["mes"] = mes
            persona["anio"] = anio
            encontrado = True
            break
    
    if not encontrado:
        # Si no hay coincidencia, crear nueva entrada
        palabras = nombre.split()
        if eliminar_qepd:
            # Si termina en "QEPD-", grabar sin "QEPD"
            nombre_formateado = ' '.join([
                palabra.capitalize() for palabra in palabras[:-1]  # Excluir "QEPD-"
            ])
        else:
            # Formatear normalmente, con "QEPD" en mayúsculas si está presente
            nombre_formateado = ' '.join([
                palabra.upper() if palabra.lower() == 'qepd' else palabra.capitalize()
                for palabra in palabras
            ])
        cumpleanos.append({"nombre": nombre_formateado, "dia": dia, "mes": mes, "anio": anio})
    
    # Guardar los cambios en el CSV
    with open('cumpleanos.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        for persona in cumpleanos:
            writer.writerow([persona["nombre"], persona["dia"], persona["mes"], persona["anio"]])

def proximo_cumpleanos():
    cumpleanos = cargar_cumpleanos()
    hoy = datetime.datetime.now().date()
    proximo = None
    menor_diferencia = None

    for persona in cumpleanos:
        # Crear la fecha del cumpleaños en el año actual
        try:
            cumple_anio_actual = datetime.date(hoy.year, persona['mes'], persona['dia'])
        except ValueError:
            # Si la fecha no es válida (ej. 29 de febrero en año no bisiesto), saltar
            continue

        # Si el cumpleaños ya pasó este año, usar el próximo año
        if cumple_anio_actual < hoy:
            try:
                cumple_anio_actual = datetime.date(hoy.year + 1, persona['mes'], persona['dia'])
            except ValueError:
                continue

        # Calcular la diferencia en días
        diferencia = (cumple_anio_actual - hoy).days

        if menor_diferencia is None or diferencia < menor_diferencia:
            menor_diferencia = diferencia
            proximo = persona
            proximo['fecha_cumple'] = cumple_anio_actual

    if proximo:
        mensaje = f"El próximo cumpleaños es de {proximo['nombre']} el {proximo['fecha_cumple'].strftime('%d/%m/%Y')}"
        if proximo['anio'] != 1900:
            edad = proximo['fecha_cumple'].year - proximo['anio']
            mensaje += f", quien cumplirá {edad} años."
        else:
            mensaje += "."
        return mensaje
    else:
        return "No hay cumpleaños registrados."

# Configuración del bot y manejadores de comandos
config = cargar_configuracion()
token = config['token']
bot = telebot.TeleBot(token)

@bot.message_handler(commands=['lista'])
def manejar_lista(message):
    lista = lista_cumpleanos()
    bot.send_message(message.chat.id, lista)

@bot.message_handler(commands=['modificar'])
def manejar_modificar(message):
    try:
        partes = message.text.split(' ', 1)[1].split(',')
        if len(partes) != 4:
            raise ValueError("Formato incorrecto. Uso: /modificar nombre completo,dia,mes,año")
        nombre = partes[0].strip()
        dia = int(partes[1].strip())
        mes = int(partes[2].strip())
        anio = int(partes[3].strip())
        
        if not validar_fecha(dia, mes, anio):
            bot.send_message(message.chat.id, "Fecha inválida o año no permitido (debe ser 1900 o posterior a 1950).")
            return
        
        modificar_cumpleanos(nombre, dia, mes, anio)
        bot.send_message(message.chat.id, "Cumpleaños actualizado/creado exitosamente.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Error: {str(e)}")

@bot.message_handler(commands=['ayuda'])
def manejar_ayuda(message):
    ayuda = (
        "Comandos disponibles:\n"
        "/lista - Muestra la lista de cumpleaños\n"
        "/modificar nombre completo,dia,mes,año - Modifica o crea una entrada de cumpleaños\n"
        "/cumple - Informa si hoy hay cumpleaños\n"
        "/proximo - Muestra el próximo cumpleaños\n"
        "/ayuda - Muestra esta ayuda"
    )
    bot.send_message(message.chat.id, ayuda)

@bot.message_handler(commands=['cumple'])
def manejar_cumple(message):
    cumpleaneros = verificar_cumpleanos_hoy()
    if cumpleaneros:
        mensajes = []
        for persona in cumpleaneros:
            if persona["edad"] is None:
                mensajes.append(f"¡Hoy es el cumpleaños de {persona['nombre']}!")
            else:
                mensajes.append(f"¡Hoy es el cumpleaños de {persona['nombre']}, quien cumple {persona['edad']} años!")
        mensaje_final = "\n".join(mensajes)
    else:
        mensaje_final = "Hoy no hay cumpleaños para celebrar."
    bot.send_message(message.chat.id, mensaje_final)

@bot.message_handler(commands=['proximo'])
def manejar_proximo(message):
    mensaje = proximo_cumpleanos()
    bot.send_message(message.chat.id, mensaje)

# Ejecución del bot
if __name__ == "__main__":
    try:
        inicio = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"Bot arrancado correctamente el {inicio}")
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Error general en la ejecución: {e}")
