# Runtime And APNG Case Study Notes

This file intentionally contains only public-safe notes. It avoids private local paths, personal authorship, repository statistics, and unpublished asset references.

## What To Learn From The APNG Case Study

- Keep a stable reference image for each character.
- Split states by first/last-frame relationship:
  - A: looping, first frame equals last frame.
  - B: one-shot return, first frame equals last frame.
  - C: transition, first frame differs from last frame.
- Use a consistent chroma key color across reference image, prompt, and post-processing.
- Budget for reruns; generated video is probabilistic.
- Package finished assets behind a generic runtime state map.

## Runtime Takeaways

A desktop-pet runtime usually needs:

- a state registry;
- files for core states such as idle, typing, thinking, sleeping, happy, notification, and error;
- optional mini/dock states;
- event-to-state mapping;
- a way to switch SVG/APNG assets at runtime.

Use `shared/state-map.md` as the public reference for this repository.

## What Not To Copy

- Do not copy existing product character assets.
- Do not reuse a product-specific `CHARACTER_PREFIX`.
- Do not assume private runtime source files are available to public users.

## Relevant pet-forge Files

- `routes/apng/prompts/template.js`
- `routes/apng/conventions/workflow.md`
- `routes/apng/conventions/loop-and-anchoring.md`
- `routes/apng/tools/`
- `shared/state-map.md`
