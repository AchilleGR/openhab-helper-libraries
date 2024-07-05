Changes
=======

The original changelog before this fork is included in the file `CHANGELOG_ORIGINAL.md`

Jul 5, 2024
-----------
- Added core.action library, API subject to change.
- Added core.action.timers, a convienence interface over the Timer and ScriptExecution actions.

Jul 4, 2024
-----------
- Fork of repository.
- Repaired `100_DirectoryTrigger.py`, scripts now hot-reload again.
- Check cron expressions with CronAdjuster if it is available.
- Completely removed the `set_uid_prefix` functionality. It does not make sense now that rule UIDs are intended to be immutable.
- Exposed every available current action in actions.py. They are exposed in a dynamic way, so this should retain backwards compatibility.
- Added core.util library, API subject to change.
