# 💳 Stripe Setup Guide

*Erstellt: 2026-03-06*

---

## Was ist Stripe?

**Online-Zahlungsabwicklung** für:
- 🛒 Online-Shops
- 💼 Freelancer
- 📱 Apps/SaaS
- 🎮 Digital Products

---

## 🏦 Warum Stripe?

| Vorteil | Beschreibung |
|---------|---------------|
| **Einfach** | 5-Minuten Setup |
| **Sicher** | PCI-konform |
| **Schnell** | Auszahlung in 2-7 Tagen |
| **Günstig** | 1.4% + €0.25 (EU) |

---

## 📋 Setup Schritt für Schritt

### Schritt 1: Account erstellen

1. Gehe zu [stripe.com](https://stripe.com)
2. "Sign up" klicken
3. E-Mail eingeben
4. Passwort erstellen
5. E-Mail bestätigen

### Schritt 2: Verifizieren

1. **Persönliche Daten**
   - Name
   - Adresse
   - Geburtsdatum

2. **Unternehmensart**
   - Privatperson / Solo-Entrepreneur
   - Firma/GmbH

3. **Bankkonto** für Auszahlungen

### Schritt 3: Dokument hochladen

- Personalausweis
- Falls Firma: Handelsregister

---

## 💰 Gebühren

### Deutschland

| Zahlungsmethode | Gebühr |
|----------------|--------|
| Karte (EU) | 1.4% + €0.25 |
| Karte (International) | 2.5% + €0.25 |
| Sofort | 1% |
| Giropay | 1% |

### Auszahlung

| Methode | Zeit | Kosten |
|---------|------|--------|
| Bank | 2-7 Tage | Kostenlos |
| Express | 1 Tag | €2 |

---

## 🔗 Integration

### Für Webseiten

```javascript
// Stripe Checkout
const stripe = require('stripe')('sk_test_...');

const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'],
  line_items: [{
    price_data: {
      currency: 'eur',
      product_data: { name: 'Mein Produkt' },
      unit_amount: 2999,
    },
    quantity: 1,
  }],
  mode: 'payment',
  success_url: 'https://meine-seite.de/success',
  cancel_url: 'https://meine-seite.de/cancel',
});
```

### Für Freelancer

1. **Payment Links** — Kein Code nötig
2. **Stripe Invoicing** — Rechnungen erstellen

---

## 📝 Use Cases

### 1. Direkte Zahlungen

```
Produkt verkaufen → Payment Link → Kunde zahlt → Geld auf Konto
```

### 2. Abonnements

```
Kunde zahlt monatlich → Recurring → Passives Einkommen
```

### 3. Rechnungen

```
Rechnung erstellen → Kunde zahlt → Automatisch gebucht
```

---

## 📊 Für uns

### Mögliche Nutzung

| Service | Stripe Nutzung |
|---------|---------------|
| Fiverr | Auszahlungen |
| Direkte Kunden | Rechnungen |
| Digital Products | Automatisch |
| eBooks | Payment Links |

### Alternative: PayPal

| Anbieter | Vorteil |
|----------|----------|
| Stripe | Günstiger, Modern |
| PayPal | Bekannter, Leichter für Kunden |

---

## 🛡️ Sicherheit

Stripe ist PCI-konform:
- SSL-Verschlüsselung
- 2-Faktor-Auth
- Fraud Protection
- Radar (AI-basiert)

---

## 📋 Checkliste

### Vor dem Start

- [ ] Stripe Account erstellen
- [ ] Verifizierung abschließen
- [ ] Bankkonto verknüpfen
- [ ] Test-Modus aktivieren

### Für Production

- [ ] Alle Tests bestanden
- [ ] AGB/Impressum auf Webseite
- [ ] Widerrufsrecht

---

## 🚀 Quick Start

### Für Freelancer (ohne Webseite)

1. **Account erstellen** → stripe.com
2. **Payment Link erstellen** → Kein Code!
3. **Link teilen** → Kunde zahlt

### Beispiel: Digitales Produkt €50

1. Product erstellen → "Mein eBook"
2. Price → €50
3. Payment Link generieren
4. Link in E-Mail/Website teilen

---

## 💡 Tipps

1. **Test-Modus nutzen** — Erst testen
2. **Payment Links** — Einfachster Start
3. **Invoice** — Für wiederkehrende Kunden
4. **Subscription** — Für monatliche Services

---

*Aktualisiert: 2026-03-06*
