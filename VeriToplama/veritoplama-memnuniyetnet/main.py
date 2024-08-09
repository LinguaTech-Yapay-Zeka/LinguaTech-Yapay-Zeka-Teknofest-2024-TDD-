from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import csv

def saveToCSV(data,listLength):
        with open(f'memnuniyetnet-{listLength}-URL-veri.csv',mode='w',newline='',encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow("URL")
            writer.writerows([link] for link in data)

def getMemnuniyetnetLink():
    markalar=[]
    csvKategori=[]
    with open("markalar.csv",mode='r',encoding='utf-8') as file:
        csvreader = csv.reader(file)
        csvKategori = next(csvreader)
        for satirlar in csvreader:
            markalar.append(satirlar)
            
    driver = webdriver.Chrome()
    time.sleep(0.25)
    driver.maximize_window()
    driver.get("https://memnuniyet.net/brands/all/page/1")
    time.sleep(3)
    toplamURL =[]

    elementBekle = 0.05
    for index in range(0,len(markalar)):
        try:
            time.sleep(elementBekle)
            aramaKutusu = driver.find_element(By.ID,"k")
            aramaKutusu.send_keys(markalar[index][1])
            aramaKutusu.send_keys(Keys.RETURN)
            time.sleep(4)
            article = driver.find_elements(By.TAG_NAME,'article')
            if len(article) > 0:
                print(f"Sayfa boş değil {len(article)} adet link var.")
                IDalma = driver.find_element(By.TAG_NAME,"body")
                pgSayac = 0
                for i in range(1,29):
                    IDalma.send_keys(Keys.PAGE_DOWN)
                    if pgSayac % 4 == 0:
                        time.sleep(4)
                    else:
                        time.sleep(0.25)
                    pgSayac+=1
                    
                memnuniyetURLs = driver.find_elements(By.XPATH,"/html/body/div/div[3]/div[1]/article/div[4]/ul/li[1]/a")
                listeURL = []
                sayac = 1
                for singleURL in memnuniyetURLs:
                    print(f"{markalar[index][1]} - URL {sayac}",singleURL.get_attribute("href"))
                    listeURL.append(singleURL.get_attribute("href"))
                    time.sleep(0.25)
                    sayac+=1
                print(listeURL)

                print("Sitede bulunan linkler")
                print(len(listeURL))

                print("Tekrar eden veriler silindikten sonra oluşturulan yeni liste")
                # Tekrar eden elemanları teke düşürmek için
                listeURL = list(set(listeURL))
                # -----------------------------------------
                for listeElemani in listeURL:
                    toplamURL.append(listeElemani)
                print(len(listeURL))   
            else:
                print("Sayfada Article yok. Bir sonraki markaya geçiyor...")
        except NoSuchElementException:
            print("Element bulunamadi. Bekleme süresi arttırılıyor.")
            elementBekle+=0.10
        except KeyboardInterrupt:
            print("İşlem yarıda kesiliyor. Veriler kaydedildikten sonra program kapanacak.")
            time.sleep(2)
            break
        except Exception as e:
            file = open("Exceptions.txt",mode="a")
            file.write(f"Hata mesajı : {e}")
            file.close()
        
    saveToCSV(toplamURL,len(toplamURL))
            
    print(f"Toplanan link sayısı : {len(toplamURL)}")
    
def getMemnuniyetler():
    """link = "https://memnuniyet.net/turk-telekom-2020"
    driver.get(link)
    time.sleep(2)
    memnuniyet = driver.find_element(By.CSS_SELECTOR,"#Post > article:nth-child(1) > div:nth-child(4)")
    print(memnuniyet.text)
    exit()"""
    
    driver = webdriver.Chrome()
    driver.maximize_window()

    # Veri çekmenin ortalarında hata olması durumunda nerede kalındıysa ordan devam edilmesi için yazıldı. En baştan başlanacaksa 0 değeri verilmeli.
    skipRows = 7
    with open('memnuniyetnet-15135-URL-veri.csv',mode='r',newline='',encoding='utf-8') as urlFile:
        readCSV = csv.DictReader(urlFile)
        with open('memnuniyet-icerikleri.csv',mode='a',encoding='utf-8',newline='') as memnuniyetFile:
            writer = csv.writer(memnuniyetFile)
            if memnuniyetFile.tell() == 0:
                writer.writerow(["Memnuniyetler"])
                
            for current_row,MemnuniyetIcerigi in enumerate(readCSV):
                writer = csv.writer(memnuniyetFile,quoting=csv.QUOTE_ALL)
                if current_row == 5000:
                    print("Belirlenen değere ulaştığı için döngüden çıkılıyor.")
                    break
                try:
                    if current_row < skipRows:
                        continue 
                    
                    # SkipRows değişkeninde verilen değerden itibaren verileri işlemeye başla
                    print(MemnuniyetIcerigi['URL'])
                    driver.get(MemnuniyetIcerigi['URL'])
                    time.sleep(2)
                    memnuniyet = driver.find_element(By.XPATH,'//*[@id="Post"]/article[1]/div[3]')
                    print(f"{current_row+1}-) {memnuniyet.text}")
                    writer.writerow([memnuniyet.text])
                except KeyboardInterrupt:
                    print("İşlem yarıda kesiliyor. Veriler kaydedildikten sonra program kapanacak.")
                    time.sleep(5)
                    exit()
                except Exception as e:
                    file = open("Exceptions.txt",mode="a",encoding='utf-8')
                    file.write(f"Hata mesajı : {e}")
                    file.close()


#getMemnuniyetnetLink()
getMemnuniyetler()