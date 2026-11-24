#!/bin/bash
# Week 12 line pipeline, whole slate, in order (Tue Nov 17 evening). Pull first: pull1124/raw/<SERIES>.txt from the browser,
# then `python3 pull1124/convert.py`. Usage: W12_PULL=pull1124 bash w12/run_chain.sh
set -e
W=/home/claude/wedger
export W12_PULL=${W12_PULL:-pull1124}
cd $W/w12 && python3 build_inputs.py | tail -3
cd $W/mom && python3 pg_next_w12.py 2>&1 | tail -1 | cut -c1-160
cd $W/arch && python3 defadj_w12.py 2>&1 | tail -1 | cut -c1-160 && python3 build_feat_w12.py 2>&1 | tail -1 | cut -c1-160
cd $W/bt && python3 rff_w12.py 2>&1 | tail -1 | cut -c1-160
cd $W/rh
for s in w12_events w12_analyze w12_build_inband w12_categorize w12_atd w12_keep_certs w12_totals w12_splits w12_matchup; do echo "== $s"; python3 $s.py 2>&1 | tail -2 | cut -c1-220; done
cd $W/arch && python3 now_w12.py > /dev/null 2>&1 && echo "== roles ok"
cd $W/rh
for s in w12_reads_cand w12_model w12_proj_exp w12_build_all w12_injflags w12_game_reads; do echo "== $s"; python3 $s.py 2>&1 | tail -3 | cut -c1-220; done
cd $W/v2 && echo "== data_v2_w12" && python3 data_v2_w12.py 2>&1 | tail -2 | cut -c1-220
cd $W/final12 && echo "== final12" && python3 build.py 2>&1 | tail -6 | cut -c1-220 && python3 make_final_js.py 2>&1 | tail -2 | cut -c1-220
