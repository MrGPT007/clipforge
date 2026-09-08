---
Note ID: "20260216161912"
Note Title: "GRANDMA-PROOF UI COPY RULEBOOK"
Created on: " Monday-16-February-2026-16-19-12}"
updated:
Note Type:
  - "#New "
Status:
  - "#active"
  - "#archived "
  - "#completed"
tags:
  - note
---
# GRANDMA-PROOF UI COPY RULEBOOK 

# 📘 GRANDMA-PROOF UI COPY RULEBOOK FOR BUILDER LLMs

**Version:** 1.0  
**Purpose:** Ensure every UI element has clear, jargon-free helper text  
**Audience:** Builder LLMs creating admin interfaces  
**Status:** Mandatory for all user-facing settings

***

## 🎯 CORE PRINCIPLE

> **"If an 80-year-old grandma who has never used a computer can't understand what will happen when she clicks this button, the copy is not good enough."**

Every setting, checkbox, button, and input field must answer three questions:
1. **What does this do?** (In plain language)
2. **What happens if I enable/disable it?** (Concrete outcome)
3. **Should I use it?** (Guidance for decision-making)

***

## 🚫 FORBIDDEN PHRASES

### **Never Use These:**
❌ "Configure settings"  
❌ "Enable functionality"  
❌ "Advanced options"  
❌ "Technical parameters"  
❌ "Integration settings"  
❌ "API endpoint"  
❌ "Hook into system"  
❌ "Initialize component"  
❌ "Toggle feature flag"  
❌ "Customize behavior"

### **Why These Are Bad:**
- They don't explain **what actually happens**
- They assume technical knowledge
- They require the user to already know what the feature does
- They create anxiety ("Should I configure this?")

***

## ✅ REQUIRED COPY STRUCTURE

### **Every Setting Must Have:**

