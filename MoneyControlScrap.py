from bs4 import BeautifulSoup
from urllib.request import *
import re

class UrlOpener( object ):
    def __init__(self, url):
        self.url = url

    def contents(self):
        return urlopen(self.url)


test_sufix ='computers-software'
moneyControlSite = UrlOpener( r'http://www.moneycontrol.com/stocks/sectors/'  )


soup = BeautifulSoup(moneyControlSite.contents(), "html.parser")

##scrapPattern = [
##  r'/stocks/sectors/.+\.html$'
##  r'/stockpricequote/.+\.html$' 
##]

def ReadCashFlow( url ):
    soup = BeautifulSoup( UrlOpener( url ).contents(), "html.parser")
    return soup.findAll(text='Closing Cash & Cash Equivalents')[0].findNext().get_text()

scrapPattern_0 = soup("a", {  'href':re.compile(r'/stocks/sectors/%s\.html$' % test_sufix) })
visited = {}


for sites in scrapPattern_0:
    print ( 'Listing all companies from %s Sector' % sites.get_text() )
    soup = BeautifulSoup( UrlOpener( sites['href'] ).contents(), "html.parser")
    
    scrapPattern_1 = soup("a", {  'href':re.compile(r'/stockpricequote/.+/.+') })

    count = 0

    for stocks in scrapPattern_1:
        soup = BeautifulSoup( UrlOpener( r'http://www.moneycontrol.com/%s' % stocks['href'] ).contents(), "html.parser")
        cashflowUrl = r'http://www.moneycontrol.com/%s' % ( soup.findAll(text='Cash Flow')[1].findPrevious()['href'] )
         
        

        if stocks.get_text() in visited:continue
        else: visited[ stocks.get_text() ] =''
        
        #scrapPattern_2 = soup("div", {'id':'findet_11' } )
        #scrapPattern_3 = soup("div", {'class':'FR gD_12' } ) #<div class="FR gD_12">453,365.91</div>
        #print ( scrapPattern_3[0].get_text() )
        if True: #scrapPattern_2 and scrapPattern_3 :
            count += 1
            Market_Cap = soup.findAll(text='MARKET CAP (Rs Cr)')[0].findNext().get_text()[0],
            Cash_Flow =  ReadCashFlow( cashflowUrl )
            Cash_to_Market_cap_ratio = 0 #100.0*float(Cash_Flow.replace(',', '' )/ float( Market_Cap.replace(',','') ) )
            result = {
            'Count': count,
            'Company':stocks.get_text(),
            'Market_Cap': Market_Cap ,
            'Total_Debt': soup.findAll(text='Total Debt')[0].findNext().get_text(), ## Total Debt
            'Total_Asset':soup.findAll(text='Total Assets')[1].findNext().get_text(), ## Total Asset
            'Cash_Flow': Cash_Flow,
            'Cash_to_Market_cap_ratio':Cash_to_Market_cap_ratio
            }
            
            print( '%(Count)4d) %(Company)-20s : \
                   Market Capatilization = %(Market_Cap)-10s \
                   Total Debt = %(Total_Debt)-8s \
                   Total Assets = %(Total_Asset)-8s \
                   Cash Flow = %(Cash_Flow)-10s \
                   Ratio = %(Cash_to_Market_cap_ratio)-10s' \
                   % result
                   )
        else:
            print( '***** Error Reading page %s' % (r'http://www.moneycontrol.com/%s' % stocks['href']) )
            


