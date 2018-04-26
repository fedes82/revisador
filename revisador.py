#!/usr/bin/env python

#version
VERSION = 2
##-----------PARA LOG
import logging
from logging import handlers
formatter = logging.Formatter("[%(asctime)s.%(msecs)03d][%(levelname)s][%(message)s]") #, "%d-%m%H:%M:%S")
fh = logging.handlers.RotatingFileHandler('revisador.log', maxBytes=4097152, backupCount=5)
fh.setFormatter(formatter)
from kivy.logger import Logger
Logger.setLevel(logging.INFO)
Logger.addHandler(fh)
##-------- FIN PARA LOG

#### CON DEBUG = True EL ENCODER FUNCIONA EN AUTOMATICO
#### SETEAR EN False PARA OPERACION NORMAL

DEBUG = True
####---------------


#kivy imports
from kivy.app import App
from kivy.lang import Builder
from kivy.cache import Cache
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition, NoTransition
from kivy.uix.image import Image
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.properties import ObjectProperty
from kivy.properties import BooleanProperty
from kivy.properties import BoundedNumericProperty
from kivy.properties import NumericProperty
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.graphics.texture import Texture
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.slider import Slider
from kivy.core.image import Image as MemImage
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.popup import Popup
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.audio import SoundLoader

#PIL imports
from PIL import Image as PILImage
from PIL import ImageFont as PILImageFont
from PIL import ImageDraw as PILImageDraw


#general - imports
import socket
import io
from time import sleep
import atexit
from os import remove 
from os import system
from os import makedirs
from os import listdir
from os.path import expanduser
import shutil
import time
import os.path
import datetime
import StringIO
import threading
import Queue
import multiprocessing as mp
import struct
import json
import copy
import textwrap
import subprocess
from functools import partial
from tendo import singleton
from random import uniform
import signal
import sys

me = singleton.SingleInstance()
#para multiprocessing
from multiprocessing.sharedctypes import Value
from ctypes import  c_int
from ctypes import c_float


### ESTO NO SE SI HACE FALTA, ES POR LAS DUDAS, PARA USAR TODOS LOS 
### NUCLEOS, VEREMOS CUANDO TERMINE
system("taskset -p 0xff %d" % os.getpid())
####
####

###----------------------------------------CONSTANTES
Window.maximize()




class PerroGuardian(Exception):

    def __init__(self, time=5):
        self.time = time
    
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handler)
        signal.alarm(self.time)
    
    def __exit__(self, type, value, traceback):
        signal.alarm(0)
    
    def handler(self, signum, frame):
        raise self


    def __str__(self):
        return "TIMEOUT del codigo subsiguiente, tardo mas de {} segundos".format( self.time)

#CONSTANTES
ICONO = 'img_default/icono.png'


#constantes operar
#CARPETA_SESIONES = expanduser("~")+'/Escritorio/SESIONES/'
CARPETA_SESIONES = 'sesion/'
#constante configuracion
SIN_CONEXION = 'img_default/error-conexion.jpg'
SONIDO_ERROR = 'error.mp3'
#  constantes diagnostico
CONEXION_OK = 'img_default/ok.png'
CONEXION_FAIL = 'img_default/fail.png'
ENCODER_DIAGNOSTICO = 'temporales/metros_diagnostico.txt'
### constantres revisador
CARPETA_SESION_FOTOS = 'sesion/'
CARPETA_TEMPORAL = 'temporales/'
IMG_DEFAULT = 'img_default/imgDefault.jpg'
COMENTARIO = 'comentario.txt'

#globales revisador
archivos_cam1 = []
archivos_cam2 = []
archivos_cam3 = []
indices_marcas = []
comentario = ''



################################################################
### INTERFAZ GRAFICA
class IntInput(TextInput):
    """Como textInput, pero solo permite ingresar numeros del 0 al 9"""
    def insert_text(self, substring,from_undo=False):
        """esto hace el filtro de enteros"""
        #print type(substring), substring
        if substring in ['1','2','3','4','5','6','7','8','9','0']:
            return super(IntInput,self).insert_text(substring, from_undo=from_undo)

