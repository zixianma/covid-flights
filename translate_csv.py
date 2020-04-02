import pandas as pd
import googletrans
from googletrans import Translator

df = pd.read_excel("民航航班信息.xlsx",encoding='GBK')
translator = Translator()
translations = {}
unique_elements = df['国家'].unique()
for element in unique_elements:
    # add translation to the dictionary
    translations[element] = translator.translate(element).text

print(translations)