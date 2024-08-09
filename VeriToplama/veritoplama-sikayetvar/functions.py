# Gerekli kütüphaneler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time
import csv
from datetime import date

today = date.today()

driver = webdriver.Chrome()
# Sayfanın yüklenmesi için en fazla ne kadar bekleyeceğini belirler.
driver.set_page_load_timeout(300)

# WebDriver'ın yönlendirilmesi için yazılan fonksiyon
def startWebdriver():
    driver.get("https://www.sikayetvar.com/sikayetler")
    time.sleep(5)
    
# Şikayet içeriklerini çeken fonksiyon.
def bringComplaints():
    # işlem yarıda kesilirse nereden devam edeceğini sağlamamız için oluşturulan değişken
    skip_rows = 0

    # Çekilen dosyadaki URL'lerin okunması
    with open('sikayetVar-6751-veri-URL.csv', mode='r', newline='', encoding='utf-8') as urlFile:
        # Dosyayı Dictionary olarak okuyor.
        readCSV = csv.DictReader(urlFile)
        # çekilen şikayetler dosyaya ekleneceği için dosyayı append modunda açıyoruz.
        with open('sikayetVar-sikayetler2.csv', mode='a', encoding='utf-8', newline='') as complaintsFile:
            writer = csv.writer(complaintsFile)
            # Dosyanın boş olup olmadığını kontrol etmek için bu koşul eklendi. Eğer dosya boşsa ilk satır ID ve Sikayet Icerigi olacak. Eğer boş değilse verileri ekleyerek devam edecek.
            if complaintsFile.tell() == 0:
                writer.writerow(["ID", "Sikayet Icerigi"])
            
            # dosyamızda bulunan satırları for döngüsü ile işliyoruz.
            for current_row, SikayetIcerigi in enumerate(readCSV):
                if current_row < skip_rows:
                    continue  # skip_rows değişkenine atanan sayı kadar satırları atlar.
                
                # skip_rows değişkenine atanan sayıdan sonraki verileri işlemeye başlar.
                # şikayetleri ekrandan takip edebilmek için ekrana yazdırıyoruz.
                print(SikayetIcerigi["Sikayet URL'leri"])
                # dosyadan okunan URL'ye gidiyor.
                driver.get(SikayetIcerigi["Sikayet URL'leri"])
                # sayfaların geç yüklenebilmesine bağlı olarak bekleme süresi ekliyoruz. (donanımınıza göre bu süre arttırılabilir veya azaltılabilir.)
                time.sleep(7)
                # sayfa içerisinde şikayetlerin yer aldığı kısmı CSS_SELECTOR yardımıyla yakalıyoruz ve SikayetIcerikleri değişkenine atıyoruz.
                sikayetIcerikleri = driver.find_element(By.CSS_SELECTOR, "#main-wrapper > main > div > div.page-grid > div.page-grid__main > div.detail-card-v2.complaint-detail.selection-share > div.complaint-detail-description > p").text
                # şikayetin yakalanıp yakalanmadığını izlemek için ekrana yazdırıyoruz.
                print(sikayetIcerikleri)
                # yakalanan şikayeti dosyaya yazıyoruz.
                writer.writerow([current_row + 1, sikayetIcerikleri])
        
# startWebDriver fonksiyonu içerisindeki şikayetvar sayfasına gidilip şikayet içeriklerinin URL'sini çeken fonksiyon. Tek Sayfayı çeker
def complaintsURLsinglePage():
    # sayfa içerisinde şikayetlerin yer aldığı kısmı CSS_SELECTOR yardımıyla yakalıyoruz ve sikayetLinkleri değişkenine atıyoruz.
    sikayetLinkleri = driver.find_elements(By.CSS_SELECTOR,"#complaints > article > h2 > a")
    # linkleri saymak için bir sayaç tanımlıyoruz.
    sikayetLinkSayaci = 1
    # şikayetleri saklamak için bir liste oluşturuyoruz.
    sikayetlerTekSayfa = []
    # her bir şikayeti yakalayıp kaydetmemiz için döngü oluşturuyoruz.
    for index,sikayetLink in enumerate(sikayetLinkleri):
        # şikayet linklerinin URL'sini yakalıyoruz.
        sikayetLinkHref = sikayetLink.get_attribute("href")
        # yakaladığımız URL'yi anlık olarak kontrol etmemiz için ekrana yazdırıyoruz.
        print(f"LINK {sikayetLinkSayaci}: ",sikayetLinkHref)
        sikayetLinkSayaci+=1
        time.sleep(0.25)
        sikayetID = index + 1
        # yakalanan URL'yi oluşturduğumuz listenin içine atıyoruz.
        sikayetlerTekSayfa.append([sikayetID,sikayetLinkHref])
    # URL'lerin bulunduğu listeyi ekrana yazdırıyoruz.
    print(sikayetlerTekSayfa)
    
    # dosyada ne kadar veri olduğunu görebilmemiz için listenin uzunluğunu başka bir değişkene atıyoruz.
    sikayetSayisi = len(sikayetlerTekSayfa)
    # oluşturduğumuz listeyi ve listenin uzunluğu saveToCSV ismindeki fonksiyonumuza göndererek dosyamızı kaydediyoruz.
    saveToCSV(sikayetlerTekSayfa,sikayetSayisi)
    
