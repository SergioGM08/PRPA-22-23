import requests
import re
import os, zipfile
import sys

urlMain = 'https://opendata.emtmadrid.es'
urlConcreto = '/Datos-estaticos/Datos-generales-(1)'

def descargaY(y):
    links = re.compile(r'<\s*a [^>]*href="([^"]+)').findall(requests.get(f'{urlMain}{urlConcreto}').text)
    descargas = [link for link in links if (link.startswith("/getattachment/") and f'{y}' in link and ('movement' in link or 'Usage' in link )) or f'trips_{y[2:4]}' in link]
    c = 0
    for url in descargas:
        print(url)
        r = requests.get(f'{urlMain}{url}', allow_redirects=True)
        open(f'{c}.zip', 'wb').write(r.content)
        c+=1

    dir_name = os.getcwd()
    extension = ".zip"
    folder = f'DatosBICIMAD/BiciMAD_{y}'

    for item in os.listdir(dir_name): 
        if item.endswith(extension): 
            file_name = os.path.abspath(item) 
            zip_ref = zipfile.ZipFile(file_name) 
            zip_ref.extractall(f'{dir_name}/{folder}') 
            zip_ref.close() 
            os.remove(file_name) 

if __name__=="__main__":
    if len(sys.argv)>1:
        descargaY(sys.argv[1])
    else:
        print('Se necesita argumento año')