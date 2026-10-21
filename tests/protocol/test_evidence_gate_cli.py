"""Command-boundary verification with fixture receipts; never a model run."""
import json,os,subprocess,sys
from pathlib import Path
import pytest
from test_verified_inventory import setup
from vgta_eval.verified_inventory import digest
ROOT=Path(__file__).resolve().parents[2]

def command(tmp):
    setup(tmp)
    return [sys.executable,str(ROOT/'experiments/transformer/correction_gate.py'),
            '--root',str(tmp),'--inventory',str(tmp/'inventory.json'),
            '--approved-plan-sha256',digest(tmp/'plan.json'),'--scope','fixture','--output',str(tmp/'gate.json')]

def test_gate_cli_emits_fixture_only(tmp_path):
    run=subprocess.run(command(tmp_path),capture_output=True,text=True,timeout=15)
    assert run.returncode==0,run.stderr
    result=json.loads((tmp_path/'gate.json').read_text())
    assert result['status']=='EVIDENCE_INVENTORY_VERIFIED'
    assert result['locked_launch_authorized'] is False
    assert result['scope']=='fixture'

def test_gate_cli_rejects_changed_artifact(tmp_path):
    cmd=command(tmp_path);(tmp_path/'stdout.txt').write_text('tampered')
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    assert run.returncode==1
    assert json.loads((tmp_path/'gate.json').read_text())['status']=='EVIDENCE_INVENTORY_REJECTED'

def test_legacy_cohort_report_cannot_supply_pass_strings(tmp_path):
    path=tmp_path/'legacy.json';path.write_text(json.dumps({'protocol':'te-v0.6.2-pythia-correction','work_package_status':{'independent_scoring':'PASS','eos_real_tokenizer_audit':'PASS'}}))
    run=subprocess.run([sys.executable,str(ROOT/'experiments/transformer/correction_gate.py'),'--cohort',str(path)],capture_output=True,text=True,timeout=15)
    assert run.returncode!=0

def test_gate_cli_never_overwrites_existing_verdict(tmp_path):
    cmd=command(tmp_path);p=tmp_path/'gate.json';p.write_text('historical result')
    run=subprocess.run(cmd,capture_output=True,text=True,timeout=15)
    assert run.returncode!=0 and p.read_text()=='historical result'
