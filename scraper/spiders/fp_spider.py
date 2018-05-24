import scrapy
from scrapy.selector import Selector
import json

class MinsaSpider(scrapy.Spider):
    name = "minsaSpider"
    
    def __init__(self, n=1,  idp='8766', ide='0095801', *args, **kwargs):
        super(MinsaSpider, self).__init__(*args, **kwargs)
        self.idp = idp
        self.ide = ide
        self.n = int(n)
    def start_requests(self):
        """
        urls = [
            'http://observatorio.digemid.minsa.gob.pe/Precios/ProcesoL/Consulta/FichaProducto.aspx?idp=8766&ide=0095801'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        """
        start_url = 'http://observatorio.digemid.minsa.gob.pe/Precios/ProcesoL/Consulta/FichaProducto.aspx'
        for i in range(self.n):
            yield scrapy.Request(url=start_url+'?idp='+self.idp+'&ide='+self.ide, callback=self.parse)

    def parse(self, response):
        data = {}        
        filename = 'med-{0}-{1}.json'.format(self.idp,self.ide) 
        with open(filename, 'w') as f:
            for span in response.xpath('//span'):
                data[Selector(text=span.extract()).xpath('//span/@id').extract_first()] = Selector(text=span.extract()).xpath('//span/text()').extract_first()
            json.dump(data, f)
        self.log('Saved file %s' % filename)