1. **Label** (What it's called)
2. **Helper Text** (What it does in plain English)
3. **Consequence Text** (What will happen when enabled/disabled)
4. **Recommendation** (Should the user enable it?)
5. **Example** (Optional but powerful - show real outcome)

***

## 📋 COPY TEMPLATES

### **Template 1: Checkbox Settings**

```
┌─────────────────────────────────────────────────────┐
│ ☐ [LABEL - Clear name, no jargon]                  │
│                                                     │
│ [HELPER TEXT - What this does in one sentence]     │
│                                                     │
│ ✅ When enabled: [Concrete outcome]                 │
│ ❌ When disabled: [What won't happen]               │
│                                                     │
│ 💡 Recommendation: [Who should use this and why]    │
└─────────────────────────────────────────────────────┘
```

### **Example - Good Checkbox:**

```
┌─────────────────────────────────────────────────────┐
│ ☐ Block Spam Email Addresses                       │
│                                                     │
│ Stop people from receiving emails sent from        │
│ temporary or throwaway email services.             │
│                                                     │
│ ✅ When enabled: Emails from services like          │
│    "tempmail.com" or "10minutemail.com" will be    │
│    rejected. Your users won't see these messages.  │
│                                                     │
│ ❌ When disabled: All emails are accepted,          │
│    including spam from throwaway addresses.        │
│                                                     │
│ 💡 Recommendation: Turn this ON if you're getting   │
│    spam. Turn it OFF if you want to accept all     │
│    emails (testing, internal use).                 │
└─────────────────────────────────────────────────────┘
```

### **Example - Bad Checkbox (What NOT to do):**

```
┌─────────────────────────────────────────────────────┐
│ ☐ Enable Disposable Domain Filter                  │  ← ❌ Jargon
│                                                     │
│ Configure rejection rules for temporary inboxes.   │  ← ❌ Vague
└─────────────────────────────────────────────────────┘
```

***

### **Template 2: Number Input Settings**

```
┌─────────────────────────────────────────────────────┐
│ [LABEL]                                             │
│ [ 5 ] [unit (emails, seconds, days, etc.)]        │
│                                                     │
│ [HELPER TEXT - What this number controls]          │
│                                                     │
│ 📊 Examples:                                        │
│    • If set to X: [What happens]                   │
│    • If set to Y: [What happens]                   │
│                                                     │
│ 💡 Recommended: [Default value and why]             │
└─────────────────────────────────────────────────────┘
```

### **Example - Good Number Input:**

```
┌─────────────────────────────────────────────────────┐
│ Maximum Emails Per Person (Per Hour)               │
│ [ 5 ] emails                                       │
│                                                     │
│ How many temporary emails one person can create    │
│ in one hour.                                       │
│                                                     │
│ 📊 Examples:                                        │
│    • If set to 5: One person can create 5 emails   │
│      per hour. Good for normal use.                │
│    • If set to 1: Very strict - only 1 email per   │
│      hour. Use this to prevent abuse.              │
│    • If set to 50: Very loose - allows 50 emails.  │
│      Only use for testing or internal sites.       │
│                                                     │
│ 💡 Recommended: 5 emails per hour prevents spam    │
│    bots while allowing real people to use your     │
│    service normally.                               │
└─────────────────────────────────────────────────────┘
```

***

### **Template 3: Dropdown/Select Settings**

```
┌─────────────────────────────────────────────────────┐
│ [LABEL]                                             │
│ [Dropdown ▼]                                        │
│                                                     │
│ [HELPER TEXT - What this choice controls]          │
│                                                     │
│ 📌 Options explained:                               │
│    • [Option 1]: [What happens if selected]        │
│    • [Option 2]: [What happens if selected]        │
│    • [Option 3]: [What happens if selected]        │
│                                                     │
│ 💡 Recommended: [Which option and why]              │
└─────────────────────────────────────────────────────┘
```

### **Example - Good Dropdown:**

```
┌─────────────────────────────────────────────────────┐
│ Username Character Type                             │
│ [Lowercase Letters & Numbers ▼]                    │
│                                                     │
│ What kind of characters are used in random email   │
│ usernames (the part before @).                     │
│                                                     │
│ 📌 Options explained:                               │
│    • Lowercase & Numbers (abc123):                 │
│      Easy to read, no confusion. Recommended.      │
│                                                     │
│    • Letters Only (abcxyz):                        │
│      No numbers. Harder to tell emails apart.      │
│                                                     │
│    • Mixed Case (AbC123):                          │
│      Uppercase and lowercase. Can cause confusion  │
│      because email addresses ignore case.          │
│                                                     │
│    • Numbers Only (123456):                        │
│      Very easy to guess. NOT secure. Avoid this.   │
│                                                     │
│ 💡 Recommended: Use "Lowercase & Numbers" for best │
│    security and readability.                       │
└─────────────────────────────────────────────────────┘
```

***

### **Template 4: Textarea Settings (Lists)**

```
┌─────────────────────────────────────────────────────┐
│ [LABEL]                                             │
│ ┌─────────────────────────────────────────────────┐ │
│ │ [Pre-filled examples]                           │ │
│ │                                                 │ │
│ │                                                 │ │
│ └─────────────────────────────────────────────────┘ │
│ [One item per line]                                 │
│                                                     │
│ [HELPER TEXT - What this list does]                │
│                                                     │
│ ✅ What this blocks/allows: [Clear explanation]     │
│                                                     │
│ 📝 How to use:                                      │
│    1. [Step 1]                                     │
│    2. [Step 2]                                     │
│                                                     │
│ 💡 Tip: [Common use case or example]                │
└─────────────────────────────────────────────────────┘
```

### **Example - Good Textarea:**

```
┌─────────────────────────────────────────────────────┐
│ Blocked Usernames                                   │
│ ┌─────────────────────────────────────────────────┐ │
│ │ admin                                           │ │
│ │ support                                         │ │
│ │ help                                            │ │
│ │ webmaster                                       │ │
│ └─────────────────────────────────────────────────┘ │
│ One username per line                               │
│                                                     │
│ These usernames cannot be used in temporary email  │
│ addresses. This prevents people from pretending to │
│ be official accounts.                              │
│                                                     │
│ ✅ What this blocks:                                 │
│    • If "admin" is blocked, nobody can create      │
│      "admin@yourdomain.com"                        │
│    • Protects important-sounding names from abuse  │
│                                                     │
│ 📝 How to use:                                      │
│    1. Type one username per line (press Enter)     │
│    2. Don't include the @domain.com part           │
│    3. Use lowercase only                           │
│                                                     │
│ 💡 Example: Block "sales" to prevent fake sales    │
│    emails. Block "ceo" to prevent impersonation.   │
│                                                     │
│ [Load Default List] [Clear All]                    │
└─────────────────────────────────────────────────────┘
```

***

### **Template 5: Warning/Risk Settings**

```
┌─────────────────────────────────────────────────────┐
│ ⚠️ [LABEL with warning icon]                       │
│                                                     │
│ [HELPER TEXT - What this risky feature does]       │
│                                                     │
│ ⚠️ IMPORTANT:                                       │
│    [What can go wrong if misused]                  │
│                                                     │
│ ✅ Use this if: [Specific use case]                 │
│ ❌ Don't use if: [When to avoid]                    │
│                                                     │
│ 💡 Most people should leave this OFF.               │
└─────────────────────────────────────────────────────┘
```

### **Example - Good Warning Setting:**

```
┌─────────────────────────────────────────────────────┐
│ ⚠️ Allow Custom Email Addresses via URL            │
│                                                     │
│ Let people create specific email addresses by      │
│ typing them in the website address bar.            │
│                                                     │
│ Example: yoursite.com?email=john@example.com       │
│ → Creates "john@example.com" automatically         │
│                                                     │
│ ⚠️ IMPORTANT:                                       │
│    • This lets people pick ANY username they want  │
│    • Spammers can create unlimited specific emails │
│    • Bypasses all rate limits and protections      │
│    • Can be abused to flood your system            │
│                                                     │
│ ✅ Use this if:                                     │
│    • You're building an app that needs this feature│
│    • You have OTHER security measures in place     │
│    • Your site is for internal company use only    │
│                                                     │
│ ❌ Don't use if:                                    │
│    • Your site is open to the public              │
│    • You're worried about spam or abuse           │
│    • You don't understand what URLs are           │
│                                                     │
│ 💡 Recommended: Leave this OFF unless you have a   │
│    specific technical reason to enable it.         │
│                                                     │
│ Currently: ☐ OFF (recommended for most users)      │
└─────────────────────────────────────────────────────┘
```

***

## 🎨 VISUAL AIDS

### **Use Icons to Guide Users:**

- ✅ = Good outcome / Enabled state
- ❌ = Bad outcome / Disabled state / Warning
- 💡 = Recommendation / Tip
- ⚠️ = Important warning / Risk
- 📊 = Example / Statistics
- 📝 = Instructions / How to use
- 🔒 = Security-related
- 🌍 = Public-facing / External users
- 🏢 = Internal / Company use
- 🎯 = Goal / Purpose
- ⏱️ = Time-related
- 📧 = Email-related
- 🛡️ = Protection / Safety

***

## 📐 COPY RULES

### **Rule 1: No Jargon**

**BAD:**
> "Enable SMTP relay authentication for outbound message processing"

**GOOD:**
> "Require a password before sending emails to other people"

***

### **Rule 2: Explain Consequences**

**BAD:**
> "Configure maximum session limit"

**GOOD:**
> "How many temporary emails one person can create before they have to start over. If set to 3: After creating 3 emails, they must clear their browser cookies to create more."

***

### **Rule 3: Provide Examples**

**BAD:**
> "Set username length parameters"

**GOOD:**
> "How long email usernames can be. If set to 6-10: Generates names like 'abc123' (6 characters) to 'hello12345' (10 characters). Shorter = easier to type. Longer = harder to guess."

***

### **Rule 4: Explain Trade-offs**

**BAD:**
> "Enable rate limiting"

**GOOD:**
> "Limit how many emails people can create per hour. Higher number = More convenient for real users, but easier for spammers. Lower number = Harder for spammers, but can frustrate real users who need multiple emails."

***

### **Rule 5: Use Comparison**

**BAD:**
> "Set cooldown period"

**GOOD:**
> "Time someone must wait before creating another email. 10 seconds = Very fast (good for testing). 30 seconds = Normal speed (recommended). 60 seconds = Slow (annoying for users, use only if you have spam problems)."

***

### **Rule 6: Answer "Why?"**

**BAD:**
> "Prohibited words filter"

**GOOD:**
> "Block usernames containing certain words. WHY? Prevents people from creating emails like 'drugs123@yourdomain.com' or 'spam456@yourdomain.com' which make your site look unprofessional and attract spam."

***

### **Rule 7: Explain Units**

**BAD:**
> "Email lifetime: [ 24 ]"

**GOOD:**
> "Email lifetime: [ 24 ] hours
> 
> How long before temporary emails are automatically deleted.
> - 1 hour = Very short (use for quick tests)
> - 24 hours = One day (recommended for most users)
> - 168 hours = One week (use if people need emails longer)"

***

## 🧪 TESTING YOUR COPY

### **The Grandma Test:**

Read your helper text out loud. Then ask:

1. **Understanding:** "Can I explain what this does without looking at the screen?"
   - If NO → Copy is too complex

2. **Confidence:** "Do I know what will happen if I click this?"
   - If NO → Add consequence text

3. **Decision:** "Do I know whether I should enable this or not?"
   - If NO → Add recommendation

4. **Safety:** "Do I understand if this could cause problems?"
   - If NO → Add warning text

***

## 📋 MANDATORY COPY CHECKLIST

Before submitting ANY settings interface, verify:

### **Every Checkbox Has:**
- [ ] Clear label (no abbreviations, no jargon)
- [ ] One-sentence explanation of what it does
- [ ] "When enabled" outcome
- [ ] "When disabled" outcome
- [ ] Recommendation (turn on/off/who should use it)

### **Every Number Input Has:**
- [ ] Label with unit clearly shown
- [ ] Explanation of what the number controls
- [ ] At least 2 examples (low value, high value)
- [ ] Recommended default value with reason
- [ ] Valid range displayed (min/max)

### **Every Dropdown Has:**
- [ ] Clear label
- [ ] Explanation of what choice controls
- [ ] Each option explained individually
- [ ] Recommended option marked
- [ ] Warnings for dangerous options

### **Every Textarea Has:**
- [ ] Label and format instruction (e.g., "one per line")
- [ ] Pre-filled examples visible
- [ ] Explanation of what list does
- [ ] Step-by-step usage instructions
- [ ] "Load Defaults" and "Clear" buttons

### **Every Dangerous Setting Has:**
- [ ] ⚠️ Warning icon in label
- [ ] "IMPORTANT" section with risks
- [ ] "Use this if" (positive use case)
- [ ] "Don't use if" (when to avoid)
- [ ] Recommendation to leave OFF by default

***

## 🎯 REAL-WORLD EXAMPLES

### **Example 1: CAPTCHA Setting**

**❌ BAD VERSION:**
```
☐ Enable CAPTCHA
   Integrate CAPTCHA verification system
```

**✅ GOOD VERSION:**
```
┌─────────────────────────────────────────────────────┐
│ 🛡️ Block Robots with Puzzle Verification           │
│ ☐ Require people to solve a puzzle before creating │
│    temporary emails                                 │
│                                                     │
│ Shows a "I'm not a robot" checkbox that people must│
│ click before generating an email address.          │
│                                                     │
│ ✅ When enabled:                                     │
│    • Real people see a checkbox to click           │
│    • Robots (spam bots) cannot create emails       │
│    • Your service is protected from automated abuse│
│                                                     │
│ ❌ When disabled:                                    │
│    • No extra steps for users (faster)             │
│    • Robots can freely create unlimited emails     │
│    • You may get spam or abuse                     │
│                                                     │
│ 💡 Recommended: Turn this ON if:                    │
│    • Your site is open to the public              │
│    • You're seeing spam or abuse                  │
│    • You have more than 100 visitors per day      │
│                                                     │
│    Turn this OFF if:                               │
│    • Your site is for internal company use only   │
│    • You're testing during development            │
│    • Your users complain it's annoying            │
│                                                     │
│ 📝 You'll need to sign up for a free account at    │
│    Google reCAPTCHA, hCaptcha, or Cloudflare       │
│    Turnstile to get the required keys.             │
└─────────────────────────────────────────────────────┘
```

***

### **Example 2: Rate Limit Setting**

**❌ BAD VERSION:**
```
Max requests per IP per hour: [ 5 ]
Configure rate limiting threshold
```

**✅ GOOD VERSION:**
```
┌─────────────────────────────────────────────────────┐
│ Maximum Emails Per Person (Hourly)                 │
│ [ 5 ] emails per hour                              │
│                                                     │
│ How many temporary email addresses one person can  │
│ create in one hour before being blocked.           │
│                                                     │
│ 📊 What different numbers mean:                     │
│                                                     │
│    • Set to 1:                                     │
│      VERY STRICT. Only 1 email per hour.           │
│      Use if you have serious spam problems.        │
│      Warning: Will frustrate real users who need   │
│      multiple emails for testing.                  │
│                                                     │
│    • Set to 5:                                     │
│      NORMAL (Recommended). 5 emails per hour.      │
│      Stops spam bots while allowing real people    │
│      to use your service normally.                 │
│                                                     │
│    • Set to 20:                                    │
│      LOOSE. 20 emails per hour.                    │
│      Use for internal company sites or testing.    │
│      Warning: Easy for spammers to abuse.          │
│                                                     │
│    • Set to 100:                                   │
│      VERY LOOSE. Almost no protection.             │
│      Only use if you trust all your users          │
│      (private internal site).                      │
│                                                     │
│ 💡 Recommended: Start with 5. If real users        │
│    complain they need more, increase to 10.        │
│    If you're getting spam, decrease to 3.          │
│                                                     │
│ ⏱️ The counter resets every hour. If someone        │
│    creates 5 emails at 2:00 PM, they can create   │
│    5 more starting at 3:00 PM.                     │
└─────────────────────────────────────────────────────┘
```

***

### **Example 3: Prohibited Words List**

**❌ BAD VERSION:**
```
Prohibited Terms
┌─────────────────┐
│ spam            │
│ drug            │
└─────────────────┘
Configure blacklist filter
```

**✅ GOOD VERSION:**
```
┌─────────────────────────────────────────────────────┐
│ 🚫 Blocked Words (Cannot Appear in Email Usernames)│
│                                                     │
│ ┌─────────────────────────────────────────────────┐ │
│ │ spam                                            │ │
│ │ scam                                            │ │
│ │ phish                                           │ │
│ │ drug                                            │ │
│ │ porn                                            │ │
│ │ hack                                            │ │
│ │ ...                                             │ │
│ └─────────────────────────────────────────────────┘ │
│ ℹ️ One word per line (press Enter after each word)  │
│                                                     │
│ 🎯 What this does:                                  │
│    Prevents people from creating email addresses   │
│    that contain these words.                       │
│                                                     │
│ 📧 Real-world examples:                             │
│    • If "spam" is blocked:                         │
│      ✅ "hello123@domain.com" → Allowed             │
│      ❌ "spammer@domain.com" → BLOCKED              │
│      ❌ "myspam99@domain.com" → BLOCKED             │
│                                                     │
│    • If "drug" is blocked:                         │
│      ✅ "test456@domain.com" → Allowed              │
│      ❌ "drugs4u@domain.com" → BLOCKED              │
│      ❌ "drugstore@domain.com" → BLOCKED            │
│      (blocks even if word is part of another word) │
│                                                     │
│ 💡 Why use this:                                    │
│    Keeps your service professional-looking and     │
│    prevents people from using it for illegal or    │
│    inappropriate purposes.                         │
│                                                     │
│ 📝 How to add more words:                           │
│    1. Click inside the box above                   │
│    2. Scroll to the bottom                         │
│    3. Type your word (lowercase, no spaces)        │
│    4. Press Enter to add more words                │
│    5. Click "Save Settings" at the bottom          │
│                                                     │
│ ⚠️ Be careful: Blocking common words like "test"   │
│    can prevent people from creating useful emails  │
│    like "test123@domain.com"                       │
│                                                     │
│ [Load Default List]  [Clear All]                   │
│ ℹ️ Load Default List = Fills in our recommended     │
│    list of 50 common spam/illegal words            │
└─────────────────────────────────────────────────────┘
```

***

## 🔄 BEFORE & AFTER COMPARISON

### **Setting: Email Lifetime**

**❌ BEFORE (Technical, unclear):**
```
Email TTL: [ 24 ] hours
Configure message retention policy
```

**✅ AFTER (Grandma-proof):**
```
┌─────────────────────────────────────────────────────┐
│ ⏰ How Long Emails Exist Before Being Deleted      │
│ [ 24 ] hours                                       │
│                                                     │
│ Temporary emails are automatically deleted after   │
│ this many hours. Users cannot access them anymore. │
│                                                     │
│ 📊 Time periods explained:                          │
│                                                     │
│    • 1 hour:                                       │
│      Very short. Good for quick tests or one-time  │
│      verification codes. Email disappears fast.    │
│                                                     │
│    • 24 hours (Recommended):                       │
│      One full day. Covers most use cases like      │
│      signing up for websites, receiving shipping   │
│      confirmations, etc.                           │
│                                                     │
│    • 168 hours (7 days):                           │
│      One week. Use if your users need access to    │
│      emails for longer (customer support, order    │
│      tracking that takes multiple days).           │
│                                                     │
│ 💡 Why delete emails:                               │
│    • Keeps your database small and fast           │
│    • Protects user privacy (old emails gone)      │
│    • Prevents your server from filling up         │
│                                                     │
│ ⏱️ Real example:                                    │
│    If set to 24 hours and someone creates an email│
│    on Monday at 3:00 PM, it will be deleted on    │
│    Tuesday at 3:00 PM. After that, they cannot    │
│    see any messages sent to that email.           │
│                                                     │
│ 🎯 Most common setting: 24 hours                    │
└─────────────────────────────────────────────────────┘
```

***

## 📐 LAYOUT GUIDELINES

### **Visual Hierarchy:**

1. **Setting Label** (Large, bold)
2. **Input Field / Checkbox** (Prominent, easy to click)
3. **One-line summary** (Directly below input)
4. **Detailed explanation** (Expandable section or always visible)
5. **Examples** (With icons: 📊)
6. **Recommendation** (With icon: 💡)
7. **Warnings** (With icon: ⚠️, red/orange color)

### **Spacing Rules:**

- Leave **16px minimum** between setting groups
- Use **borders or background colors** to separate sections
- Put **warning text in colored boxes** (light red/orange background)
- Use **consistent icon sizing** (20-24px)

### **Color Coding:**

- **Green** (✅): Positive outcomes, recommendations
- **Red** (❌): Warnings, disabled states, risks
- **Blue** (💡): Tips, information, help
- **Orange** (⚠️): Important warnings, caution
- **Gray**: Secondary information, examples

***

## ✅ FINAL CHECKLIST FOR BUILDERS

Before submitting any settings UI, answer YES to all:

- [ ] Can my grandmother understand what each setting does?
- [ ] Does every checkbox explain what happens when checked AND unchecked?
- [ ] Does every number field have examples of low/medium/high values?
- [ ] Does every dropdown explain each option individually?
- [ ] Do dangerous settings have clear warnings?
- [ ] Are recommendations provided for every setting?
- [ ] Are there zero acronyms or jargon words?
- [ ] Can a user make an informed decision without Googling anything?
- [ ] Would I feel confident using this interface if I had no technical knowledge?
- [ ] Have I tested this with someone who is NOT a developer?

***

## 🎓 TRAINING EXAMPLES

### **Practice Exercise:**

**Given this bad copy:**
```
☐ Enable DKIM validation
   Configure mail authentication protocol
```

**Your task:** Rewrite using grandma-proof principles.

**Good answer:**
```
┌─────────────────────────────────────────────────────┐
│ 🔒 Verify Sender Identity (Email Security)         │
│ ☐ Check if incoming emails are really from who     │
│    they claim to be                                 │
│                                                     │
│ Verifies that emails are actually sent by the      │
│ company they claim to be from (not fake/spam).     │
│                                                     │
│ ✅ When enabled:                                     │
│    • Emails claiming to be from "bank@chase.com"   │
│      are checked to make sure they're real         │
│    • Fake emails are marked or rejected            │
│    • Your users are protected from scams           │
│                                                     │
│ ❌ When disabled:                                    │
│    • All emails are accepted without checking      │
│    • Scammers can pretend to be anyone             │
│    • Users might receive phishing emails           │
│                                                     │
│ 💡 Recommended: Turn this ON for security.          │
│    Only turn OFF if you're having problems         │
│    receiving legitimate emails (rare).             │
│                                                     │
│ ℹ️ Technical name: DKIM Validation                  │
│    (You don't need to know this)                   │
└─────────────────────────────────────────────────────┘
```

***

## 🚀 IMPLEMENTATION MANDATE

**For ALL Builder LLMs:**

When creating any UI with settings, checkboxes, inputs, or options:

1. **STOP** and check: "Would my grandmother understand this?"
2. If NO → Rewrite using templates from this rulebook
3. **NEVER** submit settings UI without helper text
4. **ALWAYS** include consequences (what happens when enabled/disabled)
5. **ALWAYS** provide examples with real values
6. **ALWAYS** give recommendations (turn on/off/who should use)

***

## 📊 SUCCESS METRICS

A settings interface is successful when:

- **Zero support questions** about "What does this setting do?"
- **Users confidently enable/disable** features without fear
- **Non-technical users** can configure the system independently
- **Decision time < 30 seconds** per setting (no research needed)
- **Error rate < 5%** (users making wrong choices)

***

**END OF GRANDMA-PROOF UI COPY RULEBOOK**

***

**Remember:** If explaining a setting requires using words like "configure," "enable," "initialize," "integrate," or "advanced," you're not explaining it in plain English. Start over.

**Golden Rule:** "My 80-year-old grandma should be able to use this without calling me for help."

***

