# n8n Workflows für EmpireHazeClaw

---

## 1. Sales & Outreach Workflows

### A. Lead Management

```
[Webhook] → [CRM speichern] → [Email senden] → [Slack Alert]
```

**Trigger:** Webhook von Website
**Steps:**
1. Webhook (Lead from website)
2. Write to CSV/Google Sheet
3. Send Email via Brevo
4. Send Slack message to #leads

---

### B. Follow-up Automation

```
[Schedule] → [Check CRM] → [If no response] → [Send Follow-up]
```

**Trigger:** Täglich 9:00
**Steps:**
1. Read Google Sheet
2. IF Date = Today + 3 days
3. Send follow-up email
4. Update status

---

### C. New Lead Welcome

```
[New Row in Sheet] → [Send Welcome Email] → [Add to Newsletter] → [Create Task]
```

**Trigger:** New row
**Steps:**
1. Google Sheets trigger
2. Send welcome email (Brevo)
3. Add to Brevo list
4. Create Notion task

---

## 2. Marketing Workflows

### A. Social Media Auto-Post

```
[Blog New Post] → [Generate Social Text] → [Post to Twitter] → [Post to LinkedIn]
```

**Trigger:** RSS Feed or manual
**Steps:**
1. RSS Read (our blog)
2. AI (generate tweets)
3. HTTP Request (xurl/Twitter API)
4. HTTP Request (LinkedIn API)

---

### B. Content Repurposing

```
[YouTube Video] → [Get Transcript] → [AI Summary] → [Blog Post] → [Social Posts]
```

**Trigger:** Manual
**Steps:**
1. YouTube get video
2. AI extract key points
3. Write to WordPress
4. Create social posts

---

### C. Newsletter Automation

```
[Blog Post] → [AI Summary] → [Brevo Newsletter] → [Schedule Send]
```

**Trigger:** New blog post
**Steps:**
1. RSS trigger
2. AI create summary
3. Brevo create campaign
4. Schedule for Monday 10:00

---

## 3. Customer Service

### A. Support Ticket

```
[Email Received] → [Categorize] → [Create Ticket] → [Auto-Reply]
```

**Trigger:** Email (Brevo)
**Steps:**
1. Email trigger
2. Classify (urgent/normal)
3. Create Notion ticket
4. Send auto-reply

---

### B. FAQ Chatbot

```
[Webform Submit] → [AI Response] → [Email to Customer]
```

**Trigger:** Website form
**Steps:**
1. Webhook
2. AI generate response
3. Send email

---

## 4. Operations

### A. Daily Report

```
[Schedule] → [Gather Metrics] → [Format Message] → [Send to Slack/Telegram]
```

**Trigger:** Daily 8:00
**Steps:**
1. Schedule trigger
2. Get website status
3. Get outreach stats
4. Send Telegram message

---

### B. Backup Automation

```
[Schedule] → [Create Backup] → [Upload to Drive] → [Slack Notification]
```

**Trigger:** Weekly Sunday 3:00
**Steps:**
1. Execute shell command
2. Upload to Google Drive
3. Send Slack notification

---

## 5. Finance

### A. Invoice Creation

```
[New Customer] → [Create Stripe Invoice] → [Send to Customer] → [Add to Sheet]
```

**Trigger:** New row in CRM
**Steps:**
1. Google Sheets trigger
2. Stripe create invoice
3. Send via email
4. Update sheet

---

## 6. Quick Start Workflows

### 1. Simple Email Forward

```
[Gmail New Email] → [Forward to Brevo] → [Label]
```

### 2. Contact Form to CRM

```
[WordPress Form] → [Add to Sheet] → [Email Alert]
```

### 3. Social Media Scheduler

```
[Scheduled] → [Read from Sheet] → [Post to Twitter]
```

---

## Verfügbare n8n Nodes

| Service | Status | Use |
|---------|--------|-----|
| Gmail | ✅ | Email |
| Brevo | ✅ | Email Marketing |
| Stripe | ✅ | Payments |
| Google Sheets | ✅ | CRM |
| Notion | ✅ | Tasks |
| Slack | ✅ | Notifications |
| Telegram | ✅ | Notifications |
| Twitter/X | ✅ | Social |
| Webhook | ✅ | Triggers |
| HTTP Request | ✅ | APIs |
| AI | ✅ | OpenAI, Anthropic |

---

## Nächste Schritte

1. ✅ n8n installiert (Port 5678)
2. ⬜ Workflow 1: Lead → CRM → Email
3. ⬜ Workflow 2: Daily Report
4. ⬜ Workflow 3: Social Auto-Post

