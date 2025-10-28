# Tech for Good: Co programista może zrobić dla slumsów?

## Kilka godzin tygodniowo może zmienić życie tysięcy ludzi

**Data**: 26 października 2025

---

## 🎯 TL;DR - Szybki przegląd

Jako programista z **2-5 godzinami tygodniowo** możesz:

1. **Zbudować aplikację mobilną** zbierającą dane o potrzebach rodzin (2-3 miesiące)
2. **Stworzyć system zarządzania beneficjentami** dla NGO (1-2 miesiące)
3. **Mapowanie slumsów** - web app z OpenStreetMap (3-4 tygodnie)
4. **Fundraising platform** - strona do zbiórek (2-3 tygodnie)
5. **AI do analizy zdjęć** - wykrywanie niedożywienia (zaawansowane, 3-6 miesięcy)
6. **Dashboard do monitoringu** - wizualizacja danych projektu (1 miesiąc)

**Impact**: Każdy z tych projektów może zwiększyć efektywność pomocy o 30-50% i pomóc dotrzeć do 2-3x więcej rodzin.

---

## 💡 PROJEKTY TECH - OD NAJPROSTSZYCH DO NAJBARDZIEJ ZAAWANSOWANYCH

---

## 🟢 POZIOM 1: PODSTAWOWY (2-10 godzin)

### 1.1 Strona WWW projektu

**Co**: Landing page dla "Slumsy nie takie straszne"

**Stack**: HTML/CSS/JS, React, Next.js, lub Gatsby

**Funkcje:**
- O projekcie
- Jak pomóc
- Formularz kontaktowy
- Blog (markdown)
- Zbiórki (integracja Stripe/PayPal)

**Czas**: 5-10 godzin

**Impact**: Zwiększa wiarygodność, ułatwia fundraising

