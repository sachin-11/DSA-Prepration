// ============================================================
// Twilio Interview Prep — 22-09-2026
// Format: Question -> Answer (THEORY) -> code example jahan applicable
// Node.js context mein (twilio npm package) kyunki backend stack Node hai.
// ============================================================


// ------------------------------------------------------------
// SECTION 1: BASICS
// ------------------------------------------------------------

// Q1. Twilio kya hai aur ye kaise kaam karta hai (high level)?
//
// A: Twilio ek cloud communications platform (CPaaS) hai jo APIs
// provide karta hai SMS, Voice calls, WhatsApp, Video, Email (SendGrid)
// jaisi communication features ko apni app mein integrate karne ke
// liye — bina khud telecom infrastructure (carrier relationships,
// SMPP connections, PBX) build kiye. Tumhari app Twilio ke REST API
// ko HTTP request bhejti hai (jaise "SMS bhejo"), Twilio backend
// telecom carriers ke saath integrate hai aur actual message/call
// deliver karta hai. Incoming messages/calls ke liye Twilio tumhare
// server pe "webhook" (HTTP callback) hit karta hai.


// ------------------------------------------------------------
// Q2. Account SID aur Auth Token kya hote hain? Inhe secure kaise
//     rakhte ho?
//
// A: Account SID Twilio account ka unique public identifier hai
// (username jaisa), Auth Token secret credential hai (password jaisa)
// jo API requests authenticate karne ke liye use hota hai (Basic Auth
// ya request signing). Best practices:
// - Auth Token ko kabhi client-side code/git repo mein commit mat karo
// - Environment variables mein rakho (.env, secrets manager)
// - Twilio "API Keys" use karo Auth Token ke bajaye production mein —
//   inhe individually revoke kiya ja sakta hai bina main Auth Token
//   rotate kiye (jaise ek compromised microservice ka key revoke karo)
// - Auth Token leak ho jaaye to turant Twilio console se rotate karo

const twilio = require("twilio");
const client = twilio(process.env.TWILIO_ACCOUNT_SID, process.env.TWILIO_AUTH_TOKEN);


// ------------------------------------------------------------
// SECTION 2: MESSAGING (SMS/WhatsApp)
// ------------------------------------------------------------

// Q3. Twilio se SMS kaise bhejte ho? Code likho.
//
// A: messages.create() call karte ho with `to`, `from` (Twilio-owned
// number ya Messaging Service SID), aur `body`.

async function sendSMS(to, body) {
  const message = await client.messages.create({
    to,
    from: process.env.TWILIO_PHONE_NUMBER,
    body,
  });
  return message.sid; // unique message identifier, status tracking ke liye
}


// ------------------------------------------------------------
// Q4. Messaging Service kya hota hai aur single phone number se
//     directly bhejne se better kyun hai (production mein)?
//
// A: Messaging Service ek pool of phone numbers/sender IDs ko group
// karta hai ek logical unit mein. Benefits:
// - Sticky sender: same user ko hamesha same number se message jaaye
//   (conversation continuity)
// - Automatic number selection/load distribution across pool
// - Built-in features: link shortening, opt-out (STOP/HELP) handling
//   automatically, geographic number matching (compliance ke liye)
// - Scaling: high volume pe multiple numbers ke beech load balance,
//   rate limits (throughput) avoid karne ke liye


// ------------------------------------------------------------
// Q5. WhatsApp messaging Twilio ke through SMS se kaise different hai?
//     "24-hour session window" kya hota hai?
//
// A: WhatsApp Business API strict rules follow karta hai:
// - Free-form messages sirf user ke last message ke 24 hours ke andar
//   bhej sakte ho ("session window")
// - Uske baad sirf pre-approved "Message Templates" (Meta se approve
//   hue) use kar sakte ho — jaise OTP templates, notification templates
// - Opt-in mandatory hai (user ne pehle WhatsApp pe message kiya ho ya
//   explicitly consent diya ho)
// Twilio Content API templates manage karne ke liye use hoti hai.

async function sendWhatsApp(to, body) {
  return client.messages.create({
    to: `whatsapp:${to}`,
    from: `whatsapp:${process.env.TWILIO_WHATSAPP_NUMBER}`,
    body,
  });
}


