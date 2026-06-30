# Electron Runtime Case Study Notes

This file intentionally contains only public-safe notes. It avoids private local
paths, personal authorship, account handles, repository statistics, and
unpublished asset references. It describes the *method* used to take one
finished pixel-style pet from a set of states to a live desktop widget wired to
an AI coding agent — not the specific product, its name, or its assets.

## The Path This Case Followed

1. Finished a small set of self-contained states first (idle, typing, thinking,
   sleeping, happy), then added feedback states (notification, error, carrying).
2. Did **not** adopt an existing pet host. Built a minimal Electron widget
   instead, reusing only the idea of a theme manifest (state name -> file) and an
   event-to-state map.
3. Kept each state as a self-contained `.svg.html` so the widget could load it
   directly and the inline animation survived with zero rework.
4. Wired the agent's lifecycle hooks to a tiny local HTTP server inside the
   widget; each event maps to one `curl` call.
5. Packaged, deployed, then drove states manually to verify the running target —
   not just a successful build.

## What To Learn From This Case

- A usable runtime is only four parts: a transparent always-on-top window, a
  state loader, a local control server, and event-to-state hooks. Resist adding
  more before those four work end to end.
- Keep window behavior in the main process, character performance in the state
  file, and event translation in the hooks. Each part staying in its lane is
  what keeps the system debuggable.
- Make the theme manifest the single source of truth for state *behavior*, not
  just state *files*. Classifying which states are "busy" (never auto-sleep) and
  which are "momentary" (auto-return to idle) belongs in one config that both the
  main process and the renderer derive from.
- Verify on the running widget, not the source files. Source proves the edit;
  the runtime path proves deployment and mapping.

## State-Machine Takeaways

- Split states into three classes: busy, resting, and momentary. Most runtime
  bugs come from a class boundary being wrong.
- Do not infer "the user is waiting" from a stalled timer. A long build or test
  legitimately produces no new events for many seconds; a timeout-based fallback
  will misread that as waiting and flip to a notification state. Drive the
  notification state from a real "needs input" event instead.
- Do not auto-sleep while a busy state is active. "No new event for N minutes"
  is a reasonable idle rule for resting states, but a single long task can starve
  events while real work is happening. Stop the sleep timer during busy states.
- General rule: if a real event can tell you what is happening, do not guess from
  elapsed time.

## Packaging And Deployment Pitfalls (Generic)

- An Electron-based host application can inject an environment flag that makes a
  child-launched Electron executable run as plain Node and crash on startup.
  Launch the widget from a clean desktop shell, or clear that flag first.
- The packaged application archive is bound to its runtime binary. After changing
  runtime code, repackage and deploy the whole output together; swapping only the
  archive against an old binary can cause a silent startup crash.
- Launch the widget through the desktop file manager rather than as a direct
  child of a hook, so it detaches from the hook's process tree and inherits a
  clean environment.
- Kill old instances before repackaging; a running instance locks output files
  and breaks the build.
- Keep hook commands as plain commands. Wrapping them in an interactive shell
  invocation can cause some agent shells to rewrite them and never run the script.

## What Not To Copy

- Do not copy a finished character, its palette, eye design, or named product
  identity.
- Do not assume private runtime source files are available to public users.
- Use the method to wire your own character's states to your own runtime.

## Relevant pet-forge Files

- `shared/runtime-build.md`
- `shared/state-map.md`
- `routes/svg/conventions/single-file.md`
- `examples/svg-case-study-notes.md`
