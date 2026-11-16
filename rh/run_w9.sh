#!/bin/bash
# Week 9 line pipeline, in order (Wed Nov 4). Inputs: rh/rh_w9_robinhood_raw.json, rh/kalshi_props_w9.json, rh/an_w9_raw.json,
# dl8/injuries_w9.csv (pull1104/build_inj.py), rh/weather_w9.json, rh/force_out_w9.json.
set -e
cd /home/claude/wedger/w9 && python3 build_inputs.py | tail -2
cd /home/claude/wedger/rh
for s in w9_events w9_analyze w9_build_inband w9_categorize w9_atd w9_keep_certs w9_totals w9_matchup; do echo "== $s"; python3 $s.py 2>&1 | tail -2 | cut -c1-200; done
cd /home/claude/wedger/arch && python3 now_w9.py > /dev/null 2>&1 && echo "== roles ok"
cd /home/claude/wedger/rh
for s in w9_reads_cand w9_model w9_proj_exp w9_build_all w9_injflags; do echo "== $s"; python3 $s.py 2>&1 | tail -4 | cut -c1-200; done