# startWebDriver fonksiyonu içerisindeki şikayetvar sayfasına gidilip şikayet içeriklerinin URL'sini çeken fonksiyon. Birden çok sayfa çeker
def complaintsURLmultiplePage():
    # Şikayet linklerini saymak için oluşturulan bir sayaç
    sikayetURLsayaci = 1
    # işlemin yapılacağı sayfa aralıklarını belirlemek için oluşturulan değişkenler.
    baslangicSayfasi=1
    bitisSayfasi=350
    sikayetlerCokluSayfa = []
    # belirtilen sayfa aralıkları için döngü başlatıyoruz.
    for i in range(baslangicSayfasi,bitisSayfasi):
        # sayfa içerisinde şikayetlerin yer aldığı kısmı CSS_SELECTOR yardımıyla yakalıyoruz ve sikayetLinkleri değişkenine atıyoruz.
        sikayetLinkleri = driver.find_elements(By.CSS_SELECTOR,"#complaints > article > h2 > a")
        # sayfadaki şikayetlerin linklerini işlemek için döngü oluşturuyoruz.
        for sikayetLink in sikayetLinkleri:
            # şikayetlerin linklerini yakalayıp sikayetLinkHref isimli değişkene atıyoruz.
            sikayetLinkHref=sikayetLink.get_attribute("href")
            # kontrol etmemiz için şikayet linklerinin kaçınçı şikayet olduğuyla beraber ekrana yazdırıyoruz.
            print(f"LINK {sikayetURLsayaci}: ",sikayetLinkHref)
            sikayetID = sikayetURLsayaci
            # Şikayet ID'si ve Şikayet linklerini oluşturduğumuz listenin içerisine ekliyoruz.
            sikayetlerCokluSayfa.append([sikayetID,sikayetLinkHref])
            sikayetURLsayaci+=1
            time.sleep(0.15)
        # sayfada şikayetler bittikten sonra diğer şikayetlere geçiyoruz.
        driver.get(f"https://www.sikayetvar.com/sikayetler?page={i}")
        i+=1
    # dosyada ne kadar veri olduğunu görebilmemiz için listenin uzunluğunu başka bir değişkene atıyoruz.
    sikayetSayisi=len(sikayetlerCokluSayfa)
    # oluşturduğumuz listeyi ve listenin uzunluğu saveToCSV ismindeki fonksiyonumuza göndererek dosyamızı kaydediyoruz.
    saveToCSV(sikayetlerCokluSayfa,sikayetSayisi)
    time.sleep(5)
    
