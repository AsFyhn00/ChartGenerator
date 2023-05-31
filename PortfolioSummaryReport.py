import pdfplumber
import regex as re
import os 
from tqdm import tqdm
import pandas as pd

class PDFDataExtractor:
    def __init__(self, usd_cost = 0.025, gbp_cost = 0.02, eur_cost = 0.000 ):

        self.usd_cost = usd_cost
        self.gbp_cost = gbp_cost
        self.eur_cost = eur_cost
        self._set_up()

    def _set_up(self,):
        self.b_init = {}
        hegde_cost = {'USD':self.usd_cost,'GBP':self.gbp_cost,'EUR':self.eur_cost} 
        self.b_init.update({'Hedge Cost':hegde_cost})

        self._retrieve_weight()

        hedge_weight = {'USD': self.usd_weight,'GBP':self.gbp_weight,'EUR':self.eur_weight}
        self.b_init.update({'Weight':hedge_weight})

    def _retrieve_weight(self,):
        try: 
            self.usd_weight = 1
            self.eur_weight = 0
            self.gbp_weight = 0
        except:
            self.usd_weight = 0
            self.eur_weight = 0
            self.gbp_weight = 0
            print('No weight found - defaulting to 0')

    def extract_data_around_word(self, pdf_path=None):
        if pdf_path is None:
            pdf_path = self.pdf_path

        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                
        keyfigures = []
        dur = re.findall(r'E.*?ur \d+\.\d+', text)[0]
        cpn = re.findall(r'Coupon .*? \d\.\d+', text)[0]
        yld = re.findall(r'dur.*?wei.*? \d\.\d+', text)[0]
        keyfigures = {'Modified duration': float(re.findall(r'\d+\.\d+', dur)[0]), 
                        'Effective Yield': float(re.findall(r'\d+\.\d+', yld)[0]),
                        'Coupon': float(re.findall(r'\d+\.\d+', cpn)[0]), 
                        }
        return keyfigures

    def calculate_hz(self,rul, yld, dur):
        # print('Calculating horizontal return')
        effective_yield = yld
        rul_contribution = rul * (dur - 1) / 100000
        hedge_cost = self.b_init['Hedge Cost']['USD'] * self.b_init['Weight']['USD'] + self.b_init['Hedge Cost']['GBP'] * self.b_init['Weight']['GBP'] + self.b_init['Hedge Cost']['EUR'] * self.b_init['Weight']['EUR']

        return {'hz return':effective_yield + rul_contribution - hedge_cost}

    def calculate_scenario(self, hz, dur):
        b = {}
        b.update({'100bp up': hz + dur/(100/1)})
        b.update({'50bp up': hz + dur/(100/2)})
        b.update({'50bp down': hz - dur/(100/2)})
        b.update({'100bp down': hz - dur/(100/1)})
        return b

    def main(self, pdf_path, rul=0):
        self.pdf_path = pdf_path

        key_figures_dict = self.extract_data_around_word()
        
        hz = self.calculate_hz(rul, key_figures_dict['Effective Yield'], key_figures_dict['Modified duration'])
        scenario = self.calculate_scenario(hz['hz return'], key_figures_dict['Modified duration'])
        
        return {**hz, **scenario, **key_figures_dict}

# # Usage example
# pdf_data_extractor = PDFDataExtractor(usd_cost=0.025, gbp_cost=0.02, eur_cost=0.000)

# # get all files in the specified directory
# path = r'path/to/pdf/files'
# df = pd.DataFrame()
# for file in os.listdir(path):
#     if (file.endswith(".pdf")) and (file.startswith("Summary")):
#         fund = file.split('-')[1]
#         if fund[-1:] == ' ':
#             fund = fund[:-1]
#         if fund[:1] == ' ':
#             fund = fund[1:]
#         print(f'Extracting data from {fund}')
#         _dict = pdf_data_extractor.main(pdf_path=f'{path}/{file}', rul=0)
#         _df = pd.DataFrame(_dict, index=[fund])
#         df = pd.concat([df,_df])
