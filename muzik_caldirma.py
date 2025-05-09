import cv2
import mediapipe as mp
import numpy as np
import os
import time
from pygame import mixer
from deepface import DeepFace


# MediaPipe el tanima modulunu baslat
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5)

# Pygame ses modulunu baslat
mixer.init()

# Duygu cevirisi sozlugu
duygu_cevirisi = {
    "angry": "Kizgin",
    "disgust": "Tiksinti",
    "fear": "Korku",
    "happy": "Mutlu",
    "sad": "Uzgun",
    "surprise": "Saskin",
    "neutral": "Notr"
}

# Muzik dosyalarini al ve kullanilabilir olanlari tespit et
all_music_files = [file for file in os.listdir() if file.endswith(".mp3")]
all_music_files.sort() # Dosyalari sirala

# Kullanilabilir muzik dosyalarini kontrol et
music_files = []
sounds = []  # Sound nesnelerini saklamak icin liste

print("Muzik dosyalari kontrol ediliyor...")
for file in all_music_files:
    try:
        sound = mixer.Sound(file)
        sounds.append(sound)
        music_files.append(file)
        print(f"Basariyla yuklendi: {file}")
    except Exception as e:
        print(f"Yuklenemedi: {file}, Hata: {e}")

if not music_files:
    print("Hicbir muzik dosyasi yuklenemedi! Programi kapatiyorum.")
    exit()

print(f"Yuklenen muzik dosyalari: {music_files}")

current_sound = None
current_music_index = -1
is_playing = False
volume = 0.5  # 0.0 ile 1.0 arasi
music_paused_by_smile = False  # Gulumse nedeniyle muzik durduruldu mu

# Kamerayi baslat
cap = cv2.VideoCapture(0)

def count_fingers(hand_landmarks):
    """Kaldirilan parmak sayisini dondurur"""
    finger_tips = [8, 12, 16, 20]  # Indeks, orta, yuzuk ve serce parmak uclari
    thumb_tip = 4
    
    # Basparmak icin kontrol (x-koordinat farki)
    thumb_up = hand_landmarks.landmark[thumb_tip].x < hand_landmarks.landmark[thumb_tip - 1].x
    
    # Diger parmaklar icin kontrol (y-koordinat farki)
    count = sum(1 for tip in finger_tips if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y)
    
    # Basparmak kaldirildiysa ekle
    if thumb_up:
        count += 1
        
    return count

def get_thumb_index_distance(hand_landmarks):
    """Basparmak ve isaret parmagi arasindaki mesafeyi hesaplar"""
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    
    # 3D mesafeyi hesapla
    distance = np.sqrt((thumb_tip.x - index_tip.x)**2 + 
                       (thumb_tip.y - index_tip.y)**2 + 
                       (thumb_tip.z - index_tip.z)**2)
    return distance

# Son islem zamanini sakla (titresimleri onlemek icin)
last_action_time = time.time()
last_emotion_check_time = time.time()
action_delay = 1.0  # saniye
emotion_check_delay = 1.0  # saniye (duygu kontrolu icin gecikme)

# Gulumse durum degiskenlerini ekliyoruz
is_smiling = False
dominant_emotion = "unknown"
smile_start_time = 0
display_smile_message = False
smile_display_duration = 3.0  # Gulumse mesajinin gosterilme suresi (saniye)

try:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Kamera goruntusu alinamadi")
            continue

        # Goruntuyu BGR'den RGB'ye donustur
        image = cv2.flip(image, 1)  # Ayna goruntusu icin cevir
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # El algilama islemini yap
        results = hands.process(image_rgb)
        
        current_time = time.time()
        
        # DeepFace ile duygu analizi yap (her frame degil, belirli araliklarla)
        if current_time - last_emotion_check_time > emotion_check_delay:
            try:
                # DeepFace ile duygu analizi
                analysis = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)
                
                # Analiz sonuclarini isle
                if analysis and len(analysis) > 0:
                    emotions = analysis[0]['emotion']
                    prev_dominant_emotion = dominant_emotion
                    dominant_emotion = max(emotions, key=emotions.get)
                    
                    # Gulumse kontrolu
                    was_smiling = is_smiling
                    is_smiling = dominant_emotion == 'happy' and emotions['happy'] > 80  # %80'den fazla mutluluk algilandiginda
                    
                    # Yeni bir gulumse basladiysa
                    if is_smiling and not was_smiling:
                        smile_start_time = current_time
                        display_smile_message = True
                    
                    # Duygu degistiginde ve onceki durum gulumse idiyse mesaji kapat
                    if dominant_emotion != prev_dominant_emotion and prev_dominant_emotion == 'happy':
                        display_smile_message = False
                
                last_emotion_check_time = current_time
            except Exception as e:
                print(f"Duygu analizi hatasi: {e}")
        
        # Gulumse mesajini goster (sadece gulumse algilandiginda ve gulumse devam ettigi surece)
        if is_smiling or (display_smile_message and current_time - smile_start_time < smile_display_duration):
            cv2.putText(image, "GULUMSEME ALGILANDI", (50, 250),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 255, 255), 2)
        
        # Gulumse algilandiginda muzigi durdur
        if is_smiling and is_playing:
            if current_sound:
                current_sound.stop()
                is_playing = False
                music_paused_by_smile = True
                print("Gulumseme algilandi!")
        
        # Elleri isaretle ve kontrol et
        right_hand = None  # Kamera goruntusunde sol el (gercekte sag el)
        left_hand = None   # Kamera goruntusunde sag el (gercekte sol el)
        
        if results.multi_hand_landmarks:
            for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                # Eli gorsellestir
                mp_drawing.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                # Elin hangi el oldugunu belirle
                if results.multi_handedness:
                    handedness = results.multi_handedness[idx].classification[0].label
                    
                    if handedness == "Left":  # Kamera goruntusunde sol, gercekte sag el
                        right_hand = hand_landmarks
                    elif handedness == "Right":  # Kamera goruntusunde sag, gercekte sol el
                        left_hand = hand_landmarks
                    
                    # El tipini ekranda goster
                    x_base = int(hand_landmarks.landmark[0].x * image.shape[1])
                    y_base = int(hand_landmarks.landmark[0].y * image.shape[0])
                    cv2.putText(image, f"{handedness}", (x_base - 10, y_base - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Sag el (kamerada sol) parmak sayisini kontrol et - Muzik secimi icin
        if right_hand:
            finger_count = count_fingers(right_hand)
            cv2.putText(image, f"Parmak: {finger_count}", (50, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            
            # Parmak sayisina gore muzik sec ve cal (fazla hizli degisimi onlemek icin delay ekledik)
            if current_time - last_action_time > action_delay:
                music_idx = finger_count - 1  # 0-4 arasi indeks icin
                
                if 0 <= music_idx < len(music_files):
                    if music_idx != current_music_index or music_paused_by_smile:
                        # Mevcut calan muzigi durdur
                        if current_sound:
                            current_sound.stop()
                        
                        print(f"Calinan muzik: {music_files[music_idx]}")
                        current_sound = sounds[music_idx]
                        current_sound.play(-1)  # -1 parametresi surekli tekrari saglar
                        current_sound.set_volume(volume)  # Mevcut ses seviyesini ayarla
                        is_playing = True
                        current_music_index = music_idx
                        music_paused_by_smile = False  # Parmak gosterildi, gulumse durumu sifirlandi
                        
                    last_action_time = current_time
        
        # Sol el (kamerada sag) basparmak-isaret parmagi mesafesi - Ses kontrolu icin
        if left_hand:
            distance = get_thumb_index_distance(left_hand)
            
            # Mesafeyi ses seviyesine donustur (0.0-1.0 arasi)
            # Mesafenin 0.03-0.2 arasinda degisecegini varsayarak
            normalized_volume = np.clip((distance - 0.03) / 0.17, 0.0, 1.0)
            
            # Ses seviyesini guncelle
            volume = normalized_volume
            if current_sound and is_playing:
                current_sound.set_volume(volume)
            
            # Ses seviyesini gorsellestir
            bar_length = int(volume * 400)
            cv2.rectangle(image, (50, 100), (50 + bar_length, 130), (0, 255, 0), -1)
            cv2.rectangle(image, (50, 100), (450, 130), (255, 255, 255), 2)
            cv2.putText(image, f"Ses: {int(volume * 100)}%", (50, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        # Mevcut calan muzigi goster
        if current_music_index >= 0:
            music_name = music_files[current_music_index]
            status = "Caliyor" if is_playing else "Durakladi (Gulumseme Nedeniyle)"
            cv2.putText(image, f"Muzik: {music_name} - {status}", (50, 170),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
 
        # Sonuclari goster
        cv2.imshow('El Hareketleri ve Gulumseme ile Muzik Kontrolu', image)
        
        # ESC tusuna basilirsa cik
        if cv2.waitKey(5) & 0xFF == 27:
            break
except Exception as e:
    print(f"Bir hata olustu: {e}")
finally:
    # Kaynaklari serbest birak
    print("Program kapatiliyor...")
    if current_sound:
        current_sound.stop()
    hands.close()
    cap.release()
    cv2.destroyAllWindows()
    mixer.quit()
    print("Program basariyla kapatildi.")