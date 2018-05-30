import scrapy
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging


import json
import pandas as pd


class MinsaSpider(scrapy.Spider):
    name = "minsaSpider"

    def __init__(self,  idp=None, ide=None, *args, **kwargs):
        super(MinsaSpider, self).__init__(*args, **kwargs)
        self.idp = idp
        self.ide = ide
        self.keys = {
                        "Medicamento": "medicamento",
                        "Presentación" : "presentacion",
                        "MontoEmpaque" : "monto_empaque",
                        "CondicionV" : "condicion_v",
                        "Estab" : "estab",
                        "Direccion" : "direccion",
                        "Ubicacion" : "ubicacion",
                        "Telefono" : "telefono",
                        "Horario" : "horario"
                    }

        with open('minsadata/medicamentos.csv', newline='') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.idps = data['Cod_Prod'].values.tolist()

        with open('minsadata/establecimientos.csv') as file:
            data = pd.read_csv(file, encoding='Latin-1')
            self.ides = data['CODIGO DE ESTABLECIMIENTO'].values.tolist()

    def start_requests(self):

        start_url = 'http://observatorio.digemid.minsa.gob.pe/Precios/ProcesoL/Consulta/FichaProducto.aspx'

        for producto in range(1):
            self.idp = str(self.idps[producto])
            for establecimiento in range(10000, len(self.ides)):
                self.ide = str(self.ides[establecimiento])
                yield scrapy.Request(url=start_url+'?idp='+self.idp+'&ide='+self.ide.zfill(7), callback=self.parse)

    def parse(self, response):
        data = {}
        filename = 'data/med-{0}-{1}.json'.format(self.idp,self.ide.zfill(7))
        data = {'idp': self.idp, 'ide': self.ide.zfill(7)}
        for span in response.xpath('//span'):
            key = Selector(text=span.extract()).xpath('//span/@id').extract_first()
            if key in self.keys:
                data[self.keys[key]] = Selector(text=span.extract()).xpath('//span/text()').extract_first()
        if(data["monto_empaque"] != "No Determinado"):
            with open(filename, 'w') as f:
                json.dump(data, f)
            self.log('Saved file %s' % filename)

        else:
            self.log('Empty file idp={0} ide={1}'.format(self.idp, self.ide.zfill(7)))
