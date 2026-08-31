# Regulation Monitor — Try It Yourself

A working tool that watches the federal **Nuclear Regulatory Commission** feed for
new rules on nuclear-medicine topics and emails you when something posts. Built
for the Krista use case. You can stand up your own private copy and see it run in
about 5 minutes — no coding.

---

## What you'll need
- A GitHub account (free)
- A Gmail address + a Google **app password** (16 characters). If you have
  2-Step Verification on, make one at **myaccount.google.com/apppasswords**.

---

## Steps

**1. Make your own copy**
On the repo page, click the green **Use this template** → **Create a new
repository**. Name it whatever you like, click **Create**.

**2. Set the recipient**
Open `monitor.py` → click the pencil to edit → find the line
`RECIPIENT = "your-email@example.com"` and put your real email between the
quotes → **Commit changes**.

**3. Add your email login as secrets**
Go to **Settings → Secrets and variables → Actions**, then add two secrets
(**New repository secret** each time):
- Name `SMTP_USER`  → value: your Gmail address
- Name `SMTP_PASS`  → value: your 16-character app password

**4. Run it**
Click the **Actions** tab → if prompted, enable workflows → click **Regulation
Monitor** → **Run workflow**. Wait ~20 seconds and refresh.

**5. Check your inbox**
You'll get a digest of NRC items from the last 30 days that match the keywords.
(Check spam on the first one.)

---

## Making it yours
Everything you'd change lives in the **CONFIG block** at the top of `monitor.py`:
- `AGENCIES` — which agency to watch (any Federal Register agency slug)
- `KEYWORDS` — the topics to flag
- `MODE` — `"daily"` for one digest, or `"instant"` to email each item as it posts
- The schedule (daily time vs. every-30-min) is two toggle lines in
  `.github/workflows/monitor.yml`

That's the whole engine. Same architecture handles any agency + any keyword set.
