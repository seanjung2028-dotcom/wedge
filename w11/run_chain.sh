#!/bin/bash
# Week 11 line pipeline, whole slate, in order (Tue Nov 17 evening). Pull first: pull1117pm/raw/<SERIES>.txt from the browser,
# then `python3 pull1117pm/convert.py`. Usage: W11_PULL=pull1117pm bash w11/run_chain.sh
set -e
W=/home/claude/wedger
export W11_PULL=${W11_PULL:-pull1117pm}
cd $W/w11 && python3 build_inputs.py | tail -3
cd $W/mom && python3 pg_next_w11.py 2>&1 | tail -1 | cut -c1-160
cd $W/arch && python3 defadj_w11.py 2>&1 | tail -1 | cut -c1-160 && python3 build_feat_w11.py 2>&1 | tail -1 | cut -c1-160
cd $W/bt && python3 rff_w11.py 2>&1 | tail -1 | cut -c1-160
cd $W/rh
for s in w11_events w11_analyze w11_build_inband w11_categorize w11_atd w11_keep_certs w11_totals w11_splits w11_matchup; do echo "== $s"; python3 $s.py 2>&1 | tail -2 | cut -c1-220; done
cd $W/arch && python3 now_w11.py > /dev/null 2>&1 && echo "== roles ok"
cd $W/rh
for s in w11_reads_cand w11_model w11_proj_exp w11_build_all w11_injflags w11_game_reads; do echo "== $s"; python3 $s.py 2>&1 | tail -3 | cut -c1-220; done
cd $W/v2 && echo "== data_v2_w11" && python3 data_v2_w11.py 2>&1 | tail -2 | cut -c1-220
cd $W/final11 && echo "== final11" && python3 build.py 2>&1 | tail -6 | cut -c1-220 && python3 make_final_js.py 2>&1 | tail -2 | cut -c1-220
