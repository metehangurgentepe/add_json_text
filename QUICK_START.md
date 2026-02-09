# 🚀 Hızlı Başlangıç

## ✅ Güncel Durum (19 Ocak 2026)

Tüm hatalar düzeltildi! ✅
- Button form artık tüm değerleri düzgün alıyor
- Training data hem dosyaya hem Supabase'e kaydediliyor
- **YENİ**: Training data artık Supabase ID=1 kaydının **SONUNA APPEND** ediliyor (REPLACE değil!)

## Başlat

```bash
go run main.go
```

Tarayıcıda aç: **http://localhost:8080**

## 📝 Kullanım Adımları

### 0️⃣ Mevcut Dosyayı Yükle (İlk Kurulum)

Eğer `niobe_training.txt` dosyanız zaten varsa:

**[📤 niobe_training.txt'i Supabase'e Yükle]** ← Sayfanın üstündeki bu butona tıkla

✅ Tüm training data `ai_log.instructions` tablosuna yüklenir!

### 1️⃣ Training Data Ekle

```
Input: Evde Bakım
Description: Evde bakım modülüne gitmek için aşağıdaki butona tıklayınız.
Action Key: [🎲 UUID Oluştur] → 4a881122
```

**[➕ Training Data Ekle]** →

Kaydetme seçenekleri:
- **[📄 Sadece Dosyaya Kaydet]** → Sadece `niobe_training.txt` dosyasına ekler
- **[💾 Dosyaya + Supabase'e Kaydet]** → Hem dosyaya hem `ai_log.instructions` tablosuna ekler (önerilir!)

### 2️⃣ Button Oluştur

**[⬇️ Bu ID ile Button Oluştur]** ← Bu butona tıkla, Action Key otomatik gelir!

```
Button Title: Evde Bakım
Action Type: route
Navigation Type: push
Action Value: /form/97
Button ID: 4a881122 ← Otomatik geldi!
Order: 0
```

**[✅ Button Ekle]** → **[💾 Supabase'e Kaydet]**

## ✨ Özellikler

- 📤 **Toplu yükleme** - Mevcut niobe_training.txt dosyasını tek tıkla Supabase'e yükle
- 🎲 **Otomatik UUID** oluşturma
- 🔗 **Action Key aktarma** (Training → Button)
- 💾 **Direkt Supabase** kaydetme (SSL güvenli)
- 📋 **SQL kopyalama** alternatifi
- 📥 **Toplu export** özelliği

## 🎯 Sonuç

✅ Training data → `niobe_training.txt` (dosya) ve/veya `ai_log.instructions` (Supabase)
✅ Button → `public.button` tablosu (Supabase)

**Her şey direkt veritabanına kaydediliyor!** 🚀

## 💡 İpuçları

- **"Dosyaya + Supabase'e Kaydet"** kullanın - Her iki yeri de senkronize eder! ⭐
- İlk kurulumda mevcut dosyayı yüklemek için üstteki toplu yükleme butonunu kullanın
- Yeni training data eklerken "Dosyaya + Supabase'e Kaydet" kullanın
- Action Key otomatik oluşturulur ve button formuna aktarılır
- Button'lar direkt `public.button` tablosuna eklenir
- Tüm işlemler SSL güvenli

Tek seferde hem AI eğitim verisi hem de button oluşturursun! 🎉