class TxtInput(TextInput):
    """Como textInput pero solo permite letras 
    numeros y espacios, los que reemplaza por '_' ."""
    def insert_text(self, substring,from_undo=False):
        """esto hace el filtro de enteros"""
        #print type(substring), substring
        if substring == ' ':
            return super(TxtInput,self).insert_text('_', from_undo=from_undo)
        if substring.lower() in 'abcdefghijklmnopqrstuvwxyz0123456789':
            return super(TxtInput,self).insert_text(substring, from_undo=from_undo)



class MemoryImage(Image):
    """Display an image already loaded in memory."""
    memory_data = ObjectProperty(None)

    #def __init__(self, memory_data, **kwargs):
        #super(MemoryImage, self).__init__(**kwargs)

        #self.memory_data = memory_data

    def on_memory_data(self, *args):
        """Load image from memory."""
        data = StringIO.StringIO(self.memory_data)
        #data = io.BytesIO(self.memory_data)
        with self.canvas:
            self.texture = ImageLoaderPygame(data).texture


class Pantalla_Inicio(Screen):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    selection = ''
    path =''
    
    def load(self,path,filename):
        global CARPETA_SESION_FOTOS
        print path, filename
        #self.dismiss_popup()
        if filename == []:
            CARPETA_SESION_FOTOS = path + '/'
        elif filename[0].endswith('.jpg'):
            CARPETA_SESION_FOTOS = path + '/'
        else:
            CARPETA_SESION_FOTOS = filename[0]+'/'
    
    
    def seleccion_sesion(self):
    
        self.content = Elegir_sesion(load=self.load, cancel=exit)
        self.info_carpeta.text = ''
        self._popup = Popup(title="Seleccionar SESION", content=self.content,
                            size_hint=(0.9, 0.9))
        self._popup.open()
        
    def filtro_carpetas_vacias(self,folder,filename):
        print folder, filename
        return True
    ## fin del revisador 
    
    def mostar_info_carpeta(self,path,filename):
        if filename == []:
            if os.path.exists(path +'/info.txt'):
                with open(path +'/info.txt','r') as info:
                    self.info_carpeta.text = info.read()
            else:
                self.info_carpeta.text = 'NO HAY INFORMACION SOBRE LA SESION'
        elif filename[0].endswith('.jpg'):
            if os.path.exists(path +'/info.txt'):
                with open(path +'/info.txt','r') as info:
                    self.info_carpeta.text = info.read()
            else:
                self.info_carpeta.text = 'NO HAY INFORMACION SOBRE LA SESION'
        else:
            if os.path.exists(filename[0]+'/info.txt'):
                with open(filename[0] +'/info.txt','r') as info:
                    self.info_carpeta.text = info.read()
            else:
                self.info_carpeta.text = 'NO HAY INFORMACION SOBRE LA SESION'

  #      Clock.schedule_once(self.cerrar_popup_reiniciar,5)


class ImageButton(ButtonBehavior, Image):
    pass


