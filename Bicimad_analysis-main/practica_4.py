from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StringType, IntegerType, TimestampType, DoubleType
from pyspark.sql import functions as F
import matplotlib.pyplot as plt
import gdown
from descargarDatosYear import descargaY
import os
import sys

path = 'DatosBICIMAD'
estaciones = 'Estaciones.json'
pathYear = lambda y: path+f'/BiciMAD_{y}'

#Clase para centralizar las funciones sobre el dataFrame
class Datos():
    def __init__(self, df, s):
        self.df = df
        self.s = s 

#Muestra la tabla y el gráfico de barras correspondiente a n2 y su cantidad total. Mostrando n1 en el mensaje por pantalla
# y es para indicar el año que se está mostrando en el gráfico.
    def imprimeCantidad(self,n1,n2, y):
        print(f'{n1}, en todo {y}')
        dE = self.cantidadEngrupo(n2)
        dE.muestra()
        dE.grafico(n2, 'count', titulo = f'en {self.s} en {y}')

#para mostrar por pantalla la tabla del dataFrame
#Si noEntero es True entonces solo se muestran los 20 primero en vez de la tabla completa
#Si es False se muestra completa
    def muestra(self, noEntero = True):
        self.df.show(10 if noEntero else self.df.count(), False)
 
#Muestra por pantalla la media, el mínimo y el máximo de los datos   
    def describe(self):
        self.df[["Duracion","tipo_Usuario", "rango_Edad", "Hora"]].describe().show()
  
#devuelve un dataFrame con una columna nombre con los elementos de esa columna
#y otra columna count con el total de estos en el dataframe     
    def cantidadEngrupo(self, nombre):
        return Datos(self.df.groupBy(nombre).count(), self.s)  

    #Muestra los distintos grupos de edad con las medias de la duración y la hora
    def verMediasPorEdad(self):
        m = Datos(self.df.groupBy("rango_Edad").agg({'Duracion':'avg', 'Hora':'avg'}).sort('rango_Edad'), self.s)
        m.muestra()
        m.grafico('rango_Edad', 'avg(Duracion)', barras=False, titulo = 'Duración de los viajes por grupo de edad ')
        
#devuelve un dataFrame con los elementos de la columna nombre con valor v  
    def filtraPor(self, nombre, v):
        return Datos(self.df.filter(F.col(nombre)==v), self.s+f' con {nombre} = {v}')

 #devuelve un dataframe con los viajes desde o hasta Estacion
    def filtraEstaciones(self, Estacion):
        dfCU = self.df.filter(F.col("Estacion_Salida" ).contains(Estacion) 
                       | F.col("Estacion_Llegada").contains(Estacion))
        s = Datos(dfCU, Estacion)
        return s

#devuelve un gráfico hecho con los datos de nombreX en el eje X y los 
# de nombreY en el Y. 
#Si barras es True, el gráfico es de barras
    def grafico(self, nombreX, nombreY, barras=True, titulo = ''):
        x,y=[],[]
        for vx,vy in self.df.select(nombreX, nombreY).collect():
            y.append(vy)
            x.append(vx)
        if barras:
            plt.bar(x, y)
        else:
            plt.plot(x, y)

        plt.ylabel(nombreY)
        plt.xlabel(nombreX)
        plt.title(f'{nombreX} vs. {nombreY} {titulo}')
        plt.legend([nombreX], loc='upper left')

        plt.show()

#Extension de datos para la consulta inicial
class Consulta(Datos):    
    def __init__(self, nombres):
        self.spark = SparkSession.builder.getOrCreate()        
        schema = StructType()\
            .add("travel_time", DoubleType(), False)\
            .add("user_type", IntegerType(), False)\
            .add("idunplug_station", IntegerType(), False)\
            .add("idplug_station", IntegerType(), False)\
            .add("ageRange", IntegerType(), False)\
            .add("unplug_hourTime", TimestampType(), False)
        df = self.spark.read.json(nombres, schema=schema)

        #Pasamos el tiempo a minutos, para que sea más legible 
        df = df.filter(df["travel_time"]>0).withColumn("travel_time", F.round((F.col("travel_time")/60),2))
        #Cambiamos los nombre por comodidad
        df = df.withColumnRenamed("user_type", "tipo_Usuario").withColumnRenamed("ageRange", "rango_Edad").\
            withColumnRenamed("travel_time", "Duracion")

        #Dividimos el tiempo del viaje en dia y hora
        df = df.withColumn('Dia', F.to_date(df.unplug_hourTime))
        df = df.withColumn('Hora', F.hour(df.unplug_hourTime)).drop('unplug_hourTime')
        self.df = df
        self.s = 'todas las estaciones'

#Cambia idunplug_station e idplug_station por el nombre de la estación correspondiente
# bajo el nuevo nombre de "Estacion_Llegada" y "Estacion_Salida"        
    def formateaEstaciones(self):
        #Con los nombres de las estaciones, que se ve mejor :)
        df2 = self.spark.read.json(f'{path}/{estaciones}',  multiLine=True)
        df2 = df2.drop('dock_bikes','free_bases','activate','address','latitude','light','longitude','no_available','number','reservations_count','total_bases')
        df3 = (self.df.join(df2, self.df.idunplug_station ==  df2.id,"inner").withColumnRenamed("name","Estacion_Salida")).drop('id')
        df3 = (df3.join(df2,df3.idplug_station ==  df2.id,"inner").withColumnRenamed("name","Estacion_Llegada")).drop('id')
        df3 = df3.drop('idunplug_station','idplug_station')
        return Datos(df3, self.s)

#Para leer los datos de un año y producir los resultados indicados en el readme
def datos(nEst, y):
    pathY = pathYear(y)
    #Descargamos los datos si no están ya
    if not os.path.isdir(path) or not 'Estaciones.json' in os.listdir(path):
        print('Descargando Datos Estaciones, puede tardar')
        url = "https://drive.google.com/drive/folders/1dqnPVK-5qzsJJarUBwj-xcOIWjjUtpBz"
        gdown.download_folder(url, quiet=True, use_cookies=False)
    if not os.path.isdir(pathY):
        print('Descargando Datos Año, puede tardar')
        descargaY(y)

    #Hacemos la consulta para generar el dataframe del año
    consulta = Consulta([f'{pathY}/{item}' for item in os.listdir(pathY) if item.endswith('.json')])
    print(f'Viajes hechos en {y}')
    consulta.describe()

    dCU = consulta.formateaEstaciones().filtraEstaciones(nEst)

    print(f'Viajes hechos desde o hasta las estaciones de {nEst} en {y}')
    dCU.describe()
    
    dCU.muestra()

    consulta.imprimeCantidad('Viajes por grupo de Edad', 'rango_Edad', y)
    dCU.imprimeCantidad('Viajes por grupo de Edad', 'rango_Edad', y)

    consulta.spark.stop()

#Si se ejecuta sin argumentos da los datos de Sol en 2020
#Si tiene 1 argumento, los de la estación q se ha dado como argumento en 2020
#Si tiene 2 o más, da los datos de la estación q se ha dado en el primer argumento
#En los años de los sucesivos argumentos (del 2 en delante)
if __name__=="__main__":
    l = len(sys.argv)
    nEst = 'Sol' if l<2 else sys.argv[1]
    x = 2
    while l>x:
        y = sys.argv[x]
        if y in {'2017','2018','2019','2020','2021','2022','2023'}:
            datos(nEst, y)
        else:
            print(f'No hay datos para el año {y}')
        x+=1
    if l<2:
        datos(nEst, 2020)
