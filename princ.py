import scrapy
import re

class PrincSpider(scrapy.Spider):
    name = 'princ'

    # the starting url
    start_urls = ['https://www.fara.gov/quick-search.html']

    # this function will parse the first page and get to the page with the needed information
    def parse(self, response):

        # find the link to follow
        next_page = response.xpath('//a[font[contains(text(),"Active Foreign Principals")]]/@href').get() 

        next_page = response.urljoin(next_page)

        # go to the page with the information
        return scrapy.Request(next_page, callback=self.parse2) 
        
    # parsing the second page
    def parse2(self, response):

        # find the number of countries, so that it can be used to know how many tables to parse
        countries = response.xpath('//th[contains(@id,"B77386298861628701_")]/text()').getall()

        # parse the table parts
        for x in range(len(countries)):

            i = x + 1

            # all the needed table cells have a header: 
            # description B77386298861628701_x
            # where 'description' is the column name
            # 'x' is the country number
            # this is used in the xpaths 
            country = countries[x]
            f_url = response.xpath('//td[contains(@headers,"LINK B77386298861628701_' + str(i) + '")]/a/@href').getall()
            principals = response.xpath('//td[contains(@headers,"FP_NAME B77386298861628701_' + str(i) + '")]/text()').getall()  
            p_dates = response.xpath('//td[contains(@headers,"FP_REG_DATE B77386298861628701_' + str(i) + '")]/text()').getall()
            registrants = response.xpath('//td[contains(@headers,"REGISTRANT_NAME B77386298861628701_' + str(i) + '")]/text()').getall()
            r_codes = response.xpath('//td[contains(@headers,"REG_NUMBER B77386298861628701_' + str(i) + '")]/text()').getall()
            
            adresses = response.xpath('//td[contains(@headers,"ADDRESS_1 B77386298861628701_' + str(i) + '")]/text()').getall()

            # the  last row of all adresses have the &nbsp; symbol 
            # which after scraping becomes \u00a0
            # this is used to split the adresses accordingly
            
            # add "to_split" to the strings that contain \u00a0
            adresses[:] = [item + "to_split" if '\u00a0' in item else item for item in adresses]

            # join all adresses
            adresses = ','.join(adresses)

            # replace \u00a0 with simple space
            adresses = re.sub("\\u00a0\\u00a0", " ", adresses)

            # split the adresses at the specified string
            adresses = re.split(",* *to_split,* *", adresses)            

            # the number of principals per country is used to know the number of rows a country table has
            for y in range(len(principals)):

                the_url = response.urljoin(f_url[y])

                # replace empty adresses with None
                if (not adresses[y]): adresses[y] = None
                j = y + 1

                # tried to get one cell at a time, didn't really manage
                states = response.xpath('*//td[contains(@headers,"STATE B77386298861628701_' + str(i) + '")][' + str(j) + ']/text()').get()
                if (not states): states = None

                yield {
                        "url" : the_url,
                        "country" : country[31:],
                        "state" : states,
                        "reg_num" : r_codes[y],
                        "address": adresses[y],
                        "foreign_principal" : principals[y], 
                        "date" : p_dates[y],
                        "registrant" : registrants[y]
                        
                    }

    