# 🛒 STORE INTEGRATION PLAN

*Erstellt: 2026-03-28*

---

## STRIPE CHECKOUT LINKS (AKTUELL)

| Produkt | Link |
|---------|------|
| Managed AI Starter | https://checkout.stripe.com/g/pay/cs_live_a19hziBm99XL9Tx2gBW3ewLl6ktlKSgEDY35w9iUGdEc |
| Managed AI Professional | https://checkout.stripe.com/g/pay/cs_live_a1I6R47rrCkqBD8HlGCFh6MrubrbZA6RmvcKC6Q5G66 |

---

## TODO:

### 1. .DE → Stripe Integration
- .de Pricing Section mit Store Checkout Links verknüpfen
- Alle "Jetzt kaufen" Buttons → auf Store oder direkt zu Stripe

### 2. Store als Primary Checkout
- .de, .com, .info → Links zu .store/buy.html
- Buy Page zeigt alle Produkte mit Stripe Checkout

---

## QUICK FIX: Buy Page erstellen

Erstelle buy.html auf Store mit allen Produkten:

```html
<!DOCTYPE html>
<html>
<head>
  <title>Kaufen - EmpireHazeClaw</title>
</head>
<body>
  <h1>KI-Mitarbeiter kaufen</h1>
  
  <div class="product">
    <h2>Managed AI Hosting Starter</h2>
    <p>€99/Monat</p>
    <a href="https://checkout.stripe.com/g/pay/cs_live_a19hziBm99XL9Tx2gBW3ewLl6ktlKSgEDY35w9iUGdEc">
      Jetzt kaufen
    </a>
  </div>
  
  <div class="product">
    <h2>Managed AI Hosting Professional</h2>
    <p>€199/Monat</p>
    <a href="https://checkout.stripe.com/g/pay/cs_live_a1I6R47rrCkqBD8HlGCFh6MrubrbZA6RmvcKC6Q5G66">
      Jetzt kaufen
    </a>
  </div>
</body>
</html>
```

---

## STATUS

- [ ] .de mit Stripe verlinken
- [ ] Buy Page erstellen
- [ ] Alle anderen Sites → Buy Page redirect