# Marka bazlı veri çekmek için oluşturulan fonksiyon
def URLfromBrandSingle():
    # Eklenen URL'ye gider.
    driver.get('https://www.sikayetvar.com/vodafone?page=1')
    # Sayfada bulunan markaların olduğu complaint-layer CLASS'ına sahip şikayetleri yakalar.
    markaSikayetleri = driver.find_elements(By.CLASS_NAME,"complaint-layer")
    # Yakalanan şikayetlerin tutulması için liste oluşturulur.
    sikayetlerTekSayfa = []
    # şikayetlerin işlenmesi için döngü başlatır.
    for index,markaSikayetLink in enumerate(markaSikayetleri):
        # yakalanan şikayetlerin linklerini alır.
        markaSikayetLinkleri = markaSikayetLink.get_attribute("href")
        sikayetID = index + 1
        # çekilen şikayetlerin linklerini görebilmemiz için ekrana yazdırır.
        print(f"LINK {sikayetID}: ",markaSikayetLinkleri)
        time.sleep(0.25)
        # Yakalanan şikayet URL'sini listeye ekler.
        sikayetlerTekSayfa.append(markaSikayetLinkleri)
    # Listeyi ekrana yazdırır.
    print(sikayetlerTekSayfa)
    # Listede ne kadar veri çekildiyse onu görmemiz için listenin uzunluğunu ekrana yazdırır.
    print(len(sikayetlerTekSayfa))
    
def saveToCSV(veri,veriUzunlugu,veriTuru):
    # veriTuru parametresine bağlı olarak veri türünü belirleyen koşulu yazdık.
    if veriTuru==2:
        veriTuru = "Marka"
    elif veriTuru ==1:
        veriTuru = "URL"
    elif veriTuru == 3:
        veriTuru ="markaURL"
    elif veriTuru == 4:
        veriTuru = "markasalSikayetLinkleri"
    else:
        veriTuru="undefined"
        
    # Dosyayı oluşturarak alınan veriyi aşağıda yazan dosya ismi formatında yazarak kaydeder.
    with open(f'sikayetVar-{veriUzunlugu}-veri-{veriTuru}-{today}.csv',mode='w',newline='',encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["ID",f"{veriTuru}"])
        writer.writerows(veri)
        
# Marka bazlı veri çekmek için oluşturulan fonksiyon
def URLfromBrandMultiple():
    # Çekilen şikayet sayısını görmemiz için bir değişken oluşturduk.
    sikayetCekmeSayaci = 1
    # işlemin yapılacağı sayfa aralıklarını belirlemek için oluşturulan değişkenler.
    baslangicSayfasi=2
    bitisSayfasi=100
    # Şikayet linklerinin tutulacağı bir liste oluşturduk.
    sikayetlerCokluSayfa = []
    # başlangıç için ilk sayfanın linkini girdik.
    driver.get(f"https://www.sikayetvar.com/vodafone?page=1")
    # Yukarıda belirttiğimiz sayfa aralığındaki şikayetleri çekmek için döngü oluşturduk.
    for i in range(baslangicSayfasi,bitisSayfasi):
        # Sayfa içerisinde buluncan complaint-layer CLASS'ına sahip olan elementleri yakalamak için değişken oluşturduk.
        markaSikayetLinkleri = driver.find_elements(By.CLASS_NAME,'complaint-layer')
        # Sayfa içerisinde bulunan şikayetleri işlememiz için bir döngü oluşturduk.
        for markaSikayetLinki in markaSikayetLinkleri:
            # Sayfa içerisinde bulunan şikayetlerin linklerini yakalayarak değişkenimize atadık.
            markaSikayetLinkHref=markaSikayetLinki.get_attribute("href")
            # Çekilen verileri görmemiz için ekrana yazdırdık.
            print(f"LINK {sikayetCekmeSayaci}: ",markaSikayetLinkHref)
            # Çekilen verileri oluşturduğumuz listeye ekledik.
            sikayetlerCokluSayfa.append(markaSikayetLinkHref)
            sikayetCekmeSayaci+=1
            time.sleep(0.15)
        # Sayfada biten şikayetler için diğer sayfaya geçme işlemini yaptık
        driver.get(f"https://www.sikayetvar.com/vodafone?page={i}")
        i+=1
    # Verilerin çekilmiş halini ekrana yazdırdık.
    print("DATA - ORGANİK = ",sikayetlerCokluSayfa)
    # Veri tekrarına düşmemek için önce kümeye ardından tekrar listeye çevirdik böylelikle birden fazla bulunma durumunu ortadan kaldırmış olduk.
    sikayetlerCokluSayfa=set(sikayetlerCokluSayfa)
    sikayetlerCokluSayfa=list(sikayetlerCokluSayfa)
    # listenin son halini ve içerisindeki verinin uzunluğunu ekrana yazdırdık.
    print(sikayetlerCokluSayfa)
    print(len(sikayetlerCokluSayfa))

