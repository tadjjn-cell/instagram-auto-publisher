# دليل الإعداد — Instagram Auto Publisher

> صافط الفيديو ديالك لـ Saved Messages فـ Telegram مع caption كتبدا بـ `ig:` (مثلا `ig: 5 نصائح للطبخ`)، والبوت كيدير الباقي: trending research، كتابة caption + hashtags بالذكاء الاصطناعي، ونشر الفيديو كـ Reel على Instagram تلقائياً. كلشي **مجاني**، كيخدم على GitHub Actions بلا PC.

---

## ⚠️ فرق تقني مهم: كيفاش كيتنشر الفيديو

خلاف YouTube وTikTok (upload مباشر بالـ bytes)، Instagram Graph API كيطلب **رابط عمومي** للفيديو (video_url) وهو اللي كيجيبو بنفسو. الحل:
1. الفيديو كيتصيفط مؤقتاً كـ **GitHub Release asset** (رابط عمومي، مجاني، فـ نفس repo)
2. Instagram كيجيب الفيديو من هاداك الرابط، كيبروسيسيه، كينشرو
3. من بعد النشر، الـ release كيتمسح أوتوماتيكياً (cleanup)

هادشي كيتطلب الـ **repo يكون public** (bحال ما درنا لـ YouTube channel 1، بش GitHub Pages تخدم).

---

## الخطوة 1: تأكد Instagram professional + مربوط بـ Facebook Page

1. الحساب ديال Instagram خاصو يكون **Professional** (Business أو Creator) — من Instagram app: Settings > Account type
2. خاصو يكون مربوط بـ **Facebook Page** (من نفس الإعدادات، "Linked accounts" أو من Meta Business Suite)

---

## الخطوة 2: Meta App

1. [developers.facebook.com](https://developers.facebook.com) > **My Apps** > **Create App**
2. اختر نوع "Business"
3. زيد product: **Instagram** (Instagram API / Instagram Graph API)
4. فـ App Settings > Basic: احتافظ بـ **App ID** و **App Secret**
5. زيد **Valid OAuth Redirect URI** — نقدرو نستعملو نفس GitHub Pages links اللي درنا لـ YouTube (`https://tadjjn-cell.github.io/...`) أو أي URL عمومي آخر
6. **App Roles > Roles**: زيد نفسك كـ Admin/Developer (بش تقدر تستعمل الـ API بحساب ديالك بلا App Review كامل)

---

## الخطوة 3: جيب Access Token

```bash
python -m pip install -r setup/requirements.txt
python setup/get_instagram_token.py
```

غادي يطلب App ID / App Secret / Redirect URI، يحل رابط فـ browser، تدخل بـ Facebook، تعطي الصلاحية، تنسخ الرابط المُوجَّه (redirected). من بعد كيختار ليك الـ Facebook Page، وكيطبع:

```
IG_ACCESS_TOKEN=...
IG_USER_ID=...
```

**ملاحظة**: هاد التوكن كيخدم ~60 يوم. خاصك تعاود هاد السكريبت من قبل ما ينتهي (تحديث يدوي كل شهرين تقريباً).

---

## الخطوة 4: Telegram (نفس compte)

نسخ `TELEGRAM_API_ID` / `TELEGRAM_API_HASH` / `TELEGRAM_SESSION` من `.env` ديال YouTube project.

---

## الخطوة 5: GitHub Repo (خاصو يكون Public) + Secrets

1. `git init && git add . && git commit -m "Initial commit"`
2. دير repo جديد **Public** فـ GitHub (خاصو يكون public بش video asset يكون فيتشابل من Instagram)
3. Push
4. **Settings > Actions > General > Workflow permissions** → "Read and write permissions" → Save
5. زيد secrets:

| Secret |
|---|
| `GROQ_API_KEY` |
| `TELEGRAM_API_ID` |
| `TELEGRAM_API_HASH` |
| `TELEGRAM_SESSION` |
| `TELEGRAM_SOURCE_CHAT` (= `me`) |
| `IG_ACCESS_TOKEN` |
| `IG_USER_ID` |

**ملاحظة**: `GITHUB_TOKEN` ما خاصكش تزيدو يدوياً — GitHub كيعطيه أوتوماتيكياً لكل workflow.

---

## الخطوة 6: جرب

صيفط فيديو (vertical) + caption `ig: <الموضوع>` لـ Saved Messages. شغل الـ workflow يدوياً من Actions tab. Reel غادي يبان فـ Instagram دياك بعد شي دقايق (processing).