// ------------------------------------------------------------
// SECTION 3: WEBHOOKS & TwiML
// ------------------------------------------------------------

// Q6. Twilio webhooks kaise kaam karte hain? Incoming SMS/call ko
//     apne server pe kaise handle karte ho?
//
// A: Jab koi tumhare Twilio number pe SMS/call karta hai, Twilio
// tumhare configured webhook URL (Twilio console/API mein set kiya
// hua) ko HTTP POST request bhejta hai with data (From, To, Body,
// CallSid, etc.). Tumhara server ko response mein TwiML (XML) return
// karna hota hai jo batata hai Twilio ko kya karna hai (message bhejo,
// call ko forward karo, IVR menu play karo).

const express = require("express");
const { MessagingResponse, VoiceResponse } = twilio.twiml;
const app = express();
app.use(express.urlencoded({ extended: false }));

app.post("/webhooks/sms", (req, res) => {
  const incomingMsg = req.body.Body;
  const twiml = new MessagingResponse();
  twiml.message(`Aapka message mila: "${incomingMsg}"`);
  res.type("text/xml").send(twiml.toString());
});

app.post("/webhooks/voice", (req, res) => {
  const twiml = new VoiceResponse();
  twiml.say({ voice: "alice" }, "Namaste, humein call karne ke liye dhanyawad.");
  twiml.gather({ numDigits: 1, action: "/webhooks/voice/menu" });
  res.type("text/xml").send(twiml.toString());
});


// ------------------------------------------------------------
// Q7. Webhook requests genuinely Twilio se aa rahe hain, ye kaise
//     verify karoge? (Security — important senior-level question)
//
// A: Twilio har webhook request mein `X-Twilio-Signature` header
// bhejta hai — jo request URL + POST params + Auth Token ka HMAC-SHA1
// hash hota hai. Server pe usi Auth Token se signature recompute
// karke compare karo. Agar validate nahi karte to koi bhi attacker
// tumhare webhook endpoint pe fake requests bhej sakta hai (jaise
// fake "payment confirmed" SMS trigger karwana). twilio npm package
// mein built-in middleware milta hai.

const { webhook } = twilio;

app.post(
  "/webhooks/sms",
  webhook(process.env.TWILIO_AUTH_TOKEN), // validates X-Twilio-Signature
  (req, res) => {
    // yahan tak pahuncha matlab request genuinely Twilio se hai
  }
);


// ------------------------------------------------------------
// Q8. Message/call delivery status kaise track karte ho? Status
//     callbacks kya hain?
//
// A: `statusCallback` URL pass karo message.create() mein — Twilio
// message ke lifecycle ke har stage pe (queued -> sent -> delivered ->
// failed/undelivered) tumhare server ko webhook POST bhejega with
// MessageStatus. Isse tum apni DB mein delivery status track kar
// sakte ho, retry logic implement kar sakte ho failed messages ke liye.

async function sendTrackedSMS(to, body) {
  return client.messages.create({
    to,
    from: process.env.TWILIO_PHONE_NUMBER,
    body,
    statusCallback: "https://myapp.com/webhooks/sms-status",
  });
}

app.post("/webhooks/sms-status", (req, res) => {
  const { MessageSid, MessageStatus, ErrorCode } = req.body;
  // DB mein update karo: delivered / failed / undelivered
  if (MessageStatus === "failed" || MessageStatus === "undelivered") {
    console.error(`Message ${MessageSid} failed: error ${ErrorCode}`);
  }
  res.sendStatus(200);
});


// ------------------------------------------------------------
// SECTION 4: OTP / VERIFY, VOICE, SCALING
// ------------------------------------------------------------

// Q9. OTP (One-Time Password) verification khud messages.create() se
//     implement karoge ya Twilio Verify API use karoge? Farak kya hai?
//
// A: Twilio VERIFY API use karna better hai raw SMS se OTP bhejne ke
// muqable, kyunki:
// - OTP generation, expiry, retry, rate-limiting sab built-in hai
//   (khud implement nahi karna padta)
// - Fraud prevention built-in (SIM-swap detection, geographic risk checks)
// - Multi-channel support (SMS, Voice, WhatsApp, Email) same API se
// - Automatic locale-based message formatting

