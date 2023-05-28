import scrapy
import json
import pandas as pd

class HealthPlusLinkSpider(scrapy.Spider):
    name = "health_plus_link"
    headers = {
        
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    
    def __init__(self,input, *args, **kwargs):
        self.url = input
        super().__init__(*args, **kwargs)

    def start_requests(self):
       
        yield scrapy.Request(url=self.url,method="GET",headers=self.headers,dont_filter=True,callback=self.parse)
    
    def parse(self, response):
        rbzid = response.text.split(';;window.rbzns={"bereshit":"1","seed":"')[-1].split('"')[0].replace("\\","")# without cookies request then we get rbzid values after get values using spilt
        cookies= {"rbzid":rbzid} # store there rbzid values
        yield scrapy.Request(url=self.url,method="GET",cookies=cookies,headers=self.headers,dont_filter= True,callback=self.parse_2)
    
    def parse_2(self, response):
        json_data = None
        name = None
        
        images = None
        description = None
        brand = None
        sku = None,
        price = None
        availability = None
        product_id = None
        exp_date = None
        mrp_price = None
        generic_id = None
        try:
            data = response.xpath("//script[@type='application/ld+json']/text()").get().replace("\r\n"," ").replace("\r\n\t"," ").replace("\xa0"," ").replace("\\","")
        except Exception as w:
            print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++",w)
            data = None
        
        
        
        if data :
            try:
                json_data = json.loads(data)
            except Exception as ww:
                json_data =None
        
            try :
                name =json_data["name"]
            except Exception as w :
                name =  None
        
            try :
                images = response.xpath("//div[@id='slider3']//img/@src").getall()
            except:
                images = None
                
            try :
                description = json_data["description"].strip()
            except:
                description = None
                
            try :
                brand = json_data["brand"]
            except:
                brand = None
                
            try :  
                sku = json_data["sku"]
            except:
                sku  = None
                
            try :
                price = json_data["offers"]["price"]
            except:
                try :
                    price = response.xpath("//big/text()").get().replace("\r\n ","").replace("Rs.","").strip()
                except:
                    price = None
                
            try :
                availability = json_data["offers"]["availability"]
            except:
                availability = None
                
            try :
                product_id =response.xpath("//span/@product_id").get()
            except:
                product_id = None
            
            try:
                exp_date = response.xpath("//div[@class='mainPriceSec']//h4/following::p/text()").get().split(":")[-1].strip()
            except:
                try :
                    exp_date = response.xpath("//p[@class='fontsize13'][not(@style)][not(@align)]/text()").get().split(":")[-1].strip()
                except:
                    exp_date = None
               
                
            try:
                mrp_price =response.xpath("//div[@class='mainPriceSec']//h4/text()").get().replace("MRP*: Rs."," ")
            except:
                try :
                    mrp_price =response.xpath("//em/preceding::small[1]/font/text()").get().replace("MRP*: Rs."," ")
                except :
                    try:
                        mrp_price = response.xpath("//span[contains(text(),'MRP*:')]//text()[2]").get()
                    except:
                        mrp_price = None
                    
               
            try :
                generic_id =response.xpath("//span[@id='req_val']/@saltid").get()
            except:
                generic_id = None
        
        
            url = "https://catalog.prod.fkhealthplus.com/product/genericDetails/"
            try :
                payload = f"ci_csrf_token=&GenericId={generic_id}&GenericName={name.replace(' ','+')}&genericView=M&lang=e&ProductId={product_id}&pincode=&RouteId=1" 
            except:
                payload = None
            headers = {
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
            }
            
            yield scrapy.Request(url=url,headers=headers,
                                meta={"name":name,
                                    
                                        "description":description,
                                        "brand":brand,
                                        "generic_id":generic_id,
                                        "sku":sku,
                                        "images":images,
                                        "availability" :availability,
                                        "price":price,
                                        "product_id":product_id,
                                        "exp_date":exp_date,
                                        "mrp_price":mrp_price,
                                        },
                                        method="POST",body=payload,callback=self.parse_4)
        else:
            rbzid = response.text.split(';;window.rbzns={"bereshit":"1","seed":"')[-1].split('"')[0].replace("\\","")# without cookies request then we get rbzid values after get values using spilt
            cookies= {"rbzid":rbzid} # store there rbzid values
            yield scrapy.Request(url=response.url,method="GET",cookies=cookies,headers=self.headers,dont_filter= True,callback=self.parse_2)
            
    
    def parse_4(self, response):
        json_data_2 = json.loads(response.text) 
        
        generic_details =json_data_2["results"]
        url_2  =f"https://search.prod.fkhealthplus.com/similar_products?product_id={response.meta['product_id']}"
        yield scrapy.Request(url=url_2,method="GET",meta={"generic_details":generic_details,
                                                          "name":response.meta["name"],
                                       "description":response.meta["description"],
                                       "brand":response.meta["brand"],
                                      
                                       "sku":response.meta["sku"],
                                       "generic_id":response.meta["generic_id"],
                                       "images":response.meta["images"],
                                       "availability":response.meta["availability"],
                                       "price":response.meta["price"],
                                       "product_id":response.meta["product_id"],
                                       "exp_date":response.meta["exp_date"],
                                       "mrp_price":response.meta["mrp_price"],
                                      },headers=self.headers,dont_filter= True,callback=self.parse_5)
    
    def parse_5(self, response):
        try :
            json_data_3 =json.loads(response.text)
            
            ww = pd.DataFrame(json_data_3["products"],columns=json_data_3["keys"])
            www = json.loads(ww.to_json(orient='records'))
        except:
            www = []
 
        yield {
            "name":response.meta["name"],
            "description":response.meta["description"],
            "brand":response.meta["brand"],
            "sku":response.meta["sku"],
            "price":response.meta["price"],
            "product_id":response.meta["product_id"],
            "images":response.meta["images"],
            "availability":response.meta["availability"],
            "exp_date":response.meta["exp_date"],
            "mrp_price":response.meta["mrp_price"],
            "generic_details":response.meta["generic_details"],
            "substitutes_ for_tab":www,
            
        }
        

        
        
        
        
        
        