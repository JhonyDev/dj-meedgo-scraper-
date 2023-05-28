import scrapy
import json
import pandas as pd

class HealthPlusSpider(scrapy.Spider):
    name = "health_plus"
    current_page = 1
    headers = {
        
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
    def __init__(self,input,*args,**kwargs):
        self.keyword = input
        super().__init__(*args, **kwargs)
        
    def start_requests(self):
        
        self.url = f"https://search.prod.fkhealthplus.com/search_list/?q={self.keyword}&page=1&size=200"
        yield scrapy.Request(url=self.url,headers=self.headers,meta={"current_page":self.current_page},dont_filter=True,callback=self.parse)
        
    def parse(self, response):
        json_data =json.loads(response.text)
        
        ww = pd.DataFrame(json_data["products"],columns=json_data["keys"])
        ww.fillna("",inplace=True)
        ww.loc[(ww["ProductImage"]!=""),["ProductImage"]] = "https://res.fkhealthplus.com/incom/images/product/"+ ww["ProductImage"] 
        
        json_data2 = json.loads(ww.to_json(orient='records'))
        
        for ww in json_data2:
            try:
                display =ww["DisplayName"]
                display_name =display.casefold().replace(" ","-").replace("(","").replace(")","").replace(".","").replace("'","")
                
            except:
                display = None
                
            try:
                mfg =ww["MfgGroup"]
                mfg_group =mfg.casefold().replace(" ","-").replace("(","").replace(")","").replace(".","").replace("'","").replace("-&","")
              
            except:
                mfg_group = None
                
            try :
                encode = ww["EncodeProdId"]
                
            except:
                encode = None
            try :
                product_url = f"https://healthplus.flipkart.com/{display_name}-{mfg_group}/p/{encode}"
            except:
                product_url = None
            
          
        for ii in json_data2:
            ii["product_url"] = product_url
            yield ii 
           
            
        max_page  = 50 
        current_page= response.meta.get("current_page")
        
        if response.meta.get("current_page") < max_page:
            response.meta["current_page"] = response.meta.get("current_page") + 1
           
            url =f'https://search.prod.fkhealthplus.com/search_list/?q={self.keyword}&page={response.meta["current_page"]}&size=200'
        
            if len(json_data["products"]) == 0:
                pass
            else:
                yield scrapy.Request(url=url,headers=self.headers,meta={"current_page":response.meta["current_page"]},dont_filter=True
                                     ,callback=self.parse)
            
        
        
            