# Markaların isimlerini çeken fonksiyon
def brandNameList():
    # Başlangıç için aşağıdaki web sayfasına giden fonksiyonu kullandık.
    driver.get("https://www.sikayetvar.com/tum-markalar")
    # çektiğimiz markaların sayısını takip etmek için bir sayaç tanımladık.
    markaCekmeSayaci = 1
    # Hangi sayfalar arasında olacağını tanımlıyoruz.
    baslangicSayfasi=2
    bitisSayfasi=11
    # marka isimlerinin saklanması için bir liste oluşturuyoruz.
    markaIsimleri = []
    try:
        # yukarıdaki değişkenlerde belirtilen başlangıç sayfasından bitiş sayfasına kadar olan verileri çekmek için döngü oluşturuyoruz.
        for i in range(baslangicSayfasi,bitisSayfasi):
            # Marka isimlerini yakalamak için markaListeleri adında bir değişken oluşturup yakaladığımız marka isimlerini değişkenin içine atıyoruz.
            markaListeleri = driver.find_elements(By.XPATH,"/html/body/div[1]/main/div/div/section[3]/div[1]/ul/li/div/div[1]/div/a/span")
            # Yakaladığımız marka isimlerini işlemek için döngüye alıyoruz.
            for markaIsimleri in markaListeleri:
                # Yakaladığımız markaları kontrol etmek için ekrana yazdırıyoruz.
                print(f"MARKA {markaCekmeSayaci}: ",markaIsimleri.text)
                # Oluşturduğumuz sayaçı markaID isimli değişkene atayarak çektiğimiz verilerin ID'si olarak listeye ekliyoruz.
                markaID = markaCekmeSayaci
                markaIsimleri.append([markaID,markaIsimleri.text])
                markaCekmeSayaci+=1
            # Açılan sayfa için işlem bittiğinde diğer sayfaya geçiyoruz.
            driver.get(f"https://www.sikayetvar.com/tum-markalar?page={i}")
            i+=1
    except KeyboardInterrupt:
        # Programdan çıkmak istediğimiz zaman aşağıdaki mesajı kullanıcıya gösteriyoruz.
        print("İşlem yarıda kesiliyor. Veriler kaydedildikten sonra program kapanacak.")
        
    # işlem sonunda marka listesini yazdırıyoruz ve marka listesinin veri büyüklüğünü veriUzunluğu değişkenine atıyoruz.
    print(markaIsimleri)
    veriUzunlugu=len(markaIsimleri)
    
    # Yukarıda çekmiş olduğumuz verilerin listesini,büyüklüğünü ve türünü fonksiyona göndererek dosyaya kaydediyoruz.
    saveToCSV(markaIsimleri,veriUzunlugu,2)
    
def brandLinkList():
        # Başlangıç için aşağıdaki web sayfasına giden fonksiyonu kullandık.
        driver.get("https://www.sikayetvar.com/tum-markalar")
        driver.maximize_window()
        # Çektiğimiz marka linklerinin sayısını takip etmek için bir sayaç tanımladık.
        markaCekmeSayaci = 1
        # Hangi sayfalar arasında olacağını tanımlıyoruz.
        baslangicSayfasi=2
        bitisSayfasi=11
        # marka isimlerinin saklanması için bir liste oluşturuyoruz.
        markaLinkleri = []
        try:
            # yukarıdaki değişkenlerde belirtilen başlangıç sayfasından bitiş sayfasına kadar olan verileri çekmek için döngü oluşturuyoruz.
            for i in range(baslangicSayfasi,bitisSayfasi):
                time.sleep(4)
                 # Marka linklerini yakalamak için markaLinkleri adında bir değişken oluşturup yakaladığımız marka linklerini değişkenin içine atıyoruz.
                markaLinkleri = driver.find_elements(By.CSS_SELECTOR,"#main-wrapper > main > div > div > section.sec-post > div.story-block > ul > li > div > div.brand-info > div > a")
                # Yakaladığımız marka isimlerini işlemek için döngüye alıyoruz.
                for markaLinki in markaLinkleri:
                    # Yakaladığımız marka linklerini kontrol etmek için ekrana yazdırıyoruz.
                    print(f"MARKA {markaCekmeSayaci}: ",markaLinki.get_attribute("href"))
                    # Oluşturduğumuz sayaçı markaID isimli değişkene atayarak çektiğimiz verilerin ID'sini ve linklerini listeye ekliyoruz.
                    markaID = markaCekmeSayaci
                    markaLinkleri.append([markaID,markaLinki.get_attribute('href')])
                    markaCekmeSayaci+=1
                # Açılan sayfa için işlem bittiğinde diğer sayfaya geçiyoruz.
                driver.get(f"https://www.sikayetvar.com/tum-markalar?page={i}")
                i+=1
        except KeyboardInterrupt:
            # Programdan çıkmak istediğimiz zaman aşağıdaki mesajı kullanıcıya gösteriyoruz.
            print("İşlem yarıda kesiliyor. Veriler kaydedildikten sonra program kapanacak.")
        
        # işlem sonunda marka linklerinin olduğu listeyi yazdırıyoruz ve oluşturduğumuz listenin veri büyüklüğünü veriUzunluğu değişkenine atıyoruz.   
        print(markaLinkleri)
        veriUzunlugu=len(markaLinkleri)
        # Yukarıda çekmiş olduğumuz verilerin listesini,büyüklüğünü ve türünü fonksiyona göndererek dosyaya kaydediyoruz.
        saveToCSV(markaLinkleri,veriUzunlugu,3)
        