async function sendOTP(phoneNumber) {
  return client.verify.v2.services(process.env.TWILIO_VERIFY_SERVICE_SID)
    .verifications.create({ to: phoneNumber, channel: "sms" });
}

async function checkOTP(phoneNumber, code) {
  const result = await client.verify.v2.services(process.env.TWILIO_VERIFY_SERVICE_SID)
    .verificationChecks.create({ to: phoneNumber, code });
  return result.status === "approved";
}


// ------------------------------------------------------------
// Q10. Programmable Voice mein IVR (Interactive Voice Response) menu
//      kaise banate ho? <Gather> verb kya karta hai?
//
// A: <Gather> caller se DTMF digits (keypad press) ya speech input
// collect karta hai, phir specified `action` URL pe POST karta hai
// with collected input — jaha tum next TwiML decide karte ho (routing
// logic). Nested <Gather> se multi-level menus banate hain.

app.post("/webhooks/voice/menu", (req, res) => {
  const digit = req.body.Digits;
  const twiml = new VoiceResponse();
  if (digit === "1") {
    twiml.say("Sales department se connect kar rahe hain.");
    twiml.dial("+911234567890");
  } else if (digit === "2") {
    twiml.say("Support department se connect kar rahe hain.");
    twiml.dial("+919876543210");
  } else {
    twiml.say("Galat option, dobara try karein.");
    twiml.redirect("/webhooks/voice");
  }
  res.type("text/xml").send(twiml.toString());
});


// ------------------------------------------------------------
// Q11. Twilio API calls mein rate limits / errors handle karne ka
//      best practice kya hai? (retry, backoff)
//
// A: Twilio REST API rate limits enforce karta hai (per account/number
// throughput limits). Errors do categories mein aate hain:
// - Retryable (5xx server errors, network timeouts, rate limit 429) —
//   exponential backoff ke saath retry karo
// - Non-retryable (4xx client errors jaise invalid phone number,
//   unverified number in trial account) — retry karne se fayda nahi,
//   log karo aur alert raise karo
// Twilio SDK mein `RestException` catch karke `error.status`/`error.code`
// check karte hain.

async function sendSMSWithRetry(to, body, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await client.messages.create({ to, from: process.env.TWILIO_PHONE_NUMBER, body });
    } catch (err) {
      const isRetryable = err.status >= 500 || err.status === 429;
      if (!isRetryable || attempt === maxRetries) throw err;
      const backoff = 2 ** attempt * 1000;
      await new Promise((r) => setTimeout(r, backoff));
    }
  }
}


// ------------------------------------------------------------
// Q12. High-volume messaging application (jaise notification system,
//      lakhs of users) design karna ho to architecture kaisi hogi?
//
// A: Direct/synchronous Twilio calls request path mein karna anti-
// pattern hai high volume ke liye. Better design:
// 1. API request aane pe message ko QUEUE mein daalo (SQS/RabbitMQ/
//    BullMQ+Redis) — turant 202 Accepted return karo
// 2. Background workers queue se consume karke Twilio ko actual
//    call karein — concurrency control karo (Twilio throughput limits
//    ke andar rehne ke liye)
// 3. Messaging Service (number pool) use karo throughput scale karne
//    ke liye (single number ~1 msg/sec limit hota hai typically)
// 4. Idempotency: same message dobara queue se process na ho (dedupe
//    key/idempotency key use karo)
// 5. Status callbacks se delivery tracking, failed messages ko dead-
//    letter queue mein daalo retry/alerting ke liye
// 6. Webhook signature validation (Q7) + rate limiting apne endpoints pe


// ------------------------------------------------------------
// Q13. Trial account vs Production account — key limitations jo
//      interview mein "gotcha" ki tarah poochi jaati hain?
//
// A: Trial account mein:
// - Sirf VERIFIED phone numbers pe SMS/call bhej sakte ho (production
//   mein kisi bhi number pe)
// - Har outgoing message mein "Sent from a Twilio trial account" prefix
//   automatically add hota hai
// - Limited trial balance/credit
// Production ke liye account upgrade karna padta hai (billing add
// karke) — plus regulatory compliance: kuch countries mein SMS bhejne
// ke liye number registration (A2P 10DLC in US, sender ID registration
// in India/other countries) mandatory hota hai warna messages filter
// ho jaate hain carrier ke through.
