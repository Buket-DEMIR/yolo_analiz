import cv2
import os
from ultralytics import YOLO

print(">>> Program baslatiliyor, lütfen bekleyin...")

# Bilgisayarında hazır olan güçlü YOLO modelini kullanıyoruz
model = YOLO("yolo26l.pt")

video_yolu = "WhatsApp Video 2026-06-26 at 02.22.54.mp4"
cikti_yolu = "analiz_cinsiyet_ve_yas.avi"

if not os.path.exists(video_yolu):
    print(f"Uyarı: '{video_yolu}' bulunamadı. Sunucu aktif tutuluyor...")
    import time
    while True:
        time.sleep(3600)

cap = cv2.VideoCapture(video_yolu)
width  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps    = int(cap.get(cv2.CAP_PROP_FPS))

fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter(cikti_yolu, fourcc, fps, (width, height))

print(">>> Video açıldı. Düzeltilmiş Cinsiyet ve Yaş Analizi Başlıyor...")

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_count += 1
    
    # Modelin tüm nesneleri analiz etmesini sağlıyoruz
    results = model(frame, verbose=False)
    
    insanlar = []
    kadin_isaretleri = 0
    erkek_isaretleri = 0
    genc_isaretleri = 0   
    yetiskin_isaretleri = 0 
    
    for result in results:
        boxes = result.boxes
        for box in boxes:
            cls_id = int(box.cls[0])
            label = model.names[cls_id].lower()
            
            if cls_id == 0:
                insanlar.append(box)
            
            # Cinsiyet ipuçları
            if label in ["handbag", "skirt", "dress", "hair dryer"]:
                kadin_isaretleri += 1
            if label in ["tie", "necktie", "razor"]:
                erkek_isaretleri += 1
                
            # Yaş ipuçları
            if label in ["backpack", "sports ball", "skateboard"]:
                genc_isaretleri += 1
            if label in ["suitcase", "tie", "necktie"]:
                yetiskin_isaretleri += 1

    for box in insanlar:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        conf = float(box.conf[0])
        
        en = x2 - x1
        boy = y2 - y1
        oran = en / boy if boy > 0 else 0
        
        # 1. CİNSİYET KARARI (Hatalı kısım düzeltildi)
        if kadin_isaretleri > 0 or erkek_isaretleri > 0:
            if kadin_isaretleri > erkek_isaretleri:
                cinsiyet_yazisi = "Kadin"
            else:
                cinsiyet_yazisi = "Erkek"
        else:
            cinsiyet_yazisi = "Erkek" if oran > 0.40 else "Kadin"
            
        # 2. YAŞ KARARI
        if genc_isaretleri > yetiskin_isaretleri:
            yas_yazisi = "Genc (18-25)"
        elif yetiskin_isaretleri > genc_isaretleri:
            yas_yazisi = "Yetiskin (26-45)"
        else:
            if boy < height * 0.35: 
                yas_yazisi = "Cocuk/Genc"
            elif boy > height * 0.70:
                yas_yazisi = "Yetiskin (26-45)"
            else:
                yas_yazisi = "Genc (18-25)"

        # Çizim ve Etiketleme
        etiket = f"{cinsiyet_yazisi} | {yas_yazisi}"
        
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 165), 2) 
        cv2.rectangle(frame, (x1, y1 - 30), (x1 + 220, y1), (255, 0, 165), -1)
        cv2.putText(frame, etiket, (x1 + 5, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    out.write(frame)
    
    if frame_count % 10 == 0:
        print(f"İşlenen Kare Sayısı: {frame_count}")

cap.release()
out.release()
cv2.destroyAllWindows()

print(f"\n>>> Düzeltme başarılı! Çıktı '{cikti_yolu}' adıyla kaydedildi.")