def brandURLmultiple():
    with open('sikayetVar-144-veri-markaURL-2024-07-26.csv',mode='r',encoding='utf-8') as file:
        # Dosyayı Dict olarak okuyup listeye çevirir.
        reader = csv.DictReader(file)
        markaLinkleri=list(reader)
        # Şikayet linklerinin tutulacağı bir liste oluşturuyoruz.
        markaSikayetLinkListesi = []
        sikayetCekmeSayaci = 1
        # Her markanın url'sini çekmek için döngü oluşturuyoruz.
        for markaLinki in markaLinkleri:
            # Şikayetleri çekilecek markanın linkini ekrana yazdırıyoruz.
            print(markaLinki['markaURL'])
            # işlemin yapılacağı sayfa aralıklarını belirlemek için oluşturulan değişkenler.
            baslangicSayfasi=2
            bitisSayfasi=230
            # Çekilen markanın ilk sayfasına gider.
            driver.get(f"{markaLinki['markaURL']}?page=1")
            # Yukarıda brlirlediğimiz sayfa aralığında döngü oluşturur.
            for i in range(baslangicSayfasi,bitisSayfasi):
                # Şikayetleri yakalayarak aşağıdaki değişkene atıyoruz.
                markaSikayetLinkleri = driver.find_elements(By.CLASS_NAME,'complaint-layer')
                for markaSikayetLinki in markaSikayetLinkleri:
                    # Yakaladığımız şikayetlerin linklerini aşağıdaki değişkene atıyoruz.
                    markaSikayetLinkHref=markaSikayetLinki.get_attribute("href")
                    # Kaçıncı linkte olduğunu ve çekilen linki ekrana yazdırıyoruz.
                    print(f"LINK {sikayetCekmeSayaci}: ",markaSikayetLinkHref)
                    # Çektiğimiz linkleri oluşturduğumuz değişkene atıyoruz.
                    markaSikayetLinkListesi.append(markaSikayetLinkHref)
                    sikayetCekmeSayaci+=1
                    time.sleep(0.15)
                # Sonraki sayfaya geçiyoruz.
                driver.get(f"{markaLinki['markaURL']}?page={i}")
                i+=1
            # O anda çekilen kaçıncı verideyse onu ekrana yazdırır.
            print("Su anda veri sayısı",len(markaSikayetLinkListesi))
            
        print("DATA - ORGANİK = ",markaSikayetLinkListesi)
        # Listemizi önce kümeye çevirip sonrasında tekrar listeye çeviriyoruz. Çünkü verilerimizin tekrara düşmesini istemiyoruz.
        markaSikayetLinkListesi=set(markaSikayetLinkListesi)
        markaSikayetLinkListesi=list(markaSikayetLinkListesi)
        # Veri listesini ve uzunluğunu ekrana yazdırıyoruz.
        print(markaSikayetLinkListesi)
        print(len(markaSikayetLinkListesi))

