# Der ultimative "Hands-Off" Sales Funnel

Aktuell haben wir viele isolierte Prozesse (Scrapen, Mails senden, Produkte generieren). Um *wirklich* zu automatisieren (Geld im Schlaf verdienen), müssen wir die Systeme wie Legosteine verketten.

Hier sind 3 kritische Automatisierungs-Schleifen, die wir bauen können:

## 1. Der Endlos-Lead-Generator (B2B SaaS)
* **Aktuell:** Wir führen ein Skript manuell aus, das 5 IT-Agenturen scrappt und anmailt.
* **Voll-Automatisiert:** 
  - Ein Cronjob läuft täglich um 02:00 Uhr.
  - Der `crawl4ai`-Agent sucht in DuckDuckGo nach wechselnden Keywords (z.B. "Webdesign Agentur München", "KI Beratung Berlin").
  - Er extrahiert E-Mails, validiert sie und gleicht sie mit einer "Blacklist" ab (damit wir niemanden zweimal anschreiben).
  - Um 08:30 Uhr übergibt er die frischen Leads (Tageslimit: max. 25, um Spam-Filter zu meiden) an den `outreach`-Agenten.
  - Der Outreach-Agent schreibt *personalisierte* Mails (z.B. "Hey [Name], mir gefällt euer Projekt [Portfolio-Item aus dem Crawl]").

## 2. Der "Inbound-Closer" (Gmail OAuth)
* **Aktuell:** Wenn uns eine der 5 IT-Agenturen antwortet ("Klingt interessant, was kostet das Setup?"), liegt die Mail tot in unserem `empirehazeclaw@gmail.com` Postfach.
* **Voll-Automatisiert:**
  - Wir richten endlich das Gmail OAuth ein (`gog auth add empirehazeclaw@gmail.com --services gmail`).
  - Ein Agent checkt alle 15 Minuten die Inbox auf neue Antworten.
  - Wenn eine Antwort positiv/interessiert ist, draftet der Agent selbstständig eine Antwort (mit Stripe Payment Link oder Calendly-Termin) und legt sie dir als Entwurf hin (oder schickt sie direkt, je nach Freigabe).

## 3. Der Social-Media Content Loop
* **Aktuell:** Wir haben 3 Reddit-Posts generiert, die du morgen manuell kopieren musst.
* **Voll-Automatisiert:**
  - Wir nutzen unsere `multi_platform_analytics.py` (die als Hidden Gem schlummert).
  - Ein Cronjob postet automatisch jeden Dienstag und Donnerstag einen SEO-optimierten Artikel auf unserem Blog.
  - Ein zweiter Job liest diesen Blogpost, fasst ihn zusammen und postet ihn (sobald wir den 403-Fehler gefixt haben) auf Twitter und LinkedIn.
  - *Optional:* Wir nutzen Tools wie `praw` (Python Reddit API Wrapper), um automatisch in Subreddits zu kommentieren (sehr hohes Bann-Risiko, daher lieber manuell lassen).
