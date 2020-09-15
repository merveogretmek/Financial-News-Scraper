def ziraat_yatirim():
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
    driver = webdriver.Chrome(executable_path = driver_path)

    # ZİRAAT YATIRIM MENKUL DEĞERLER A.Ş.

    araci_kurum = 'ZİRAAT YATIRIM MENKUL DEĞERLER A.Ş.'

    print("Downloading PDF...")
    # PDF'i indirme
    ziraat_today = today.strftime("%d-%m-%y")
    url = f"https://www.ziraatyatirim.com.tr/documents/SS_{ziraat_today}.pdf"
    r = requests.get(url)
    filename = f"ziraat_{today}.pdf"
    open(filename, 'wb').write(r.content)
    print(f"PDF is downloaded from {url}")

    # PDF'i text'e yazdırma
    ziraat_text_list_1 = [pdf_to_text(filename)]

    # Düzenleme
    ziraat_text_list_2 = []
    for element in ziraat_text_list_1:
        ziraat_text_list_2.append(element.replace('\n \n', '\n\n'))

    # Ziraat için patternlar
    sirket_haberleri_pattern_1 = '\([A-Z][A-Z][A-Z][A-Z]+,.*?(?=\\n\\n)'
    sirket_haberleri_pattern_2 = '\([A-Z][A-Z][A-Z][A-Z]+\).*?(?=\\n\\n)'

    print("Parsing codes and Haber...")
    # Şirket Haberlerini çekme
    ziraat_haber_list_1 = []
    for element in ziraat_text_list_2:
        if bool(re.search(r'ŞİRKET HABERLERİ', element)):
            ziraat_haber_list_1.append(re.findall(sirket_haberleri_pattern_1, element, re.DOTALL))
            ziraat_haber_list_1.append(re.findall(sirket_haberleri_pattern_2, element, re.DOTALL))
        else:
            print("There is no news in Ziraat Yatırım Menkul Değerler today.")
    print("Parsing codes and Haber are completed.")

    # Haber sayısını hesaplama
    ziraat_lengths = []
    for element in ziraat_haber_list_1:
        ziraat_lengths.append(len(element))

    # Hisse Sembolü ve Haber'i ayırma
    ziraat_haber_list_2 = []
    for elements in ziraat_haber_list_1:
        for element in elements:
            ziraat_haber_list_2.append(element.split(':', maxsplit=1))

    # Tarih, Aracı Kurum ve URL yazdırma
    ziraat_tarih_list = []
    ziraat_araci_kurum_list = []
    ziraat_url_list = []
    ziraat_timestamp_list = []
    for i in range(len(ziraat_lengths)):
        ziraat_tarih_list.append([[today]] * ziraat_lengths[i])
        ziraat_araci_kurum_list.append([[araci_kurum]] * ziraat_lengths[i])
        ziraat_url_list.append([[url]] * ziraat_lengths[i])
        ziraat_timestamp_list.append([[timestamp]] * ziraat_lengths[i])
    print("date_list,  and Timestamp are written.")

    # Listeleri tek boyutlu yapma
    ziraat_tarih_list = flatten(ziraat_tarih_list)
    ziraat_araci_kurum_list = flatten(ziraat_araci_kurum_list)
    ziraat_url_list = flatten(ziraat_url_list)
    ziraat_timestamp_list = flatten(ziraat_timestamp_list)

    # Columnları yazdırma
    col_1_and_2 = pd.DataFrame(ziraat_haber_list_2, columns=['codes', 'news'])  # Hisse Sembolü ve Haber
    col_3 = pd.DataFrame(ziraat_tarih_list, columns=['date_list'])  # Tarih
    col_4 = pd.DataFrame(ziraat_araci_kurum_list, columns=['araci_kurum'])  # Aracı Kurum
    col_5 = pd.DataFrame(ziraat_timestamp_list, columns=['timestamp'])  # Timestamp
    col_6 = pd.DataFrame(ziraat_url_list, columns=['link'])  # URL

    # Columnları birleştirme
    df = pd.concat([col_1_and_2, col_3, col_4, col_5, col_6], axis=1)
    df = df.dropna()

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

    # Baştaki sondaki boşlukları silme
    df['codes'] = df['codes'].str.strip()
    df['news'] = df['news'].str.strip()

    # Hisse sembolü dışındakileri silme
    df = df[df['codes'].str.contains('[A-Z][A-Z][A-Z][A-Z]+')]

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

    df.to_csv("sirket_haberleri.csv", encoding="utf-8", index=False, header=False, mode='a')

    print("Ziraat Yatırım Menkul Değerler is completed.")
