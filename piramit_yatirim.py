def piramit_yatirim():
    import requests
    import io
    import re
    from datetime import date
    import pdfminer
    from pdfminer.pdfparser import PDFSyntaxError
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    import numpy as np
    import pandas as pd
    from itertools import chain
    from selenium.common.exceptions import NoSuchElementException
    from selenium import webdriver
    from fuzzywuzzy import process
    import datetime

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
    today = datetime.datetime.today().now().date()
    timestamp = datetime.datetime.today().now().time()

    driver_path = '/Users/merveogretmek/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path=driver_path)

    # PİRAMİT MENKUL KIYMETLER A.Ş.

    araci_kurum = 'PİRAMİT MENKUL KIYMETLER A.Ş.'

    print("Downloading PDF...")
    # PDF'i indirme
    try:
        driver.get("https://www.piramitmenkul.com.tr/Arastirma/Bulten/GUNLUKSTRATEJIBULTEN")
        href_xpath = '//*[@id="raporTable"]/tbody/tr[1]/td[2]/a'
        href = driver.find_element_by_xpath(href_xpath)
        url = href.get_attribute("href")
        r = requests.get(url)
        filename = f"piramit_{today}.pdf"
        open(filename, 'wb').write(r.content)
        print(f"PDF is downloaded from {url}")
        driver.close()

        # PDF'i text'e yazdırma
        piramit_text_list_1 = [pdf_to_text(filename)]

        # Düzenleme
        piramit_text_list_2 = []
        for element in piramit_text_list_1:
            piramit_text_list_2.append(element.replace('\n \n', '\n\n'))

        # Piramit için patternlar
        haber_text_pattern = '(?<=Şirket Haberleri).*?(?=Ekonomi Haberleri)'
        sirket_haberleri_pattern_1 = '\([A-Z][A-Z][A-Z][A-Z]+\):.*?(?=\\n\\n)'

        print("Parsing codes and haber...")
        # Haberlerin olduğu kısmı text'e yazma

        piramit_haber_text = []
        for element in piramit_text_list_2:
            if bool(re.search(haber_text_pattern, element, re.DOTALL)):
                piramit_haber_text.append(re.findall(haber_text_pattern, element, re.DOTALL))
                print("Parsing codes and news are completed.")
            else:
                print("There is no news in Piramit Menkul Kıymetler today.")
        piramit_haber_text = flatten(piramit_haber_text)


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
        piramit_timestamp_list = []
        piramit_url_list = []
        for i in range(len(piramit_lengths)):
            piramit_tarih_list.append([[today]] * piramit_lengths[i])
            piramit_araci_kurum_list.append([[araci_kurum]] * piramit_lengths[i])
            piramit_timestamp_list.append([[timestamp]] * piramit_lengths[i])
            piramit_url_list.append([[url]] * piramit_lengths[i])

        if len(piramit_haber_list_1) > 0:
            print("date_list, araci_kurum, timestamp and link are written.")
            # Listeleri tek boyutlu yapma
            piramit_tarih_list = flatten(piramit_tarih_list)
            piramit_araci_kurum_list = flatten(piramit_araci_kurum_list)
            piramit_timestamp_list = flatten(piramit_timestamp_list)
            piramit_url_list = flatten(piramit_url_list)

            # Columnları yazdırma
            col_1_and_2 = pd.DataFrame(piramit_haber_list_2, columns=['codes', 'news'])  # Hisse Sembolü ve Haber
            col_3 = pd.DataFrame(piramit_tarih_list, columns=['date_list'])  # Tarih
            col_4 = pd.DataFrame(piramit_araci_kurum_list, columns=['araci_kurum'])  # Aracı Kurum
            col_5 = pd.DataFrame(piramit_timestamp_list, columns=['timestamp'])  # Timestamp
            col_6 = pd.DataFrame(piramit_url_list, columns=['link'])  # URL

            # Columnları birleştirme
            df = pd.concat([col_1_and_2, col_3, col_4, col_5, col_6], axis=1)

            # Baştaki sondaki boşlukları silme
            df['codes'] = df['codes'].str.strip()
            df['news'] = df['news'].str.strip()

            # Hisse Sembolü'nden parantezleri çıkarma
            df['codes'] = df['codes'].str.extract(r"\((.*?)\)", expand=False)

            # Aynı haberi birden fazla şirket için yazdırma
            lens = df['codes'].str.split(',').map(len)
            df = pd.DataFrame({'codes': chainer_1(df['codes']),
                               'news': np.repeat(df['news'], lens),
                               'date_list': np.repeat(df['date_list'], lens),
                               'araci_kurum': np.repeat(df['araci_kurum'], lens),
                               'timestamp': np.repeat(df['timestamp'], lens),
                               'link': np.repeat(df['link'], lens)})

            # Satırları düzenleme
            df = df.replace(r'\s', ' ', regex=True)

            # Fazla boşlukları silme
            df['news'] = df['news'].replace('  ', ' ', regex=True)
            df['news'] = df['news'].replace('   ', ' ', regex=True)

            # ID Number yazdırma
            old_df = pd.read_csv("sirket_haberleri.csv")
            last_id = old_df['id_number'].iloc[-1]
            df['id_number'] = range(last_id + 1, last_id + 1 + len(df))

            df = df[['id_number', 'date_list', 'codes', 'news', 'araci_kurum', 'timestamp', 'link']]

            first_row_count = df.shape[0]

            # Hisse Sembolü kontrolü
            df['codes'] = df['codes'].astype(str) + '.E'
            df_bist = pd.read_csv('hissesembolu.csv', delimiter=';')
            df_merge = fuzzy_merge(df, df_bist, 'codes', "ISLEM  KODU", threshold=100)
            df = df_merge[['id_number', 'date_list', 'codes', 'news', 'araci_kurum', 'timestamp', 'link']]
            df['codes'] = df['codes'].str.strip('.E')

            second_row_count = df.shape[0]
            print(f"{second_row_count} news passed the Stock Name Test from total of {first_row_count} news.")

            df.to_csv("sirket_haberleri.csv", encoding="utf-8", index=False, header=False, mode='a')


    except NoSuchElementException:
        print("URL of the website or the xpath might be changed. Check URL and xpath.")

    print("Piramit Menkul Kıymetler is completed.")







