import scrapy
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

import os

import geocoder
import requests
import json
import pandas as pd


class MinsaSpider(scrapy.Spider):
    name = "minsaSpider2"

    def __init__(self,  idp=None, ide=None, *args, **kwargs):
        super(MinsaSpider, self).__init__(*args, **kwargs)
        self.idp = idp
        self.ide = ide
        self.apiurl = "http://innovations.pe/arturo/api-meds/medicamento/create.php"
        self.headersapi = {"Content-Type": "application/x-www-form-urlencoded"}
        self.keys = {
                        "Medicamento": "medicamento",
                        "Presentacion" : "presentacion",
                        "MontoEmpaque" : "monto_empaque",
                        "CondicionV" : "condicion_v",
                        "Estab" : "estab",
                        "Direccion" : "direccion",
                        "Ubicacion" : "ubicacion",
                        "Telefono" : "telefono",
                        "Horario" : "horario"
                    }
        """
        with open('minsadata/medicamentos.csv', newline='') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.idps = data['Cod_Prod'].values.tolist()

        with open('minsadata/establecimientos.csv') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.ides = data['CODIGO DE ESTABLECIMIENTO'].values.tolist()
        """
        with open('minsadata/db.csv', newline='') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.idps = data['ID_P'].values.tolist()
            self.ides = data['ID_E'].values.tolist()

    def start_requests(self):

        start_url = 'http://observatorio.digemid.minsa.gob.pe/Precios/ProcesoL/Consulta/FichaProducto.aspx'

        for producto in range(1):
            self.idp = str(int(self.idps[producto]))
            for establecimiento in range(10000, len(self.ides)):
                self.ide = str(int(self.ides[establecimiento]))
                yield scrapy.Request(url=start_url+'?idp='+self.idp+'&ide='+self.ide.zfill(7), callback=self.parse)

    def parse(self, response):
        datamed = {}
        filename = 'datamed/med-{0}-{1}.json'.format(self.idp,self.ide.zfill(7))
        datamed = {"id_p": int(self.idp), "id_e": int(self.ide)}
        for span in response.xpath('//span'):
            k= Selector(text=span.extract()).xpath('//span/@id').extract_first()
            if k in self.keys:
                v = Selector(text=span.extract()).xpath('//span/text()').extract_first()
                if v is None:
                    datamed[self.keys[k]] = "null"
                else:
                    datamed[self.keys[k]] = Selector(text=span.extract()).xpath('//span/text()').extract_first()
        if(datamed["monto_empaque"] != "No Determinado"):
            # Location to coordinates
            g = geocoder.google(datamed["direccion"], key='')
            coordinates = g.latlng
            datamed["latitud"] = str(coordinates[0])
            datamed["longitud"] = str(coordinates[1])
            """
            with open(filename, 'w') as f:
                json.dump(datamed, f)
            self.log('Saved file %s' % filename)
            """
            """
            r = requests.post(self.apiurl, data=json.dumps(datamed), headers=self.headersapi)
            print("AAAAAAAAAAAAAAAAAAA",r.text)
            print("TAJJJJJ" ,json.dumps(datamed))
            """
        else:
            self.log('EMPTY  idp={0} ide={1}'.format(self.idp, self.ide.zfill(7)))