class Pantalla_Revisar(Screen):
    btn_playpausa = ObjectProperty()
    velocidad = ObjectProperty()
    comentario = ObjectProperty()
    img1 = ObjectProperty()
    img2 = ObjectProperty()
    img3 = ObjectProperty()
    linea_de_tiempo = ObjectProperty()
    
    DEBUG = True
    Logger.info('REVISADOR: Cominezo revisador')
    archivos_cam1 = []
    archivos_cam2 = []
    archivos_cam3 = []
    indices_marcas = []
    indice = 0
    estado = 'MANUAL'
    
    def crear_fullscreens(self,*largs):
        self.img1_fullscreen = ImageButton(source = self.img1.source, on_release = self.ocultar_pantalla_completa_img1)
        self.img2_fullscreen = ImageButton(source = self.img2.source, on_release = self.ocultar_pantalla_completa_img2)
        self.img3_fullscreen = ImageButton(source = self.img3.source, on_release = self.ocultar_pantalla_completa_img3)
        
    def mostrar_pantalla_completa_img1(self,*largs):
        self.add_widget(self.img1_fullscreen)
    
    def mostrar_pantalla_completa_img2(self,*largs):
        self.add_widget(self.img2_fullscreen)
    
    def mostrar_pantalla_completa_img3(self,*largs):
        self.add_widget(self.img3_fullscreen)
    
    def ocultar_pantalla_completa_img1(self, *largs):
        self.remove_widget(self.img1_fullscreen)
        
    def ocultar_pantalla_completa_img2(self, *largs):
        self.remove_widget(self.img2_fullscreen)
    
    def ocultar_pantalla_completa_img3(self, *largs):
        self.remove_widget(self.img3_fullscreen)
    def on_exit(self):
        Clock.unschedule(self.siguiente)
        self.estado = 'MANUAL'
        self.btn_playpausa.text = 'PLAY'
    
    def borrar_temporales(self,*largs):
        """borra los temporales con la imagen default
            que se pueden haber usado para rellenar las listas 
            de archivos
        """
        if os.path.exists(CARPETA_SESION_FOTOS+IMG_DEFAULT):
            os.remove(CARPETA_SESION_FOTOS+IMG_DEFAULT)
        if os.path.exists(CARPETA_SESION_FOTOS+IMG_DEFAULT):
            os.remove(CARPETA_SESION_FOTOS+IMG_DEFAULT)
        if os.path.exists(CARPETA_SESION_FOTOS+IMG_DEFAULT):
            os.remove(CARPETA_SESION_FOTOS+IMG_DEFAULT)
    
    def play(self):
        if self.estado == 'MANUAL':
            if self.velocidad.text == '':
                vel = 500
            else:
                vel=int(self.velocidad.text)
            Clock.schedule_interval(self.siguiente, vel/1000.0)
            self.estado = 'AUTOMATICO'
            self.btn_playpausa.text = 'STOP'
        else:
            Clock.unschedule(self.siguiente)
            self.estado = 'MANUAL'
            self.btn_playpausa.text = 'PLAY'
        pass
    

    def rellenar_lista(self):
        """Rellena la lista de archivos cuando alguna lista tiene menos que otras
            tambien copia los repetidos
            Los nuevos que pone, les pone nombre cortos, con los metros para que 
            queden acomodados y terminando en FALTA para identificarlos
        """
        cam1 = []
        cam2 = []
        cam3 = []
        print 'entre a relllenar_lista'
        #print cam1
        #print self.archivos_cam1
        for archivo in self.archivos_cam1:
          #  print archivo[0:6]
          #  print int(archivo[0:6])
            cam1.append(int(archivo[0:6]))
        
        for archivo in self.archivos_cam2:
            cam2.append(int(archivo[0:6]))
        
        for archivo in self.archivos_cam3:
            cam3.append(int(archivo[0:6]))

        for i in range(len(cam1)):
            if cam1[i] not in cam2:
                cam2.append(cam1[i])
                self.archivos_cam2.append(self.archivos_cam1[i][0:6]+'m__c2__'+'FALTA')
           #################     else if self.archivos_cam1.endswith('MARCA') and 
            if cam1[i] not in cam3:
                cam3.append(cam1[i])
                self.archivos_cam3.append(self.archivos_cam1[i][0:6]+'m__c3__'+'FALTA')
        cam2.sort()
        self.archivos_cam2.sort()
        cam3.sort()
        self.archivos_cam3.sort()
        for i in range(len(cam2)):
            if cam2[i] not in cam1:
                cam1.append(cam2[i])
                self.archivos_cam1.append(self.archivos_cam2[i][0:6]+'m__c1__'+'FALTA')
            if cam2[i] not in cam3:
                cam3.append(cam1[i])
                self.archivos_cam3.append(self.archivos_cam2[i][0:6]+'m__c3__'+'FALTA')
        cam1.sort()
        self.archivos_cam1.sort()
        cam3.sort()
        self.archivos_cam3.sort()
        for i in range(len(cam3)):
            if cam3[i] not in cam2:
                cam2.append(cam3[i])
                self.archivos_cam2.append(self.archivos_cam3[i][0:6]+'m__c2__'+'FALTA')
            if cam3[i] not in cam1:
                cam1.append(cam3[i])
                self.archivos_cam1.append(self.archivos_cam3[i][0:6]+'m__c3__'+'FALTA')
        cam2.sort()
        self.archivos_cam2.sort()
        cam1.sort()
        self.archivos_cam1.sort()
        if DEBUG:
            Logger.info( 'REVISADOR: rellenar_lista: Lista cam1: {}'.format(cam1))
            Logger.info( 'REVISADOR: rellenar_lista: Lista cam2: {}'.format(cam2))
            Logger.info( 'REVISADOR: rellenar_lista: Lista cam3: {}'.format(cam3))
            Logger.info( 'REVISADOR: Las listas tienen una vez rellenas {},{},{} archivos'.format(len(self.archivos_cam1),len(self.archivos_cam2),len(self.archivos_cam3)))
        self.linea_de_tiempo.max = len(self.archivos_cam1)-1
        self.linea_de_tiempo.min = 0

    def actualizar_indices(self):
        """Actualiza la lista de los indices de las imagenes que tienen marca
        """

        ##global indices_marcas
        
        self.indices_marcas=[]
        for archivo in self.archivos_cam3:
            if archivo.endswith('MARCA.jpg') and (self.archivos_cam3.index(archivo) not in self.indices_marcas):
                self.indices_marcas.append(self.archivos_cam3.index(archivo))
        for archivo in self.archivos_cam2:
            if archivo.endswith('MARCA.jpg')and (self.archivos_cam2.index(archivo) not in self.indices_marcas):
                self.indices_marcas.append(self.archivos_cam2.index(archivo))
        for archivo in self.archivos_cam1:
            if archivo.endswith('MARCA.jpg') and (self.archivos_cam1.index(archivo) not in self.indices_marcas):
                self.indices_marcas.append(self.archivos_cam1.index(archivo))
        self.indices_marcas.sort()
        if DEBUG:
            Logger.info( 'REVISADOR: Hay {} archivos marcados: '.format(len(self.indices_marcas)))

        

    def leer_archivos(self):
        """Crea listas ordenadas de los archivos de cada camara, 
        archivos_camx       con los nombres de los archivos
        self.indices_marcas     con los indices que tienen las imagenes marcadas en la primer lista
        """
        Logger.info( 'REVISADOR: reviso carpeta: {}'.format(CARPETA_SESION_FOTOS))
        global DEBUG

        self.archivos_cam1 = os.listdir(CARPETA_SESION_FOTOS)
        self.archivos_cam2 = os.listdir(CARPETA_SESION_FOTOS)
        self.archivos_cam3 = os.listdir(CARPETA_SESION_FOTOS)
        
        if self.DEBUG:
            copia = copy.deepcopy(self.archivos_cam1)
            for archivo in copia:
                if (not '__c1__' in archivo) or (not archivo.lower().endswith('jpg')):
                    self.archivos_cam1.remove(archivo)
            self.archivos_cam1.sort()
            
            copia = copy.deepcopy(self.archivos_cam2)
            for archivo in copia:
                if (not '__c2__' in archivo) or (not archivo.lower().endswith('jpg')):
                    self.archivos_cam2.remove(archivo)
            self.archivos_cam2.sort()
            
            copia = copy.deepcopy(self.archivos_cam3)
            for archivo in copia:
                if (not '__c3__'  in archivo) or (not archivo.lower().endswith('jpg')):
                    self.archivos_cam3.remove(archivo)
            self.archivos_cam3.sort()
            
            del(copia)
        self.rellenar_lista()
        self.actualizar_indices()
        self.copiar_fotos_para_gui(0)
        #print archivos_cam1
        if DEBUG:
            Logger.info( 'REVISADOR: leer_archivos: Lista cam1: {}'.format(self.archivos_cam1))
            Logger.info( 'REVISADOR: leer_archivos: Lista cam2: {}'.format(self.archivos_cam2))
            Logger.info( 'REVISADOR: leer_archivos: Lista cam3: {}'.format(self.archivos_cam3))
            Logger.info( 'REVISADOR: leer_archivos: Las listas tienen {},{},{} archivos'.format(len(self.archivos_cam1),len(self.archivos_cam2),len(self.archivos_cam3)))
            Logger.info( 'REVISADOR: leer_archivos: con {} archivos marcados'.format(self.indices_marcas))
        self.linea_de_tiempo.value = 0


