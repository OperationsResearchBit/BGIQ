# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (C) 2026 bgtools contributors
"""buy_delta: how much would buying one tavern minion change your next fight?

delta.py   the number itself (your board + one minion vs one opponent board)
field.py   the same against typical opponent boards, before any board has been seen
shop.py    the number for every minion that could appear, worked out once per board state
preview.py try it on boards you type in (used by `python -m bgtools buydeltapreview`)

Pure calculations on core data and simcore. The screen lives in ui/buy_delta_view.py and the
commands in commands/cmd_buydelta.py and commands/cmd_buydeltapreview.py.
"""
