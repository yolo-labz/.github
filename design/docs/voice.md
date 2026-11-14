# Voice

Anything a reader can see sounds like one person writing plainly: what broke, what fixed it, with the number.
The long form is the blog's `docs/voice.md` and its `scripts/check-voice.sh`.

**Rules**
- No em dash, and no en dash or spaced hyphen standing in for one. Split the sentence, or use a comma or a colon.
- Concrete over abstract. A claim points at a commit, a log line or a measurement, or it is cut.
- No signposting, no manner words, no three-item flourishes, no "not X, but Y" reveals.
- Say nothing about how our own images, copy or code were made. A product that works with a model still says so.
- Dates are DD/MM/YYYY in text, 24-hour time.

**Right:** "The nightly suite was red from 08/11 to 13/11: four tests need a model the runner does not have."
**Wrong:** "We're excited to share a robust, comprehensive solution to flaky tests, seamlessly leveraging the runner."

**Right:** "Alerts stay on. Version updates are off, because the mirror closes every pull request."
**Wrong:** the same two facts joined by an em dash, with the reason as an aside.
