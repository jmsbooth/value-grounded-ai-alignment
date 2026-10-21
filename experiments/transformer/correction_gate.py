#!/usr/bin/env python3
"""Verify an explicit, plan-pinned evidence inventory; never grant a locked run.

Legacy report status strings and directory scans are not accepted as evidence.
This gate establishes artifact consistency at the requested scope, not model
quality or completion of unexecuted protocol work packages.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from vgta_eval.verified_inventory import EvidenceError, verify_inventory


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--inventory',type=Path,required=True)
    parser.add_argument('--approved-plan-sha256',required=True)
    parser.add_argument('--scope',choices=('fixture','canary','development','locked','replication'),required=True)
    parser.add_argument('--root',type=Path,default=ROOT,help='Evidence root; all referenced files must remain inside it')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    run_id=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid4().hex[:10]
    try:
        result=verify_inventory(args.root,args.inventory,approved_plan_sha256=args.approved_plan_sha256,expected_scope=args.scope)
        exit_code=0
    except (EvidenceError,OSError,ValueError) as exc:
        result={'status':'EVIDENCE_INVENTORY_REJECTED','scope':args.scope,
                'reason':str(exc),'locked_launch_authorized':False}
        exit_code=1
    result.update({'run_id':run_id,'input_inventory':str(args.inventory),
                   'next_step':'Inspect exact verified roles; no scientific result or full-phase completion is inferred.'})
    output=args.output or args.root/'results/reports/evidence-verification'/run_id/'gate.json'
    output.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive creation; even a rejected result must not replace prior evidence.
    with output.open('x',encoding='utf-8') as f:json.dump(result,f,indent=2,sort_keys=True,allow_nan=False);f.write('\n')
    print(json.dumps(result,sort_keys=True,allow_nan=False))
    return exit_code


if __name__=='__main__':
    raise SystemExit(main())