#######---------vengo hasta aca por ahora
    def copiar_fotos_para_gui(self,indice):
        if len(self.archivos_cam1) == 0:
            self.img1.source = IMG_DEFAULT
            self.img2.source = IMG_DEFAULT
            self.img3.source = IMG_DEFAULT
        else:
            if indice > len(self.archivos_cam1):
                indice = 0
            if not self.archivos_cam1[indice].endswith('FALTA'):
                #shutil.copy(CARPETA_SESION_FOTOS+self.archivos_cam1[indice],'imagenCamara1.jpg')
                self.img1.source = CARPETA_SESION_FOTOS+self.archivos_cam1[indice]
            else:
                #shutil.copy(IMG_DEFAULT,'imagenCamara1.jpg')
                self.img1.source = IMG_DEFAULT
            if not self.archivos_cam2[indice].endswith('FALTA'):
                #shutil.copy(CARPETA_SESION_FOTOS+self.archivos_cam2[indice],'imagenCamara2.jpg')
                self.img2.source = CARPETA_SESION_FOTOS+self.archivos_cam2[indice]
            else:
               # shutil.copy(IMG_DEFAULT,'imagenCamara2.jpg')
                self.img2.source = IMG_DEFAULT
            if not self.archivos_cam3[indice].endswith('FALTA'):
                self.img3.source = CARPETA_SESION_FOTOS+self.archivos_cam3[indice]
              #  shutil.copy(CARPETA_SESION_FOTOS+self.archivos_cam1[indice],'imagenCamara3.jpg')
            else:
                shutil.copy(IMG_DEFAULT,'imagenCamara3.jpg')
                self.img3.source = IMG_DEFAULT
        try:
            self.img1_fullscreen.source = self.img1.source
        except:
            pass
        try:
            self.img2_fullscreen.source = self.img2.source
        except:
            pass
        try:
            self.img3_fullscreen.source = self.img3.source
        except:
            pass
        self.linea_de_tiempo.value = indice

    def saltar_a_valor(self,*largs):
        self.indice = int(self.linea_de_tiempo.value)
        self.copiar_fotos_para_gui(self.indice)
        print 'nuevo indice', self.indice
        
        
    def siguiente(self,*largs):
        
        print 'avanzo con indice ',self.indice
        if self.indice >= (len(self.archivos_cam1) -1):
            self.indice = 0
        else:
            self.indice = self.indice + 1
        self.copiar_fotos_para_gui(self.indice)
        print 'nuevo indice', self.indice

    def anterior(self):
        print 'retrocedo con indice ',self.indice
        if self.indice == 0 :
            self.indice = (len(self.archivos_cam1) -1)
        else:
            self.indice = self.indice - 1
        self.copiar_fotos_para_gui(self.indice)
        print 'nuevo indice', self.indice

    def marca_siguiente(self):
        print 'indice actual:',self.indice
        print 'indice marcas:',self.indices_marcas
        if len(self.indices_marcas) == 0 :
            print 'no hay marcas, no hago nada'
            return
        for indice_marca in self.indices_marcas:
            if indice_marca > self.indice:
                self.indice = indice_marca
                print 'nuevo indice', self.indice
                self.copiar_fotos_para_gui(self.indice)
                return
        self.indice = self.indices_marcas[0]
        self.copiar_fotos_para_gui(self.indice)
        print 'nuevo indice', self.indice
        
    def marca_anterior(self):
        print 'indice actual:',self.indice
        print 'indice marcas:',self.indices_marcas
        if len(self.indices_marcas) == 0 :
            return
        for indice_marca in sorted(self.indices_marcas,reverse=True):
            if indice_marca < self.indice:
                self.indice = indice_marca
                print 'nuevo indice', self.indice
                self.copiar_fotos_para_gui(self.indice)
                return
        self.indice = self.indices_marcas[-1]
        self.copiar_fotos_para_gui(self.indice)
        print 'nuevo indice', self.indice

    def marcar_imagen(self,ruta, archivo_original,ruta_destino):
        """
        Crea una copia de la imagen, agregando MARCA al final del nombre del
        archivo, marca y comenta, y devuelve el nombre del archivo marcado, guarda la original
        en la carpetas marcadas-originales
        """
        print archivo_original
        nombre_nuevo = os.path.split(archivo_original)[-1].rstrip('.jpg')+'MARCA.jpg'
        ###creo la copia de las imagenes marcadas
        lineas = textwrap.wrap(self.comentario.text, width=50)
        img = PILImage.open(ruta+archivo_original,'r')
        draw = PILImageDraw.Draw(img)
        #La marca
        font = PILImageFont.truetype('UbuntuMono-B.ttf',200)
        draw.text((800, 80),"*",(255,0,0),font=font)
        #El comentario
        font = PILImageFont.truetype('UbuntuMono-B.ttf',45) 
        i=0
        for linea in lineas:
            draw.text((2, 200+i*50),linea,(255,0,0),font=font)
            i+= 1
        img.save(ruta_destino+nombre_nuevo,quality=100)
        print CARPETA_SESION_FOTOS,self.archivos_cam1[self.indice]
        #mover original a carpeta marcados
        if not os.path.exists(CARPETA_SESION_FOTOS+'MARCADAS-ORIGINALES'):
                makedirs(CARPETA_SESION_FOTOS+'MARCADAS-ORIGINALES')
        shutil.move(ruta+archivo_original,CARPETA_SESION_FOTOS+'MARCADAS-ORIGINALES')
        return nombre_nuevo
    
    def pre_marcar(self):
        print 'entro a premarcar con indice:',self.indice
        print 'en una lista con ',len(self.archivos_cam1),' elementos'
        print self.archivos_cam1[self.indice], self.archivos_cam1[self.indice].endswith('FALTA')
        if not (self.archivos_cam1[self.indice].endswith('FALTA') or self.archivos_cam1[self.indice].endswith('MARCA.jpg') ):
            self.archivos_cam1.insert(self.indice,self.marcar_imagen(CARPETA_SESION_FOTOS,self.archivos_cam1[self.indice],CARPETA_SESION_FOTOS))
            self.archivos_cam1.pop(self.indice+1)
        print self.archivos_cam2[self.indice], self.archivos_cam2[self.indice].endswith('FALTA')
        if not (self.archivos_cam2[self.indice].endswith('FALTA') or  self.archivos_cam2[self.indice].endswith('MARCA.jpg')):
            self.archivos_cam2.insert(self.indice,self.marcar_imagen(CARPETA_SESION_FOTOS,self.archivos_cam2[self.indice],CARPETA_SESION_FOTOS))
            self.archivos_cam2.pop(self.indice+1)
        print self.archivos_cam3[self.indice], self.archivos_cam3[self.indice].endswith('FALTA')
        if not (self.archivos_cam3[self.indice].endswith('FALTA') or  self.archivos_cam3[self.indice].endswith('MARCA.jpg')):
            self.archivos_cam3.insert(self.indice,self.marcar_imagen(CARPETA_SESION_FOTOS,self.archivos_cam3[self.indice],CARPETA_SESION_FOTOS))
            self.archivos_cam3.pop(self.indice+1)
        self.copiar_fotos_para_gui(self.indice)
        self.comentario.text = ''
        self.rellenar_lista()
        self.actualizar_indices()
        #self.siguiente()

       
    def adherir_comentario(self):
        print 'voy a adherir comentario'
        ####aca esta la papota del comentaroi
        #with open(COMENTARIO,'r') as texto:
            #texto_crudo = texto.read()
        #print texto_crudo
        lineas = textwrap.wrap(self.comentario.text, width=50)
        if not self.archivos_cam1[self.indice].endswith('FALTA'):
            img = PILImage.open(CARPETA_SESION_FOTOS+self.archivos_cam1[self.indice],'r')
            draw = PILImageDraw.Draw(img)
            font = PILImageFont.truetype('UbuntuMono-B.ttf',45)
          # draw.text((x, y),"Sample Text",(r,g,b))
            i=0
            for linea in lineas:
                draw.text((2, 200+i*50),linea,(255,0,0),font=font)
                i+= 1
                if not self.archivos_cam1[self.indice].endswith('MARCA.jpg'):
                    img.save(CARPETA_TEMPORAL+self.archivos_cam1[self.indice],quality=100)
                    self.archivos_cam1.insert(self.indice,self.marcar_imagen(CARPETA_TEMPORAL,self.archivos_cam1[self.indice],CARPETA_SESION_FOTOS))
                else:
                    img.save(CARPETA_SESION_FOTOS+self.archivos_cam1[self.indice],quality=100)
        
        if not self.archivos_cam2[self.indice].endswith('FALTA'):
            img = PILImage.open(CARPETA_SESION_FOTOS+self.archivos_cam2[self.indice],'r')
            draw = PILImageDraw.Draw(img)
            font = PILImageFont.truetype('UbuntuMono-B.ttf',45)
          # draw.text((x, y),"Sample Text",(r,g,b))
            i=0
            for linea in lineas:
                draw.text((2, 200+i*50),linea,(255,0,0),font=font)
                i+= 1
                if not self.archivos_cam2[self.indice].endswith('MARCA.jpg'):
                    img.save(CARPETA_TEMPORAL+self.archivos_cam2[self.indice],quality=100)
                    self.archivos_cam2.insert(self.indice,self.marcar_imagen(CARPETA_TEMPORAL,self.archivos_cam2[self.indice],CARPETA_SESION_FOTOS))
                else:
                    img.save(CARPETA_SESION_FOTOS+self.archivos_cam2[self.indice],quality=100)   
        
        if not self.archivos_cam3[self.indice].endswith('FALTA'):
            img = PILImage.open(CARPETA_SESION_FOTOS+self.archivos_cam3[self.indice],'r')
            draw = PILImageDraw.Draw(img)
            font = PILImageFont.truetype('UbuntuMono-B.ttf',45)
          # draw.text((x, y),"Sample Text",(r,g,b))
            i=0
            for linea in lineas:
                draw.text((2, 200+i*50),linea,(255,0,0),font=font)
                i+= 1
                if not self.archivos_cam3[self.indice].endswith('MARCA.jpg'):
                    img.save(CARPETA_TEMPORAL+self.archivos_cam3[self.indice],quality=100)
                    self.archivos_cam3.insert(self.indice,self.marcar_imagen(CARPETA_TEMPORAL,self.archivos_cam3[self.indice],CARPETA_SESION_FOTOS))
                else:
                    img.save(CARPETA_SESION_FOTOS+self.archivos_cam3[self.indice],quality=100)
        self.comentario.text = ''
        self.rellenar_lista()
        self.actualizar_indices()
        self.copiar_fotos_para_gui(self.indice)
        #self.siguiente()
        #print 'nuevo indice', indice
        