# Markaların kaç sayfa şikayet barındırdığını yakalamak için oluşturulan fonksiyon
def brandPageCounter():
    with open('sikayetVar-144-veri-markaURL-2024-07-26.csv',mode='r',encoding='utf-8') as file:
        reader = csv.DictReader(file)
        # Dosyayı liste olarak okuyup markaLinkleri değişkenine bu listeyi atıyoruz.
        markaLinkleri=list(reader)
        sayfaSayisi = []
        for markaLinki in markaLinkleri:
            # Liste olarak çektiğimiz her bir markayı çağırıp, en altta bulunan sayfa sayıları bölümünden çekiyoruz.
            driver.get(f"{markaLinki['markaURL']}")
            sonSayfa = driver.find_element(By.CSS_SELECTOR,"#main-content > div.brand-detail-grid__main.model-detail-show-cover > nav > ul > li:nth-child(7) > a")
            print(sonSayfa.text)
            # Çektiğimiz sayfayı döngülerde kullanabilmemiz için int yani tam sayı veri tipine çeviriyoruz.
            sayisal = int(sonSayfa.text)
            sayfaSayisi.append(sayisal)
        # Çektiğimiz verinin bulunduğu listeyi ekrana yazdırıyoruz.
        print(sayfaSayisi)
        # Çektiğimiz verinin uzunluğunu ekrana yazdırıyoruz.
        print(len(sayfaSayisi))
        
        # Çektiğimiz veri içerisindeki en düşük sayıyı ekrana yazdırıyoruz.(Markaların şikayet barındırdığı sayfa değişkenlik gösterebildiği için bunu yazdırdık.
        # dilersek her sayfa için döngü sayısını değiştirmek yerine en düşük sayfası olan markayı baz alarak sabit bir değer atayıp işlemi yapabiliriz. En düşük sayfa sayısına sahip değer
        # her markada o sayfa barınacağı için sabit bir değer olarak kullanılabilir.)
        print(min(sayfaSayisi))

# Hata ile karşılaşması durumunda hata mesajını error_log.txt dosyasına yazdırıyoruz.
def log_error_to_file(error_message):
    with open('error_log.txt', mode='a', encoding='utf-8') as error_file:
        error_file.write(f"{error_message}\n")

