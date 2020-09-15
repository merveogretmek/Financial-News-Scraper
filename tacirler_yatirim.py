def tacirler_yatirim():
    import requests
    import io
    import re
    from datetime import date
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
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
    today = datetime.datetime.today().now().date()
    timestamp = datetime.datetime.today().now().time()

    driver_path = '/Users/merveogretmek/Downloads/chromedriver'
    driver = webdriver.Chrome(executable_path = driver_path)

    # TACİRLER YATIRIM MENKUL KIYMETLER A.Ş.

    araci_kurum = 'TACİRLER YATIRIM MENKUL KIYMETLER A.Ş.'

    print("Downloading PDF...")
    # PDF'i indirme
    driver.get("https://www.tacirler.com.tr/Hizmetler/ArastirmaGunlukBulten.aspx")
    href_xpath = '//*[@id="aspnetForm"]/div[4]/div/div/div[2]/div[2]/ul[1]/li/a'
    href = driver.find_element_by_xpath(href_xpath)
    url = href.get_attribute("href")
    r = requests.get(url)
    filename = f"tacirler_{today}.pdf"
    open(filename, 'wb').write(r.content)
    print(f"PDF is downloaded from {url}")

    # PDF'i text'e yazdırma
    tacirler_text_list_1 = [pdf_to_text(filename)]

    # Düzenleme
    tacirler_text_list_2 = []
    for element in tacirler_text_list_1:
        tacirler_text_list_2.append(element.replace('\n \n ', '\n\n'))

    # Tacirler Yatırım için patternlar
    haber_text_pattern = '(?<=Şirket ve Sektör Haberleri).*?(?=Teknik Analiz)'

    print("Parsing codes and news...")
    # Haberlerin olduğu kısmı text'e yazma
    tacirler_haber_text = []
    for element in tacirler_text_list_2:
        if bool(re.search(haber_text_pattern, element, re.DOTALL)):
            tacirler_haber_text.append(re.findall(haber_text_pattern, element, re.DOTALL))
        else:
            print("There is no news in Tacirler Yatırım Menkul Kıymetler today.")
    tacirler_haber_text = flatten(tacirler_haber_text)
    print("Parsing codes and news are completed.")

    # Şirket Haberlerini çekme
    tacirler_haber_list_1 = []
    for element in tacirler_haber_text:
        tacirler_haber_list_1.append(element.split("\n\n"))

    tacirler_haber_list_1 = list(
        map(lambda words: list(filter(lambda word: len(word) > 20, words)), tacirler_haber_list_1))

    # Haber sayısını hesaplama
    tacirler_lengths = []
    for element in tacirler_haber_list_1:
        tacirler_lengths.append(len(element))

    # Hisse Sembolü ve Haber'i ayırma
    tacirler_haber_list_2 = []
    for elements in tacirler_haber_list_1:
        for element in elements:
            if ' – ' in element:
                tacirler_haber_list_2.append(element.split(' – ', 1))
            elif ' - ' in element:
                tacirler_haber_list_2.append(element.split(' - ', 1))

    # Tarih, Aracı Kurum ve URL yazdırma
    tacirler_tarih_list = []
    tacirler_araci_kurum_list = []
    tacirler_timestamp_list = []
    tacirler_url_list = []
    for i in range(len(tacirler_lengths)):
        tacirler_tarih_list.append([[today]] * tacirler_lengths[i])
        tacirler_araci_kurum_list.append([[araci_kurum]] * tacirler_lengths[i])
        tacirler_timestamp_list.append([[timestamp]] * tacirler_lengths[i])
        tacirler_url_list.append([[url]] * tacirler_lengths[i])
    print("date_list, araci_kurum, timestamp and link are written.")

    # Listeleri tek boyutlu yapma
    tacirler_tarih_list = flatten(tacirler_tarih_list)
    tacirler_araci_kurum_list = flatten(tacirler_araci_kurum_list)
    tacirler_timestamp_list = flatten(tacirler_timestamp_list)
    tacirler_url_list = flatten(tacirler_url_list)

    # Columnları yazdırma
    col_1_and_2 = pd.DataFrame(tacirler_haber_list_2, columns=['codes', 'news'])  # Hisse Sembolü ve Haber
    col_3 = pd.DataFrame(tacirler_tarih_list, columns=['date_list'])  # Tarih
    col_4 = pd.DataFrame(tacirler_araci_kurum_list, columns=['araci_kurum'])  # Aracı Kurum
    col_5 = pd.DataFrame(tacirler_timestamp_list, columns=['timestamp'])  # Timestamp
    col_6 = pd.DataFrame(tacirler_url_list, columns=['link'])  # URL


    # Columnları birleştirme
    df = pd.concat([col_1_and_2, col_3, col_4, col_5, col_6], axis=1)

    # NaN değerleri silme
    df = df.dropna()

    first_row_count = df.shape[0]

    # BIST Verisi ile Matchleme
    df_bist = pd.read_csv('hissesembolu.csv', delimiter=';')

    df['codes'] = df['codes'].str.upper()
    df['codes'] = df['codes'].str.replace('Ç', 'C')
    df['codes'] = df['codes'].str.replace('Ğ', 'G')
    df['codes'] = df['codes'].str.replace('İ', 'I')
    df['codes'] = df['codes'].str.replace('Ö', 'O')
    df['codes'] = df['codes'].str.replace('Ş', 'S')
    df['codes'] = df['codes'].str.replace('Ü', 'U')

    df = df.rename(columns={'codes': 'BULTEN ADI'})
    df = fuzzy_merge(df, df_bist, 'BULTEN ADI', 'BULTEN ADI', threshold=85)
    df = pd.merge(df, df_bist, on=['BULTEN ADI'])
    df = df[["ISLEM  KODU", "news", "date_list", "araci_kurum", "timestamp", "link"]]
    df = df.rename(columns={'ISLEM  KODU': 'codes'})
    df['codes'] = [x.split('.')[0] for x in df['codes']]

    # Baştaki sondaki boşlukları silme
    row_count = df.shape[0]
    if row_count >= 1:
        df['codes'] = df['codes'].str.strip()
        df['news'] = df['news'].str.strip()

    # Satırları düzenleme
    df = df.replace(r'\s', ' ', regex=True)

    # Fazla boşlukları silme
    df['news'] = df['news'].replace('  ', ' ', regex=True)
    df['news'] = df['news'].replace('   ', ' ', regex=True)

    # ID Number yazdırma
    old_df = pd.read_csv("ortak.csv")
    last_id = old_df['id_number'].iloc[-1]
    df['id_number'] = range(last_id + 1, last_id + 1 + len(df))

    second_row_count = df.shape[0]

    df = df[['id_number', 'date_list', 'codes', 'news', 'araci_kurum', 'timestamp', 'link']]
    print(f"Tacirler Yatırım'da {first_row_count} haberden {second_row_count} tanesi yazdırıldı.")

    df.to_csv("sirket_haberleri.csv", encoding="utf-8", index=False, header=False, mode='a')

    print("Tacirler Yatırım Menkul Kıymetler is completed.")