**Repo template**: [GitHub - charity-website-template](https://github.com/search?q=charity+website+template)

---

### 1.2 Automatyzacja social media

**Co**: Bot postujący success stories na Instagram/Facebook/Twitter

**Stack**: Python + APIs (Instagram Graph API, Facebook Graph API)

**Funkcje:**
- Scheduled posts
- Hashtagowanie automatyczne
- Cross-posting na multiple platformy
- Analytics

**Czas**: 3-5 godzin

**Impact**: Zwiększa reach o 300%, oszczędza 5h/tydzień dla zespołu

**Przykładowy kod**:
```python
# Instagram bot (używając instabot library)
from instabot import Bot
import schedule

bot = Bot()
bot.login(username="slumsynietakiestraszne", password="xxx")

def post_success_story():
    bot.upload_photo("success_story_001.jpg", 
                     caption="Meet Jane from Kibera... #slumsproject #kenya")

schedule.every().monday.at("10:00").do(post_success_story)
```

---

### 1.3 Email newsletter automation

**Co**: Automatyczne newslettery dla donorów

**Stack**: Mailchimp API lub SendGrid + Python/Node.js

**Funkcje:**
- Segmentacja (donor size, frequency)
- Automated thank you emails
- Monthly impact reports
- Donation receipts (tax)

**Czas**: 3-5 godzin

**Impact**: Zwiększa donor retention o 40%

---

## 🟡 POZIOM 2: ŚREDNI (10-40 godzin)

### 2.1 Beneficiary Management System (BMS)

**Co**: System do zarządzania beneficjentami projektu

**Stack**: 
- **Backend**: Node.js + Express + MongoDB / PostgreSQL
- **Frontend**: React / Vue.js
- **Hosting**: Heroku (free tier) / Railway / Fly.io

**Funkcje:**

**CRUD dla rodzin:**
- Dane demograficzne (imię, wiek, liczba dzieci)
- Lokalizacja (GPS coordinates)
- Status (active, graduated, inactive)
- Historia interwencji

**Dashboard:**
- Liczba beneficjentów
- Mapa rozmieszczenia
- Statystyki (wiek, wielkość rodziny)
- Filtry i wyszukiwanie

**Reporting:**
- Export do Excel/CSV
- Generowanie raportów dla donorów
- KPIs tracking

**Mobile-first** - Community Health Workers używają na telefonach

**Czas**: 20-40 godzin

**Impact**: 
- Oszczędza 10-15h/tydzień papierkowej roboty
- Eliminuje duplikaty
- Umożliwia data-driven decisions

**Tech spec**:
```javascript
// MongoDB Schema
const FamilySchema = new Schema({
  familyId: { type: String, unique: true },
  headOfHousehold: String,
  members: [{
    name: String,
    age: Number,
    gender: String,
    school: Boolean
  }],
  location: {
    type: { type: String, default: 'Point' },
    coordinates: [Number] // [longitude, latitude]
  },
  interventions: [{
    type: { type: String, enum: ['health', 'education', 'food', 'microcredit'] },
    date: Date,
    description: String,
    cost: Number
  }],
  status: { type: String, enum: ['active', 'graduated', 'inactive'] },
  createdAt: { type: Date, default: Date.now }
});
```

**Open source inspo**: 
- [OpenMRS](https://github.com/openmrs) - medical records
- [CommCare](https://www.dimagi.com/commcare/) - case management

---

### 2.2 Data Collection Mobile App

**Co**: Aplikacja dla Community Health Workers do zbierania danych

**Stack**: 
- **React Native** (iOS + Android z jednego kodu)
- **Expo** (szybki development)
- **SQLite** (offline storage)
- **Backend API** (sync gdy online)

**Funkcje:**

**Offline-first:**
- Działa bez internetu (slumsy = słaby internet)
- Synchronizuje gdy dostępny WiFi

**Formularze:**
- Rejestracja nowej rodziny
- Health check-up (waga dzieci, symptomy)
- Education tracking (czy dziecko chodzi do szkoły)
- Distribution log (paczki żywnościowe, leki)

**Zdjęcia:**
- Przed/po (mieszkanie, dzieci)
- Auto-upload z kompresją

**GPS:**
- Auto-tracking lokalizacji wizyty
- Mapping na mapie

**Czas**: 30-50 godzin

**Impact**: 
- CHWs mogą odwiedzić 2x więcej rodzin dziennie
- 95% redukcja błędów w danych (no paperwork)
- Real-time visibility dla managementu

**Przykładowy screen**:
```
┌─────────────────────────┐
│ New Family Visit        │
├─────────────────────────┤
│ Head of Household:      │
│ [_______________]       │
│                         │
│ Number of children:     │
│ [▼ Select]              │
│                         │
│ GPS: ✓ Location saved   │
│                         │
│ [📷 Take Photo]         │
│                         │
│ Health Check:           │
│ □ Malaria symptoms      │
│ □ Malnutrition signs    │
│ □ Other (specify)       │
│                         │
│ [Save (offline)] [Sync] │
└─────────────────────────┘
```

**Open source base**: 
- [ODK Collect](https://github.com/getodk/collect) - data collection
- Można zforkować i dostosować

---

### 2.3 Interactive Slum Map

**Co**: Mapa Kibery z oznaczonymi zasobami i potrzebami

**Stack**:
- **Leaflet.js** lub **Mapbox GL**
- **OpenStreetMap** data
- **Backend**: API z danymi o lokalizacjach

**Funkcje:**

**Layers:**
- 📍 Punkty wody
- 🚽 Toalety publiczne
- 🏥 Kliniki/health posts
- 🏫 Szkoły (formalne/nieformalne)
- 🏠 Beneficjenci projektu
- ⚠️ Areas of high need

**Interaktywność:**
- Click na marker → info window
- Filtry (show only water points)
- Heatmap (poverty density)
- Routing (shortest path to resource)

**Crowdsourcing:**
- Mieszkańcy mogą zgłaszać nowe zasoby/problemy
- Moderacja przed publikacją

**Czas**: 15-25 godzin

**Impact**:
- CHWs wiedzą gdzie są zasoby
- Nowi beneficjenci łatwiej znajdują pomoc
- Planowanie interwencji (gdzie brakuje wody?)

**Demo code**:
```javascript
// Leaflet.js + OpenStreetMap
const map = L.map('map').setView([-1.3133, 36.7950], 15); // Kibera coords

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);

// Add water point
const waterIcon = L.icon({ iconUrl: 'water-icon.png', iconSize: [25, 25] });
L.marker([-1.3140, 36.7960], { icon: waterIcon })
  .bindPopup('Water Point #1<br>Open: 6am-8pm<br>Queue time: ~30min')
  .addTo(map);

// Heatmap of poverty
const heatData = [
  [-1.3133, 36.7950, 0.8], // lat, lng, intensity
  [-1.3140, 36.7960, 0.6],
  // ... more points
];
L.heatLayer(heatData).addTo(map);
```

**Inspiration**:
- [Kibera Public Space Project](http://mapkibera.org/)
- [OpenStreetMap Humanitarian](https://www.hotosm.org/)

---

### 2.4 Fundraising Platform

**Co**: Dedicated crowdfunding platform dla projektu

**Stack**:
- **Frontend**: React/Next.js
- **Backend**: Node.js + Stripe API
- **Database**: PostgreSQL

**Funkcje:**

**Campaign pages:**
- "Build a well in Kibera" - progress bar
- "Sponsor a child's education" - $300/year
- "Emergency medical fund"

**Payment:**
- Stripe/PayPal integration
- One-time & recurring donations
- Multiple currencies (PLN, USD, EUR)

**Transparency:**
- Real-time impact counter
- Photos/videos of completed projects
- Thank you messages from beneficiaries

**Gamification:**
- Badges (Bronze/Silver/Gold donor)
- Leaderboards
- Challenges ("Help us reach $10k this month!")

**Czas**: 25-40 godzin

**Impact**:
- 3-5x więcej donacji niż przez external platforms (lower fees)
- 70% donor retention (better engagement)

**Similar platforms**:
- [DonorBox](https://donorbox.org/) - inspo for features
- [GoFundMe Charity](https://www.gofundme.com/c/charity)

---

## 🔴 POZIOM 3: ZAAWANSOWANY (40-100+ godzin)

### 3.1 AI-Powered Malnutrition Detection

**Co**: AI analizujące zdjęcia dzieci do wykrywania niedożywienia

**Stack**:
- **ML**: TensorFlow / PyTorch
- **Computer Vision**: OpenCV
- **Model**: Transfer learning (ResNet, MobileNet)
- **Backend**: Python + FastAPI
- **Mobile**: Integracja z data collection app

**Jak działa:**

1. CHW robi zdjęcie dziecka (w czasie wizyty)
2. App wysyła zdjęcie do API
3. Model analizuje:
   - MUAC (Mid-Upper Arm Circumference) estimation
   - Facial features (sunken eyes, cheeks)
   - Skin condition
   - Body proportions
4. Output: 
   - Risk score (0-100)
   - Classification (normal / moderate / severe malnutrition)
   - Recommendations (urgent medical, monitoring, etc.)

**Training data:**
- WHO images (public datasets)
- Partnerstwo z lokalnym szpitalem (anonimized)
- Augmentation (różne światło, kąty)

**Accuracy target**: 85%+ (comparable to human assessment)

**Czas**: 60-120 godzin (research + training + deployment)

**Impact**:
- Early detection = ratowanie życia
- Skalowanie (1 model może ocenić tysiące dzieci)
- Consistency (no human bias)

**Ethical considerations**:
- Privacy (GDPR-compliant, data encryption)
- Bias (testing across ethnicities)
- Human-in-the-loop (zawsze final decision przez medyka)

**Research papers**:
- "Automated Detection of Malnutrition in Children Using CNNs"
- WHO guidelines on malnutrition assessment

**Podobne projekty**:
- [Project ECHO](https://hsc.unm.edu/echo/) - telemedicine
- [Peek Vision](https://peekvision.org/) - AI eye diagnostics

---

### 3.2 Predictive Analytics for Intervention Planning

**Co**: ML model przewidujący które rodziny potrzebują interwencji w najbliższym czasie

**Stack**:
- **ML**: Python + scikit-learn / XGBoost
- **Features**: Historical data (wizyty, health checks, income)
- **Dashboard**: Plotly/Dash dla visualizations

**Model:**

**Input features:**
- Demographic (household size, age, gender)
- Economic (income, employment status, debt)
- Health (malnutrition incidents, disease history)
- Education (school attendance %)
- Environmental (distance to water, toilet access)
- Historical (# of past interventions, outcomes)

**Output:**
- Risk score dla każdej rodziny (0-100)
- Probability of needing:
  - Medical intervention (next 30 days)
  - Food assistance (next 7 days)
  - Financial crisis (next 90 days)

**Use case:**

CHWs dostają każdego tygodnia listę "high risk" rodzin do odwiedzenia priorytetowo.

**Czas**: 50-80 godzin

**Impact**:
- 40% redukcja emergency cases (early intervention)
- Optimized resource allocation
- Data-driven decision making

**Model evaluation**:
- Precision/Recall (minimize false negatives - don't miss crises)
- ROC-AUC
- Fairness metrics (no discrimination)

**Code sketch**:
```python
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# Training
X = df[['household_size', 'income', 'malnutrition_history', ...]]
y = df['needed_intervention_30days']  # 0/1

model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Prediction
new_families = pd.read_csv('current_families.csv')
predictions = model.predict_proba(new_families)

# High risk = probability > 0.7
high_risk = new_families[predictions[:, 1] > 0.7]
print(f"Visit these {len(high_risk)} families this week:")
print(high_risk[['family_id', 'location', 'risk_score']])
```

---

### 3.3 SMS/USSD Platform for Beneficiaries

**Co**: System SMS/USSD pozwalający beneficjentom zgłaszać potrzeby bez smartfona

**Stack**:
- **Twilio API** lub **Africa's Talking** (dla Kenii)
- **Backend**: Node.js / Python
- **Database**: PostgreSQL

**Problem**: W Kiberze większość ma proste telefony (feature phones), nie smartfony.

**Rozwiązanie**: USSD (jak *123# w bankach) + SMS

**Funkcje:**

**USSD Menu:**
```
*789# → Slumsy Nie Takie Straszne

1. Zgłoś problem
   1. Potrzebuję jedzenia
   2. Dziecko chore
   3. Brak wody
   4. Inne
   
2. Sprawdź status zgłoszenia

3. Najbliższa pomoc (GPS location)

4. Kontakt CHW
```

**SMS incoming:**
- "FOOD 12345" → family ID 12345 needs food
- Auto-response: "Zgłoszenie przyjęte. CHW odwiedzi Cię w 24h."

**SMS outgoing (automated):**
- "Your child's health check-up is tomorrow at 10am at clinic #3"
- "Your microloan payment of 500 KES is due in 3 days"
- "New water point opened near you! Location: ..."

**Czas**: 40-60 godzin

**Impact**:
- 10x więcej zgłoszeń (każdy ma telefon vs 20% smartfonów)
- Faster response time
- Two-way communication

**Cost**: 
- Africa's Talking: $0.008/SMS, USSD: $0.02/session
- 1000 rodzin x 4 SMS/miesiąc = $32/mies

**Code example**:
```javascript
// Express + Africa's Talking
const africastalking = require('africastalking')({
  apiKey: 'YOUR_API_KEY',
  username: 'slumsy'
});

app.post('/ussd', (req, res) => {
  const { sessionId, phoneNumber, text } = req.body;
  
  let response = '';
  
  if (text === '') {
    // First interaction
    response = 'CON Witaj w Slumsy!\n1. Zgłoś problem\n2. Status\n3. Kontakt';
  } else if (text === '1') {
    response = 'CON Wybierz problem:\n1. Jedzenie\n2. Zdrowie\n3. Woda';
  } else if (text === '1*1') {
    // Food request
    saveToDB(phoneNumber, 'food');
    response = 'END Zgłoszenie zapisane. CHW się skontaktuje.';
  }
  
  res.send(response);
});
```

---

### 3.4 Blockchain-based Transparency Platform

**Co**: Blockchain tracking każdej darowizny od donora do beneficjenta

**Stack**:
- **Blockchain**: Ethereum / Polygon (lower fees)
- **Smart contracts**: Solidity
- **Frontend**: Web3.js + React
- **Explorer**: dla donorów do śledzenia ich $$

**Problem**: Donorzy nie wiedzą czy ich pieniądze doszły do beneficjentów (brak transparentności).

**Rozwiązanie**:

**Smart contract:**
```solidity
contract SlumsyDonation {
    struct Donation {
        address donor;
        uint amount;
        string purpose; // "education", "health", "food"
        string beneficiaryId;
        bool distributed;
        uint timestamp;
    }
    
    mapping(uint => Donation) public donations;
    uint public donationCount;
    
    function donate(string memory purpose, string memory beneficiaryId) public payable {
        donations[donationCount] = Donation(
            msg.sender,
            msg.value,
            purpose,
            beneficiaryId,
            false,
            block.timestamp
        );
        donationCount++;
    }
    
    function markDistributed(uint donationId) public onlyAdmin {
        donations[donationId].distributed = true;
    }
}
```

**Frontend:**
- Donor goes to website
- Connects MetaMask wallet
- Donates (e.g., $50 for "Sponsor Jane's education")
- Gets transaction hash
- Can track on explorer:
  - When funds were moved to local partner
  - When school fees were paid
  - Jane's progress reports (off-chain, linked)

**Czas**: 60-100 godzin (smart contract + security audit + frontend)

**Impact**:
- 100% transparency = trust = 3x więcej donorów
- No intermediary fees (crypto → local currency DEX)
- Immutable record dla audytów

**Challenges:**
- Gas fees (use Layer 2 like Polygon)
- Crypto adoption w Kenii (partnering z M-Pesa integration)
- Regulatory (Kenya's stance on crypto)

**Similar projects**:
- [GiveTrack](https://www.givetrack.org/) - BitGive Foundation
- [AidCoin](https://www.aidcoin.co/)

---

## 🛠️ SIDE PROJECTS - UTILITY TOOLS (5-20 godzin każdy)

### 4.1 WhatsApp Bot dla FAQs

**Co**: Bot odpowiadający na częste pytania (jak pomóc, gdzie jesteśmy, etc.)

**Stack**: Twilio WhatsApp API + Python

**Czas**: 5-10 godzin

---

### 4.2 Invoice/Receipt Generator

**Co**: Automated PDF receipts dla donorów (tax deduction)

**Stack**: Node.js + PDFKit / Python + ReportLab

**Czas**: 8-12 godzin

---

### 4.3 Volunteer Management System

**Co**: Portal dla wolontariuszy (aplikacja, scheduling, tracking hours)

**Stack**: Django / Rails

**Czas**: 20-30 godzin

---

### 4.4 Impact Calculator

**Co**: Widget na stronie "Twoje $50 = 1 dziecko w szkole przez miesiąc"

**Stack**: JavaScript widget

**Czas**: 3-5 godzin

---

### 4.5 Photo Story Generator

**Co**: AI generujące opisy success stories na podstawie zdjęć (GPT-4 Vision API)

**Stack**: OpenAI API + Python

**Czas**: 5-8 godzin

---

## 📊 PORÓWNANIE PROJEKTÓW - IMPACT vs EFFORT

| Projekt | Czas | Impact (1-10) | Difficulty | Priority |
|---------|------|---------------|------------|----------|
| **Landing page** | 5-10h | 6 | Easy | HIGH |
| **BMS** | 20-40h | 9 | Medium | HIGH |
| **Mobile data app** | 30-50h | 10 | Medium-Hard | HIGH |
| **Slum map** | 15-25h | 7 | Medium | Medium |
| **Fundraising platform** | 25-40h | 8 | Medium | HIGH |
| **AI malnutrition** | 60-120h | 10 | Hard | Medium |
| **Predictive analytics** | 50-80h | 8 | Hard | Low |
| **SMS/USSD** | 40-60h | 9 | Medium-Hard | Medium |
| **Blockchain** | 60-100h | 6 | Hard | Low |

---

## 🚀 RECOMMENDED PATH - JEŚLI ZACZYNASZ OD ZERA

### **Miesiąc 1** (10-15 godzin total):
1. **Tydzień 1-2**: Landing page (5-10h)
   - Ustaw podstawy: domena, hosting, content
2. **Tydzień 3-4**: Email automation (3-5h)
   - Mailchimp setup, templates

**Efekt**: Projekt ma profesjonalny front, może zbierać emaile i donacje.

---

### **Miesiąc 2-3** (20-30 godzin total):
3. **Tydzień 5-10**: Beneficiary Management System (20-40h)
   - Backend + frontend + deployment
   - Współpraca z 1-2 NGO pracującymi w Kiberze (testują)

**Efekt**: NGO mogą efektywniej zarządzać beneficjentami, mają dane do raportów.

---

### **Miesiąc 4-5** (30-50 godzin total):
4. **Tydzień 11-18**: Mobile Data Collection App (30-50h)
   - React Native + offline storage
   - Integracja z BMS (sync data)

**Efekt**: CHWs w terenie zbierają dane real-time, 2x więcej wizyt dziennie.

---

### **Miesiąc 6+** (wedle zainteresowań):
5. **Advanced projects**: AI malnutrition detection, SMS platform, etc.

---

## 💻 TECH STACK - CO POLECAMY

**Frontend:**
- **React** (most popular, huge community)
- **Next.js** (SEO, SSR for landing pages)
- **Tailwind CSS** (fast styling)

**Mobile:**
- **React Native + Expo** (cross-platform, jedna codebase)

**Backend:**
- **Node.js + Express** (JavaScript everywhere)
- **Python + FastAPI** (dla ML/AI projects)
- **PostgreSQL** (relational data - rodziny, intervencje)
- **MongoDB** (flexible schema - różne typy danych)

**Hosting:**
- **Vercel/Netlify** (frontend - FREE tier)
- **Railway/Fly.io** (backend - FREE tier wystarczy na start)
- **Supabase** (PostgreSQL + auth + storage - FREE tier)

**APIs:**
- **Stripe** (payments)
- **Twilio / Africa's Talking** (SMS/WhatsApp)
- **Mapbox** (maps)
- **OpenAI** (GPT for content generation)

---

## 🤝 JAK ZACZĄĆ - KONKRETNE KROKI

### **Krok 1: Dołącz do projektu**
- Email: [do utworzenia - devs@slumsynietakiestraszne.org]
- Discord server: [do utworzenia]
- GitHub org: github.com/slumsy-tech

### **Krok 2: Wybierz projekt**
- Zobacz roadmap (GitHub Projects)
- Claim issue ("I'll work on this")
- Zespół pomoże w onboardingu

### **Krok 3: Build**
- Fork repo
- Local development
- Pull request
- Code review
- Deploy

### **Krok 4: See impact**
- Twój kod używany w Kiberze
- Feedback od CHWs
- Success stories ("dzięki Twojej appce uratowaliśmy Jane")

---

## 📈 CASE STUDY - REALNE PRZYKŁADY

### **Przykład 1: Peek Vision (UK)**
- **Co**: Aplikacja mobilna do badania wzroku w developing countries
- **Tech**: iOS/Android app, AI image recognition
- **Impact**: 300,000+ badań w 40 krajach
- **Team**: 5 devs + 2 doctors
- **Funding**: Gates Foundation grant

### **Przykład 2: Ushahidi (Kenya)**
- **Co**: Crowdsourced crisis mapping (started during 2008 Kenya elections)
- **Tech**: Web platform + SMS
- **Impact**: Used in Haiti earthquake, Libya conflict, etc.
- **Team**: Open source, 100+ contributors
- **Bootstrapped** → self-sustaining

### **Przykład 3: mPharma (Ghana/Kenya)**
- **Co**: Prescription management platform dla aptek w Afryce
- **Tech**: Web + mobile app, inventory management
- **Impact**: 9M+ patients, $100M+ funding
- **Started**: 3 devs in Ghana

**Lesson**: Small tech projects can scale to life-changing impact.

---

## ❓ FAQ

### Q: Nie znam Reacta/Node.js, mogę i tak pomóc?
**A**: TAK! Możesz:
- Uczyć się podczas projektu (dokumentacja, tutorials)
- Zacząć od prostszych tasków (HTML/CSS, dokumentacja)
- Pair programming z doświadczonymi devs

### Q: Czy muszę jechać do Kenii?
**A**: NIE. 95% pracy zdalnie. Opcjonalnie: reconnaissance trip (2 tyg) żeby zobaczyć impact na własne oczy.

### Q: Jak jest z prawami autorskimi?
**A**: Projekt open source (MIT license). Ty zachowujesz authorship (GitHub commits), ale kod jest wolny dla wszystkich NGO.

### Q: Czy to płatne?
**A**: Nie, to wolontariat. ALE:
- Możesz użyć w CV/portfolio (realne projekty z impactem)
- Reference letter od fundacji
- Jeśli projekt pozyska duże fundy (EU grant), możliwość paid consultancy

### Q: Ilu devs jest w projekcie?
**A**: Teraz: 0 (projekt nowy!)
**Target**: 10-20 active contributors
**Long-term**: 50+ (jak OpenStreetMap)

### Q: Ile czasu muszę się zobowiązać?
**A**: Minimum: 2h/tydzień. Realnie: 5-10h/tydzień dla significant impact.

---

## 🎁 CO TY ZYSKUJESZ

### **Portfolio:**
- Realne projekty (nie TODO app)
- Live production (używane przez NGO)
- International exposure
- Social impact story dla interviews

### **Skills:**
- Pracujesz z real constraints (offline-first, low bandwidth, różne devices)
- Nowe tech (ML, blockchain, mobile, GIS)
- Cross-functional team (devs + medycy + social workers)

### **Network:**
- Poznasz devs z całego świata (open source community)
- Contact z NGO sector (może przyszła kariera?)
- Reference od fundacji

### **Impact:**
- Twój kod ratuje życia (dosłownie)
- Widzisz zmianę (feedback z terenu)
- Purpose-driven work

### **Fun:**
- Hackathons (online/offline)
- Team retreats (potential Kenya trip!)
- Build something that matters

---

## 📞 CONTACT

**Dla programistów zainteresowanych projektem:**

- **Email**: devs@slumsynietakiestraszne.org [do utworzenia]
- **Discord**: [tech-for-good] [do utworzenia]
- **GitHub**: github.com/slumsy-tech [do utworzenia]
- **LinkedIn**: [grupa] [do utworzenia]

**Pierwsze spotkanie:**
- **Online kickoff**: Co 2 tygodnie (sobota 10:00 CET)
- **Topic**: Roadmap, assign projects, Q&A

---

## 🌟 CALL TO ACTION

### Jesteś programistą?

**Masz kilka godzin tygodniowo?**

**Chcesz żeby Twój kod miał realny impact?**

### **DOŁĄCZ DO NAS.**

**1 programista** = System dla 50 rodzin  
**5 programistów** = Platforma dla 500 rodzin  
**20 programistów** = Rozwiązanie skalowalne na całą Afrykę  

---

**Kod może zmieniać świat. Zaczynamy od Kibery.**

**Slumsy nie takie straszne - Tech Team** 💻🌍

---

*Dokument tech - wersja 1.0*  
*Data: 26 października 2025*  
*Contributors wanted: ∞*
