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
count = 0

class MinsaSpider(scrapy.Spider):
    name = "minsaSpider3"

    def __init__(self,  idp=None, ide=None, *args, **kwargs):
        super(MinsaSpider, self).__init__(*args, **kwargs)
        self.idp = idp
        self.ide = ide
        self.apiurl = "http://innovations.pe/arturo/api-meds/medicamentos/create/"
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

        with open('minsadata/db.csv', newline='') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.idps = data['ID_P'].dropna().values.astype(int).tolist()
            self.ides = data['ID_E'].dropna().values.astype(int).tolist()
            print(self.idps)
            print(self.ides)

    def start_requests(self):

        start_url = 'http://observatorio.digemid.minsa.gob.pe/Precios/ProcesoL/Consulta/FichaProducto.aspx'

        for producto in self.idps:
            for establecimiento in self.ides:
                print(producto, establecimiento)
                yield scrapy.Request(url=start_url+'?idp='+str(producto)+'&ide='+str(establecimiento).zfill(7), meta={'idp': producto, 'ide': establecimiento})

    def parse(self, response):
        datamed = {}
        datamed = {"id_p": response.meta['idp'], "id_e": response.meta['ide']}
        for span in response.xpath('//span'):
            k = Selector(text=span.extract()).xpath('//span/@id').extract_first()
            if k in self.keys:
                v = Selector(text=span.extract()).xpath('//span/text()').extract_first()
                if v is None:
                    datamed[self.keys[k]] = "null"
                else:
                    datamed[self.keys[k]] = Selector(text=span.extract()).xpath('//span/text()').extract_first()
        if(datamed["monto_empaque"] != "No Determinado"):
            # notifier
            global count
            count += 1
            self.log('**********************************************************************************************************************************************')
            self.log('*                                                                                                                                            *')
            self.log('*                                                        Valid med: {0}                                                                      *'.format(count))
            self.log('*                                                                                                                                            *')
            self.log('**********************************************************************************************************************************************')


            # Location to coordinates

            g = geocoder.google(datamed["direccion"], key='AIzaSyDhY9yQRQnq1lKBfxVMK6_oe7fSh1KmnT4')
            coordinates = g.latlng
            datamed["monto_empaque"] = float(datamed["monto_empaque"])
            datamed["latitud"] = coordinates[0]
            datamed["longitud"] = coordinates[1]
            r = requests.post(self.apiurl, data=json.dumps(datamed), headers=self.headersapi)
            print("Status: ", r.text)
            print(json.dumps(datamed))


        else:
            self.log('EMPTY  idp={0} ide={1}'.format(str(response.meta['idp']), str(response.meta['ide']).zfill(7)))