def limpiar_lista(sesion):
    print 'limpio sesion: ',sesion
    arch = os.listdir(sesion)

    c1=[];c2=[];c3=[];
    for ar in arch:
        if '__c1__' in ar: c1.append(ar)
        if '__c2__' in ar: c2.append(ar)
        if '__c3__' in ar: c3.append(ar)
    c1.sort()
    c2.sort()
    c3.sort()
    cams = [c1,c2,c3]
    QUANTO = 10
    quantos = []
    for i in range(len(c1)-1):
        if int(c1[i+1][:6]) - int(c1[i][:6]) != 0:
            quantos.append (abs( int(c1[i+1][:6]) - int(c1[i][:6]) ))
    
    QUANTO = min(quantos)
    print 'QUANTO :', QUANTO
    
    
    for cam in cams:
        for i in range(1,len(cam)-1):
            if cam[i+1][:6] == cam[i][:6] : #si esta repetido
                if int(cam[i][:6])-int(cam[i-1][:6]) >= QUANTO :  #si el anterior no es el contiguo
                    nombre_viejo = cam[i]
                    cam[i] =cam[i].replace(cam[i][:7],'{0:06}m'.format(int(cam[i][:6])-QUANTO)) # lo muevo
                    shutil.move(sesion+nombre_viejo,sesion+cam[i])
                else:  
                    os.remove(sesion+cam[i])
    for cam in cams:
        print cam[0],cam[0][6],cam[1],cam[1][:6]
        if cam[0][:6] == cam[1][:6]:
            print sesion+cam[0]
            os.remove(sesion+cam[0])


