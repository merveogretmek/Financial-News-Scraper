def piramit_yatirim():
    import requests
    import io
    import re
    from datetime import date
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    import numpy as np
    import pandas as pd
    from itertools import chain
    from selenium import webdriver
    from fuzzywuzzy import process
    from datetime import datetime

    print('Modules imported.')

    # FONKSİYONLAR

    # PDF'ten text'e çevirme
    def pdf_to_text(path):
        manager = PDFResourceManager()
        retstr = io.StringIO()
        layout = LAParams(all_texts=True)
        device = TextConverter(manager, retstr, laparams=layout)
        filepath = open(path, 'rb')
        interpreter = PDFPageInterpreter(manager, device)

        for page in PDFPage.get_pages(filepath, check_extractable=False):
            interpreter.process_page(page)

        txt = retstr.getvalue()

        filepath.close()
        device.close()
        retstr.close()
        return txt

    # Listeyi tek boyutlu yapma
    def flatten(l):
        try:
            return flatten(l[0]) + (flatten(l[1:]) if len(l) > 1 else []) if type(l) is list else [l]
        except IndexError:
            return []

    # Aynı haberi birden fazla hisse için yazma
    def chainer_1(s):
        return list(chain.from_iterable(s.str.split(',')))

    def chainer_2(s):
        return list(chain.from_iterable(s.str.split('/')))

    # Şirket adı, hisse ismi eşleştirme
    def fuzzy_merge(df_1, df_2, key1, key2, threshold=90, limit=2):
        s = df_2[key2].tolist()

        m = df_1[key1].apply(lambda x: process.extract(x, s, limit=limit))
        df_1['matches'] = m

        m2 = df_1['matches'].apply(lambda x: ', '.join([j[0] for j in x if j[1] >= threshold]))
        df_1['matches'] = m2

        return df_1

    # Bugün'ün tarihi
    today = date.today()
    timestamp = datetime.now()

    driver_path = '/Users/merveogretmek/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=driver_path)

    # PİRAMİT MENKUL KIYMETLER A.Ş.

    araci_kurum = 'PİRAMİT MENKUL KIYMETLER A.Ş.'

    print("Downloading PDF...")
    # PDF'i indirme
    driver.get("https://www.piramitmenkul.com.tr/Arastirma/Bulten/GUNLUKSTRATEJIBULTEN")
    href_xpath = '//*[@id="raporTable"]/tbody/tr[1]/td[2]/a'
    href = driver.find_element_by_xpath(href_xpath)
    url = href.get_attribute("href")
    r = requests.get(url)
    filename = f"piramit_{today}.pdf"
    open(filename, 'wb').write(r.content)
    print("PDF is downloaded.")

    # PDF'i text'e yazdırma
    piramit_text_list_1 = [pdf_to_text(filename)]

    # Düzenleme
    piramit_text_list_2 = []
    for element in piramit_text_list_1:
        piramit_text_list_2.append(element.replace('\n \n', '\n\n'))

    # Piramit için patternlar
    haber_text_pattern = '(?<=Şirket Haberleri).*?(?=Ekonomi Haberleri)'
    sirket_haberleri_pattern_1 = '\([A-Z][A-Z][A-Z][A-Z]+\):.*?(?=\\n\\n)'

    print("Parsing Hisse Sembolü and Haber...")
    # Haberlerin olduğu kısmı text'e yazma
    piramit_haber_text = []
    for element in piramit_text_list_2:
        if bool(re.search(haber_text_pattern, element, re.DOTALL)):
            piramit_haber_text.append(re.findall(haber_text_pattern, element, re.DOTALL))
        else:
            print("Bugün Piramit'te şirket haberi yok.")
    piramit_haber_text = flatten(piramit_haber_text)
    print("Parsing Hisse Sembolü and Haber are completed.")

    # Şirket Haberlerini çekme
    piramit_haber_list_1 = []
    for element in piramit_haber_text:
        if bool(re.search(sirket_haberleri_pattern_1, element, re.DOTALL)):
            piramit_haber_list_1.append(re.findall(sirket_haberleri_pattern_1, element, re.DOTALL))

    # Haber sayısını hesaplama
    piramit_lengths = []
    for element in piramit_haber_list_1:
        piramit_lengths.append(len(element))

    # Hisse Sembolü ve Haber'i ayırma
    piramit_haber_list_2 = []
    for elements in piramit_haber_list_1:
        for element in elements:
            piramit_haber_list_2.append(element.split(':', maxsplit=1))

    # Tarih, Aracı Kurum, URL ve Timestamp yazdırma
    piramit_tarih_list = []
    piramit_araci_kurum_list = []
    piramit_url_list = []
    piramit_timestamp_list = []
    for i in range(len(piramit_lengths)):
        piramit_tarih_list.append([[today]] * piramit_lengths[i])
        piramit_araci_kurum_list.append([[araci_kurum]] * piramit_lengths[i])
        piramit_url_list.append([[url]] * piramit_lengths[i])
        piramit_timestamp_list.append([[timestamp]] * piramit_lengths[i])
    print("Tarih, Aracı Kurum and Timestamp are written.")

    # Listeleri tek boyutlu yapma
    piramit_tarih_list = flatten(piramit_tarih_list)
    piramit_araci_kurum_list = flatten(piramit_araci_kurum_list)
    piramit_url_list = flatten(piramit_url_list)
    piramit_timestamp_list = flatten(piramit_timestamp_list)

    # Columnları yazdırma
    col_1_and_2 = pd.DataFrame(piramit_haber_list_2, columns=['Hisse Sembolü', 'Haber'])  # Hisse Sembolü ve Haber
    col_3 = pd.DataFrame(piramit_tarih_list, columns=['Tarih'])  # Tarih
    col_4 = pd.DataFrame(piramit_araci_kurum_list, columns=['Aracı Kurum'])  # Aracı Kurum
    col_6 = pd.DataFrame(piramit_timestamp_list, columns=['Timestamp'])  # Timestamp

    # Columnları birleştirme
    df = pd.concat([col_1_and_2, col_3, col_4, col_6], axis=1)

    # Baştaki sondaki boşlukları silme
    df['Hisse Sembolü'] = df['Hisse Sembolü'].str.strip()
    df['Haber'] = df['Haber'].str.strip()

    # Hisse Sembolü'nden parantezleri çıkarma
    df['Hisse Sembolü'] = df['Hisse Sembolü'].str.extract(r"\((.*?)\)", expand=False)

    # Aynı haberi birden fazla şirket için yazdırma
    lens = df['Hisse Sembolü'].str.split(',').map(len)
    df = pd.DataFrame({'Hisse Sembolü': chainer_1(df['Hisse Sembolü']),
                       'Haber': np.repeat(df['Haber'], lens),
                       'Tarih': np.repeat(df['Tarih'], lens),
                       'Aracı Kurum': np.repeat(df['Aracı Kurum'], lens),
                       'Timestamp': np.repeat(df['Timestamp'], lens)})

    # Satırları düzenleme
    df = df.replace(r'\s', ' ', regex=True)

    # Fazla boşlukları silme
    df['Haber'] = df['Haber'].replace('  ', ' ', regex=True)
    df['Haber'] = df['Haber'].replace('   ', ' ', regex=True)

    # ID Number yazdırma
    df['ID Number'] = range(1, 1 + len(df))

    df = df[['ID Number', 'Tarih', 'Hisse Sembolü', 'Haber', 'Aracı Kurum', 'Timestamp']]

    df.to_csv("sirket_haberleri.csv", encoding="utf-8", index=False, header=False, mode='a')

    print("Piramit Yatırım is completed.")



