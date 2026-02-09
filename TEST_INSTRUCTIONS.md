# 🧪 Test İnstructions - Son Değişiklikler

## ✅ Yapılan Düzeltmeler

### 1. Button Form Empty Data Hatası Düzeltildi
**Problem**: Button formu submit edildiğinde tüm değerler boş geliyordu.

**Çözüm**:
- `main.go`'da `addButtonHandler` fonksiyonunu tamamen yeniden yazdık
- Multipart form parsing'i düzelttik
- Kapsamlı debug logging ekledik
- Form field'larını doğrudan okumak için `r.FormValue()` kullanımını iyileştirdik

**Kod Değişiklikleri**: [main.go:78-152](main.go#L78-L152)

### 2. Training Data Dosya + Supabase Senkronizasyonu
**Problem**: Training data eklenirken sadece Supabase'e gidiyordu, `niobe_training.txt` dosyasına eklenmi yordu.

**Çözüm**:
- `saveTrainingToSupabaseHandler` fonksiyonunu güncelledik (lines 384-448)
- Şimdi önce dosyaya append ediyor
- Sonra tüm dosyayı okuyup Supabase'e UPDATE ediyor (ID=1)

**Workflow**:
```
1. Training data oluştur → currentTrainingText
2. "Dosyaya + Supabase'e Kaydet" butonuna tıkla
3. ✅ niobe_training.txt'ye append edilir
4. ✅ Dosya okunur ve ai_log.instructions (ID=1) UPDATE edilir
```

## 🧪 Test Adımları

### Test 1: Button Form (Boş Data Hatası)

1. **Tarayıcıda aç**: http://localhost:8080

2. **Button Form doldur**:
   ```
   Button Title: Test Button
   Action Type: route
   Navigation Type: push
   Action Value: /form/999
   Button ID: test1234
   Order: 0
   ```

3. **"✅ Button Ekle" butonuna tıkla**

4. **Kontrol Et**:
   - ✅ Sayfada button card'ı görünmeli
   - ✅ Tüm değerler doğru görünmeli (boş değil!)
   - ✅ SQL çıktısında doğru INSERT sorgusu olmalı

5. **Terminal loglarını kontrol et**:
   ```bash
   tail -f /tmp/go_server_latest.log
   ```

   Görmek istediğimiz:
   ```
   === Button Form Submission ===
   Content-Type: multipart/form-data; boundary=...
   Parsed values: id="test1234", title="Test Button", action_type="route", ...
   Final button object: {ID:test1234 Title:Test Button ...}
   === End Button Form ===
   ```

6. **"💾 Supabase'e Kaydet" butonuna tıkla**
   - Supabase `public.button` tablosunda yeni kaydı kontrol et

---

### Test 2: Training Data File + Supabase Sync

1. **Training Data Form doldur**:
   ```
   Input Text: Test Input
   Description: Bu bir test açıklamasıdır.
   Action Key: [🎲 UUID Oluştur] → testkey1
   ```

2. **"➕ Training Data Ekle" butonuna tıkla**
   - Training data çıktısı görünmeli

3. **"💾 Dosyaya + Supabase'e Kaydet" butonuna tıkla**

4. **Kontrol Et**:

   a) **Dosyayı kontrol et**:
   ```bash
   tail -5 niobe_training.txt
   ```
   Son satırda yeni eklenen data olmalı:
   ```
   input: Test Input
   output: {"description": "Bu bir test açıklamasıdır.", "actionKey": "testkey1"}
   ```

   b) **Supabase'i kontrol et**:
   ```sql
   SELECT id, LEFT(instructions, 100)
   FROM ai_log.instructions
   WHERE id = 1;
   ```
   `instructions` column'u tüm dosya içeriğini içermeli (203+ satır)

5. **Terminal loglarını kontrol et**:
   ```bash
   tail -f /tmp/go_server_latest.log
   ```

   Görmek istediğimiz:
   ```
   Uploading to Supabase, content length: XXXX bytes
   PATCH response status: 200
   Successfully updated instructions record
   ```

---

### Test 3: Tam Workflow (Training → Button)

1. **Training Data oluştur**:
   ```
   Input: Evde Bakım
   Description: Evde bakım modülüne gitmek için aşağıdaki butona tıklayınız.
   Action Key: [🎲 UUID Oluştur] → 4a881122
   ```

2. **"➕ Training Data Ekle" → "💾 Dosyaya + Supabase'e Kaydet"**

3. **"⬇️ Bu ID ile Button Oluştur" butonuna tıkla**
   - Button formuna `4a881122` ID'si otomatik gelmeli
   - Field sarı highlight olmalı

4. **Button bilgilerini doldur**:
   ```
   Button Title: Evde Bakım
   Action Type: route
   Navigation Type: push
   Action Value: /form/97
   Button ID: 4a881122 (otomatik geldi!)
   Order: 0
   ```

5. **"✅ Button Ekle" → "💾 Supabase'e Kaydet"**

6. **Sonuç Kontrol**:
   - ✅ `niobe_training.txt`: Yeni training data eklenmiş olmalı
   - ✅ `ai_log.instructions` (ID=1): Güncellenmiş tüm content
   - ✅ `public.button`: Yeni button kaydı `4a881122` ID'si ile

---

## 📊 Beklenen Davranışlar

### Button Form
- ❌ **Önce**: `Form values received: map[]` (boş)
- ✅ **Şimdi**: Tüm değerler dolu gelir

### Training Data
- ❌ **Önce**: Sadece Supabase'e gidiyordu
- ✅ **Şimdi**: Hem dosyaya append, hem Supabase'e UPDATE

### Supabase ai_log.instructions
- Strategi: **REPLACE** (tüm dosya içeriğini ID=1'e yaz)
- Her yeni training data eklendiğinde:
  1. `niobe_training.txt`'ye append
  2. Dosyanın tümü okunur
  3. `ai_log.instructions` ID=1 UPDATE edilir

## 🐛 Hata Durumunda Debug

### Button boş geliyor:
```bash
# Server loglarını izle
tail -f /tmp/go_server_latest.log

# Şunu görmek istiyoruz:
=== Button Form Submission ===
Content-Type: multipart/form-data; boundary=...
r.Form (combined): map[action_type:[route] action_value:[/form/999] ...]
Parsed values: id="xxx", title="xxx", ...
```

### Training data dosyaya eklenmiyor:
```bash
# Dosya izinlerini kontrol et
ls -la niobe_training.txt

# Olması gereken: -rw-r--r--
# Eğer yazma izni yoksa:
chmod 644 niobe_training.txt
```

### Supabase bağlantı hatası:
```bash
# SSL bypass doğru çalışıyor mu kontrol et
# Logda görmek istediğimiz:
PATCH response status: 200
Successfully updated instructions record

# Eğer 404 / 42P01 hatası varsa:
# - Schema headers doğru: Accept-Profile: ai_log
# - Content-Profile: ai_log
```

## 📝 Notlar

- Tüm SSL certificate errors bypass edilmiş (`InsecureSkipVerify: true`)
- Enum field'lar (action_type, navigation_type) sadece boş değilse Supabase'e gönderiliyor
- Training data dosya işlemleri append mode (`os.O_APPEND`)
- Supabase instructions ID=1 stratejisi: Tek bir kayıt, sürekli UPDATE

## 🚀 Sonraki Adımlar (Opsiyonel)

Eğer hala sorun varsa:
1. Tarayıcı dev tools console'u kontrol et (F12)
2. Network tab'ında `/add-button` request'i incele
3. Request Payload'da form data var mı kontrol et
4. Server loglarında debug output'u oku