####-------Fin interfaz grafica


#### -------------------------------------------------PROGRAMA PRINCIPAL
class revisadorApp(App):
    #Configuracion de operar
    icon = ICONO
    title = 'REFEOCA VIEWER'
    path = ''
    selection = ''
    def build(self):
        #valores por defecto
    #    shutil.copy('img_default/default.jpg','temporales/camara1c.jpg')
    #    shutil.copy('img_default/default.jpg','temporales/camara2c.jpg')
    #    shutil.copy('img_default/default.jpg','temporales/camara3c.jpg')
    
        #CREO TODAS LAS PANTALLAS
        self.pInicio = Pantalla_Inicio(name='inicio')
        self.pRevisar = Pantalla_Revisar(name='revisar')
        self.screenAdmin = ScreenManager()#transition=NoTransition())
        self.screenAdmin.add_widget(self.pInicio)
        self.screenAdmin.add_widget(self.pRevisar)
        self.screenAdmin.current = 'inicio'
        #OPERAR###
        print 'fin build'
        return self.screenAdmin
    

        
##------------------------------------------------------ARCHIVO INFO.TXT
        #with open(self.sesion+'info.txt','w') as info:
            #info.write('OPERADOR: '+ self.pConfOperar.operador.text + '\n')
            #info.write('FECHA: '+ datetime.datetime.fromtimestamp(ts).strftime('%d-%m-%Y_%Hh%Mm%S').rstrip('0') +'\n') 
            #info.write('RUTA: '+ self.pConfOperar.ruta.text + '\n')
            #info.write('SENTIDO: '+ self.pConfOperar.sentido.text+ '\n')
            #info.write('DISTANCIA INICIAL: '+ self.pConfOperar.progreso.text+ '\n' )


#####-------------------------------------------------------------------
#####----------------------------------------------------------FUNCIONES

    #------esto es del revisador
    def dismiss_popup(self):
        self._popup.dismiss()
        
    def cargar(self):
        self.screenAdmin.current = 'revisar'
        print 'cambio a revisar'
        
        

    def volver(self):
        self.screenAdmin.current = 'inicio'
        print 'cambio a inicio'
        print 'cambio a inicio'
    
    def salir(self):
        exit()


revisadorApp().run()
