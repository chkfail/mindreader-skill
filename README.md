<div align="center">

# 🔮 mindreader-skill

**Stop guessing what they really meant. Stop rehearsing in your head. Talk to their shadow first.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-AgentSkill-purple)](https://github.com/anthropics/claude-code)
[![Stars](https://img.shields.io/github/stars/chkfail/mindreader-skill?style=social)](https://github.com/chkfail/mindreader-skill)

[中文版 README](./README.zh.md) · [Demo](#-demo) · [Quickstart](#-quickstart) · [FAQ](#-faq)

> ⚠️ **This is a v0.1 toy project. Things will break. The ethics are unresolved on purpose. Read the [Why this exists](#-why-this-exists-and-why-its-built-the-way-it-is) section before starring.**

</div>

---

Build a **digital shadow** of anyone real — your ex, your boss, the person you can't read, a difficult client, your parents.

Then do three things with it:

🕯️ **Séance Mode `/mindreader seance`** — Pull up an old conversation. Ask the shadow: *"What were they actually thinking?"*

🎭 **Rehearsal Mode `/mindreader rehearse`** — Before you say it to the real person, run it past their shadow first.

📐 **Calibrate Mode `/mindreader calibrate`** — Feed in a real conversation. The shadow predicts the second half. See how close it gets.

> This is a **hypothesis generator**, not real mind-reading. It won't tell you "the truth." It will tell you **the possibilities you didn't think of.** That distinction matters. There's a whole section on it below.

---

## 🎬 Demo

### 🕯️ `/mindreader seance` — *"What did they actually mean?"*

You dig up a conversation from three months ago. You still can't figure out what they meant by *"whatever, it's fine."* Feed it in:

```
You          ❯ /mindreader seance

mindreader   ❯ Paste the conversation. Then tell me what you're stuck on.

You          ❯ [pastes 20 messages]
             ❯ I can't tell if "whatever, it's fine" was passive-aggressive
             ❯ or if she really didn't care anymore.

mindreader   ❯ I see 3 contradictory readings in these 20 messages.
             ❯ I don't know which one is true. You probably know better than I do.
             ❯
             ❯ ━━━ Reading A: She was angry (confidence ~40%)
             ❯ Evidence: msg #7 she opened up the weekend plan, you replied
             ❯           short. msg #12 ends with a period — in your prior
             ❯           chats, she only uses periods 3 times, all when upset.
             ❯ If this reading is right: she was waiting for you to push.
             ❯
             ❯ ━━━ Reading B: She was actually exhausted (confidence ~35%)
             ❯ Evidence: msg #3 mentions overtime. Reply intervals stretched
             ❯           from ~2min to ~18min by msg #15.
             ❯ If this reading is right: pushing would have made it worse.
             ❯
             ❯ ━━━ Reading C: She wasn't thinking that hard (confidence ~25%)
             ❯ Evidence: 4 prior instances of similar phrasing with no
             ❯           follow-up conflict. You may be projecting current
             ❯           anxiety backward onto a neutral moment.
             ❯
             ❯ ⚠️  I can make all three of these sound true. That's what
             ❯     LLMs are best at, and that's the trap. Treat this as a
             ❯     list of "possibilities I didn't consider," not an answer.
```

**Key design: the shadow won't give you one answer. It gives you three contradictory ones, with evidence, confidence levels, and a self-warning.** This is what separates this tool from a Magic 8-Ball. There's a whole section below on why this matters.

---

### 🎭 `/mindreader rehearse` — *"Run the conversation 100 times before it happens once."*

You want to ask your boss for a raise. You also know your boss is the kind of person who shuts down the moment they feel cornered. Run it past the shadow first:

```
You          ❯ /mindreader rehearse

mindreader   ❯ What's your goal? (one sentence)

You          ❯ Get a 20% raise without damaging the relationship.

mindreader   ❯ How are you planning to open?

You          ❯ "Hey, I think I've contributed a lot this year and I'd
             ❯  like to talk about my comp."

mindreader   ❯ Ran 5 simulated rounds. Goal achievement: 2/10.
             ❯
             ❯ ━━━ Shadow's response
             ❯ Shadow: "Contributed a lot? Like what specifically?"
             ❯ Shadow's inner monologue: (here's another one who thinks
             ❯                            they're indispensable)
             ❯
             ❯ ━━━ Failure mode
             ❯ You triggered their "being extracted from" defense. In their
             ❯ mental model, "I contributed a lot" is a conclusion, not an
             ❯ argument. They want the argument first.
             ❯
             ❯ ━━━ Suggested rewrite (estimated achievement: 7/10)
             ❯ "Hey, I'd love to walk through the projects I shipped this
             ❯  year and talk about where I should focus next year."
             ❯
             ❯ This version routes around the trigger word "raise," reframes
             ❯ the conversation from "I want" to "let's align," which fits
             ❯ their communication style. Bring up comp in round two, after
             ❯ they've already nodded along to the framing.
             ❯
             ❯ ⚠️  The shadow is built from the chat logs you gave me. If
             ❯     the logs are thin, or only cover one type of situation,
             ❯     the simulation will be off. This is a rehearsal, not a
             ❯     script. Stay present in the real conversation.
```

**Key design: every round labels the shadow's "inner monologue," and every output ships with a fidelity warning.** Those two details are what separate entertainment from a serious tool.

---

### 📐 `/mindreader calibrate` — *"How well does my shadow actually know them?"*

You've built a shadow of your partner. But how accurate is it, really? Feed in a real conversation and find out:

```
You          ❯ /mindreader calibrate

mindreader   ❯ Paste a complete real conversation (at least 10 messages).

You          ❯ [pastes 30 messages]

mindreader   ❯ Got 30 messages.
             ❯
             ❯ Split plan:
             ❯   First half: messages 1–15 (fed to shadow)
             ❯   Second half: messages 16–30 (shadow predicts)
             ❯
             ❯ Start calibration?

You          ❯ Go.

mindreader   ❯ ━━━ Shadow Calibration Report ━━━
             ❯
             ❯ 📊 Score: 7.2/10
             ❯
             ❯ 30 messages (15 context / 15 predicted)
             ❯ Shadow predicted 8 of their replies
             ❯
             ❯ ━━━ Side-by-side ━━━
             ❯
             ❯ Message #17 (them):
             ❯   Real:   "lol ok whatever you say"
             ❯   Shadow: "haha sure sure"
             ❯   Score: 8/10
             ❯   Analysis: Same dismissive-affectionate tone.
             ❯             Shadow nailed the vibe, missed the
             ❯             specific phrasing.
             ❯
             ❯ Message #22 (them):
             ❯   Real:   "can we not do this rn"
             ❯   Shadow: "I don't want to talk about this"
             ❯   Score: 7/10
             ❯   Analysis: Same avoidance, but shadow was too
             ❯             formal — real version is more clipped.
             ❯
             ❯ ━━━ Dimension Scores ━━━
             ❯
             ❯   Semantic direction: 7.8/10  ████████░░
             ❯   Emotional tone:     7.5/10  ████████░░
             ❯   Expression style:   6.2/10  ██████░░░░
             ❯   Behavioral choice:  7.0/10  ███████░░░
             ❯
             ❯ ━━━ Diagnosis ━━━
             ❯
             ❯ Strengths: Shadow reads their emotional direction
             ❯   well — knows when they'll deflect vs. engage.
             ❯ Blind spots: Expression style is off — shadow is
             ❯   too "proper," real person uses more slang/abbrevs.
             ❯ Suggestion: Feed more casual/daily chat logs to
             ❯   calibrate the shadow's register.
             ❯
             ❯ ⚠️  This score doesn't mean "how well you know them."
             ❯     It means: given the data you fed the shadow, how
             ❯     well can it reproduce their expression. Biased
             ❯     data → biased score. Complete data → still maybe
             ❯     biased, because people aren't models.
             ❯
             ❯ 📸 Screenshot and share:
             ❯    "My shadow scored 72% — how about yours?"
             ❯    #mindreader #digitalshadow
```

**Key design: the score is decomposed into four dimensions with side-by-side comparisons, so you see _where_ the shadow is strong and _where_ it drifts.** And of course, it ships with a warning that the score measures the shadow's data, not your understanding.

---

## 🧠 Why this exists (and why it's built the way it is)

Let's be direct: this project sits in an ethical gray zone. We know.

**About Séance Mode:**

An LLM cannot "know" what another person was thinking. It only sees the corpus you gave it and the description you wrote. So if it gives you **a single "truth,"** that truth is 100% a hallucination — a repackaging of **what you already half-suspected** in their voice.

That's why `/seance` is hard-wired to output **multiple contradictory readings + evidence + confidence + a self-warning**. The design goal is to **loosen** your fixed narrative, not **harden** it. If you want a confident single answer, this tool will disappoint you. That's intentional.

**About Rehearsal Mode:**

There is a gap between "phrasing that works on the shadow" and "phrasing that works on the real person." That gap equals the sum of every way the shadow model differs from the actual human. The harder you optimize, the more you converge on sentences that **exploit the model's blind spots** instead of **actually landing on the person**. This is Goodhart's law, and in this domain it bites hard.

That's why `/rehearse` won't let you run 1000 trials and pick the winner. It caps at 5 rounds and forces a reminder that **this is rehearsal, not a script**. Rehearsal exists to make you **less reactive in the real moment**, not to pre-write your lines.

**Meta-criticism:**

Yes, treating people as systems to reverse-engineer is itself a relational stance. Even if they don't know, you do. This tool will change how you see the people in your life. That's a real cost. We're not pretending it isn't.

If you read all three of those paragraphs and still want to use it: welcome. If you read them and think *"this thing should be set on fire"*: also welcome. The issue tracker is open. We reply.

---

## 🚀 Quickstart

```bash
# Install (Claude Code, global)
git clone https://github.com/chkfail/mindreader-skill ~/.claude/skills/mindreader

# Or install per-project
mkdir -p .claude/skills && \
  git clone https://github.com/chkfail/mindreader-skill .claude/skills/mindreader
```

**First run:**

```
/mindreader build         # Build a new shadow
/mindreader seance        # Séance mode
/mindreader rehearse      # Rehearsal mode
/mindreader calibrate     # Calibrate shadow accuracy
/mindreader list          # List all shadows you've built
/mindreader forget <n>    # Delete a shadow
```

**Feeding data:**

- Paste raw chat logs (any format — the shadow will parse it)
- Or import an existing persona file from [ex-skill](https://github.com/titanwings/ex-skill)
- Or just describe the person (lower quality, but it works)

---

## 🧬 How it works

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   Your chat logs + your description                     │
│            │                                            │
│            ▼                                            │
│   ┌─────────────────┐                                   │
│   │ Persona Builder │  (reuses ex-skill's 6-layer model)│
│   └─────────────────┘                                   │
│            │                                            │
│            ▼                                            │
│   ┌─────────────────┐                                   │
│   │  Shadow object  │                                   │
│   └─────────────────┘                                   │
│       │           │          │                           │
│       ▼           ▼          ▼                           │
│  ┌─────────┐ ┌──────────┐ ┌────────────┐                │
│  │ /seance │ │/rehearse │ │/calibrate  │                │
│  └─────────┘ └──────────┘ └────────────┘                │
│  multi-reading 5 rounds +  split & predict              │
│  + evidence    inner mono  + score + share              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

The shadow's persona structure is based on [ex-skill](https://github.com/titanwings/ex-skill)'s 6-layer model (Core Patterns → Identity → Expression → Emotional Behavior → Conflict & Boundaries → Tripwires). Credit where it's due.

---

## ❓ FAQ

**Q: Is this legal?**
A: The tool is. How you use it is on you. Don't feed it chat logs that aren't yours. Don't use it to harass, manipulate, or deceive anyone. The legal and ethical line is yours to hold.

**Q: How accurate is it?**
A: Unknown and unmeasurable, because there is no ground truth. This is a hypothesis generator, not a prediction engine. If you want "scientific accuracy," this isn't your project.

**Q: What's the relationship to ex-skill?**
A: ex-skill is the spiritual ancestor. The persona generation method is reused directly. The difference: ex-skill is for people who have already left your life (grief). mindreader is for people who are still in it (cognition). If you only want to talk to your ex's shadow, just use ex-skill — it does that better.

**Q: Can I use this on my boss?**
A: Technically yes. Psychologically, think it through: when you start treating everyone around you as a system to reverse-engineer, you also start becoming that system. This isn't me telling you to stop. It's me telling you to notice.

**Q: Won't this get used to manipulate people?**
A: Yes. Any tool that helps you understand humans can be used to manipulate them — Sun Tzu, *How to Win Friends*, every psychology textbook. Our mitigations: (1) forced multi-reading output, which kills the "I cracked them" illusion; (2) Rehearsal Mode caps at 5 rounds to limit overfitting; (3) this entire README. The rest is on you.

**Q: Where's my data stored? Does it get uploaded?**
A: 100% local. Shadow files live under `~/.claude/skills/mindreader/shadows/`. No server, no telemetry, no cloud. If you delete the file, it's gone.

**Q: Does it work in languages other than English?**
A: Yes. Prompts are bilingual (EN/中文), and shadows can be built in any language. Documentation is currently EN + 中文. PRs for other languages welcome.

**Q: Can the shadow be wrong about the real person in a way that hurts me?**
A: Yes, easily. Especially if the chat logs only cover one type of situation (e.g., only conflict messages, or only flirty ones). The shadow will overfit to that slice and confidently extrapolate. The fidelity warnings in every output are not boilerplate — they're load-bearing. Read them.

---

## 🗺️ Roadmap

- [x] v0.1 — Séance + Rehearsal MVP
- [ ] v0.2 — Calibrate Mode + Multi-shadow management + version rollback
- [ ] v0.3 — Shadow journal: let the shadow write its own take on you
- [ ] v0.4 — Shadow-of-the-shadow: let the shadow predict what you'll do next, score it against reality
- [ ] v0.5 — Shadow mirror: the shadow builds a reverse-portrait of YOU from the same chat logs — see yourself through their eyes
- [ ] v0.6 — Reverse rehearsal: the shadow rehearses how THEY would approach YOU about something — discover the conversations they never started
- [ ] v0.7 — Shadow drift: feed conversations from different time periods, watch how the person changed over months or years

---

## 🤝 Contributing

This is a v0.1 demo. Bugs are guaranteed. Design will have holes. PRs, issues, criticism (technical or ethical) all welcome. We aim to reply within 48 hours.

Especially welcome:

- New persona data source adapters
- Better prompt templates
- **Failure cases** — seriously, failure cases are more valuable than success cases for this project
- Translations into any language

---

## 🙏 Credits

- [ex-skill](https://github.com/titanwings/ex-skill) by [@titanwings](https://github.com/titanwings) — the spiritual ancestor and the source of the persona methodology
- [AgentSkills](https://github.com/anthropics/claude-code) open standard
- Everyone who showed up in the issue tracker to yell at us and stayed to help fix it

---

## 📜 License

MIT. Take it, use it, you're on your own if anything goes sideways.

---

<div align="center">

**Built by [@chkfail](https://github.com/chkfail) · [X](https://x.com/__chk_fail)**

*If this project made you uncomfortable, that's the point. If it made you star it anyway, thank you.*

</div>