# Marka bazlı çekilen Şikayet URL'lerin çekilmesi ve kaydedilmesi için yazılan fonksiyon.
def getComplaintFromBrandURL():    
    # WebDriver'ı tam ekran yapmak için kullanılan fonksiyon
    driver.maximize_window()
    # Çekilen şikayetler için sayaç oluşturuyoruz.
    sikayetURLsayaci = 1
    # Çekilen markaların URL'lerin olduğu dosyayı okuma modunda açıyoruz.
    with open('sikayetVar-144-veri-markaURL-2024-07-26.csv', mode='r', newline='', encoding='utf-8') as brandURLfile:
        # Dosyayı Dictionary olarak okuyarak çektiğimiz verileri listeye dönüştürüyoruz.
        reader = csv.DictReader(brandURLfile)
        markaLinkleri=list(reader)
        try:
            # Dosyada bulunan verileri işlemek için döngü oluşturuyoruz.
            for markaLinki in markaLinkleri:
                # Çekilecek verinin markasının URL'sini ekrana yazdırıyoruz.
                print(markaLinki["markaURL"])
                # Hangi sayfalar arasında olacağınız tanımlıyoruz.(Bitiş sayfasını 230 olarak belirledik çünkü markaların sayfalarındaki sayfa sayılarını çekerken en düşük sayfa sayısına sahip
                # markanın 230 sayfa içerdiğini gördük.)
                baslangicSayfasi=2
                bitisSayfasi=230
                try:
                    # Dosyadan okuduğumuz markanın ilk şikayet sayfasını açıyoruz.
                    driver.get(f"{markaLinki['markaURL']}?page=1")
                except TimeoutException:
                    # Veri boyutu yükseldiği için zaman aşımı hatasıyla karşılaşmamız durumunda ekrana hata mesajını yazdırıyoruz. 
                    error_message = f"Zaman aşımı hatası: {markaLinki['markaURL']}"
                    print(error_message)
                    # Hata mesajlarını daha sonrasında incelememiz için log_error_to_file() fonksiyonunu kullanarak txt dosyasına kaydediyoruz.
                    log_error_to_file(error_message) # Fonksiyon içeriği 322. Satırda bulunmaktadır.
                    continue
                
                # Belirtlilen sayfa aralıklarına verilerin çekilmesi için döngü oluşturuyoruz.
                for i in range(baslangicSayfasi,bitisSayfasi):
                    # Her sayfada verileri saklamamız için liste oluşturuyoruz. Liste döngünün başına geldiğinde sıfırlanıyor çünkü performans açısından sorun yaratmasını istemiyoruz.
                    markaLinkleri = []
                    try:
                        # Şikayetlerin linklerini yakalamak için bir değişken oluşturuyoruz. complaint-layer CLASS'ına sahip elementleri bulup bu değişkenin içerisine atıyoruz.
                        markaSikayetLinkleri = driver.find_elements(By.CLASS_NAME,'complaint-layer')
                        
                        # Sayfada bulunan şikayetlerin linklerini almak için döngü oluşturuyoruz.
                        for markaSikayetLinki in markaSikayetLinkleri:
                            # Yakaladığımız şikayetin linkini markaSikayetLinkHref ismindeki değişkene atıyoruz.
                            markaSikayetLinkHref=markaSikayetLinki.get_attribute("href")
                            # Yakaladığımız şikayetin sayısını ve linkini görmek için ekrana yazdırıyoruz.
                            print(f"LINK {sikayetURLsayaci}: ",markaSikayetLinkHref)
                            # Yakaladığımız şikayetleri oluşturduğumuz listenin içerisine atıyoruz.
                            markaLinkleri.append([markaSikayetLinkHref])
                            sikayetURLsayaci+=1
                        # Diğer sayfadaki şikayetler çekmemiz için bir sonraki sayfayı getiriyoruz.
                        driver.get(f"{markaLinki['markaURL']}?page={i}")
                        i+=1
                    except TimeoutException:
                        # Veri boyutu yükseldiği için zaman aşımı hatasıyla karşılaşmamız durumunda ekrana hata mesajını yazdırıyoruz.
                        error_message = f"Zaman aşımı hatası: {markaLinki['markaURL']}?page={i}"
                        print(error_message)
                        # Hata mesajlarını daha sonrasında incelememiz için log_error_to_file() fonksiyonunu kullanarak txt dosyasına kaydediyoruz.
                        log_error_to_file(error_message) # Fonksiyon içeriği 322. Satırda bulunmaktadır.
                        break
                    # Eğer marka linklerinin olduğu liste doluysa verileri CSV dosyasına ekliyoruz.
                    if markaLinkleri:
                        markaLinkleri = list(markaLinkleri)
                        with open('sikayetvar-144-markasal-sikayetler-URL-Listesi.csv', mode='a', encoding='utf-8', newline='') as complaintsFile:
                            # Eğer dosya boşsa ilk satırı dolduruyoruz. Değilse içindeki verilerin üzerine ekliyoruz.
                            writer = csv.writer(complaintsFile)
                            if complaintsFile.tell() == 0:
                                writer.writerow(["Linkler"])
                            writer.writerows(markaLinkleri)
                        # Eklenen şikayet linklerinin sayısını yazdırıyoruz.
                        print(f"{len(markaLinkleri)} adet link dosyaya eklendi.")
                # O anki olan veri sayısını ekrana yazdırıyoruz.
                print("Su anda veri sayisi",len(markaLinkleri))
                print("Çekilen markaların şikayet linkleri = ",markaLinkleri)
                print(markaLinkleri)
                print(len(markaLinkleri))
        except KeyboardInterrupt:
            # Kullanıcı tarafından işlem kesilirse aşağıdaki mesajı ekrana yazdırıyoruz.
            print("İşlem yarıda kesiliyor.")
        except Exception as e:
            # KeyboardInterrupt hatasından farklı bir hata alırsak bu hata mesajını ekrana yazdırıp, fonksiyon ile error_log.txt olarak kaydediyoruz.
            error_message = f"Bir hata oluştu: {e}"
            log_error_to_file(error_message)
            
#startWebdriver()
#bringComplaints()
#complaintsURLsinglePage()
#complaintsURLmultiplePage()
#URLfromBrandSingle()
#URLfromBrandMultiple()
#brandNameList()
#brandLinkList()
#brandPageCounter()
#getComplaintFromBrandURL()
    
driver.close()