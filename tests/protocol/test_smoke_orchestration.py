"""Exercise the real CLI orchestration with a mocked model attempt.

Passing these tests is command/coverage evidence, never Pythia evidence.
"""
from __future__ import annotations
import argparse, ast, hashlib, json, sys, types
from datetime import datetime, timezone
from pathlib import Path
import pytest

ROOT=Path(__file__).resolve().parents[2]
ARMS=('A1','B','C1','C2','B-TEXT-A','C1-TEXT-N','C1-SHAM','C2-SHAM')

def namespace(tmp_path, monkeypatch, extra):
    path=ROOT/'experiments/transformer/corrected_variant_smoke.py'
    tree=ast.parse(path.read_text())
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='main')
    cfg=tmp_path/'variants.yaml';cfg.write_text('common:\n  seeds: [11, 23]\nvariants: {}\n')
    out=tmp_path/'run'
    monkeypatch.setattr(sys,'argv',['runner','--config',str(cfg),'--output-root',str(out),*extra])
    attempts=[]
    def attempt(spec,seed,destination,**kw):
        attempts.append((spec.name,seed))
        destination.mkdir(parents=True,exist_ok=True)
        result={'variant':spec.name,'seed':seed,'status':'CORRECTED_VARIANT_ATTEMPT_COMPLETE','updates_completed':kw['max_updates'],'checkpoint':{'verified':True,'reloaded':True}}
        (destination/'result.json').write_text(json.dumps(result))
        return result
    def receipt(**kw):return dict(kw,receipt_digest='unit_fixture_only')
    ns={'__file__':str(path),'argparse':argparse,'Path':Path,'datetime':datetime,'timezone':timezone,'json':json,'hashlib':hashlib,'sys':sys,'ROOT':tmp_path,'PLAN':cfg,'PROTOCOL':'te-v0.6.2-pythia-correction','load_variant_specs':lambda p:{n:types.SimpleNamespace(name=n) for n in ARMS},'run_attempt':attempt,'make_receipt':receipt,'sha256_file':lambda p:hashlib.sha256(p.read_bytes()).hexdigest(),'write_receipt':lambda p,r:p.write_text(json.dumps(r)),'subprocess':types.SimpleNamespace()}
    exec(compile(ast.Module(body=[node],type_ignores=[]),str(path),'exec'),ns)
    return ns,out,attempts

def test_selected_cli_finishes_with_receipt(tmp_path,monkeypatch):
    ns,out,attempts=namespace(tmp_path,monkeypatch,['--variants','A1','--seeds','11','--max-updates','1'])
    assert ns['main']()==0
    assert (out/'evidence-receipt.json').is_file()
    summary=json.loads((out/'run-summary.json').read_text())
    assert summary['attempt_count']==1
    assert attempts==[('A1',11)]

def test_canary_not_full_protocol_complete(tmp_path,monkeypatch):
    ns,out,_=namespace(tmp_path,monkeypatch,['--variants','C2-SHAM','--seeds','11','--max-updates','1'])
    assert ns['main']()==0
    s=json.loads((out/'run-summary.json').read_text())
    assert s['status']=='CORRECTED_VARIANT_SMOKE_PARTIAL'
    assert s['protocol_expected_attempt_count']==16
    assert s['selected_execution_complete'] is True
    assert s['protocol_completed_attempt_count']==0

def test_complete_required_mock_scope(tmp_path,monkeypatch):
    ns,out,attempts=namespace(tmp_path,monkeypatch,[])
    assert ns['main']()==0
    s=json.loads((out/'run-summary.json').read_text())
    assert len(attempts)==16 and s['status']=='CORRECTED_VARIANT_SMOKE_COMPLETE'

def test_existing_root_is_not_overwritten(tmp_path,monkeypatch):
    ns,out,attempts=namespace(tmp_path,monkeypatch,['--variants','A1','--seeds','11','--max-updates','1'])
    out.mkdir();(out/'sentinel').write_text('prior evidence')
    with pytest.raises(FileExistsError):ns['main']()
    assert not attempts and (out/'sentinel').read_text()=='prior evidence'

def test_isolated_child_does_not_receive_parent_root(tmp_path,monkeypatch):
    ns,out,_=namespace(tmp_path,monkeypatch,['--variants','A1','--seeds','11','23','--max-updates','1','--isolate-attempts'])
    destinations=[]
    def child(command,**kwargs):
        child_root=Path(command[command.index('--output-root')+1]); destinations.append(child_root)
        assert child_root!=out
        name=command[command.index('--variants')+1];seed=int(command[command.index('--seeds')+1])
        p=child_root/name/f'seed-{seed}'/'result.json';p.parent.mkdir(parents=True)
        p.write_text(json.dumps({'variant':name,'seed':seed,'status':'CORRECTED_VARIANT_ATTEMPT_COMPLETE','updates_completed':1,'checkpoint':{'verified':True,'reloaded':True}}))
        (child_root/'run-summary.json').write_text('child summary must survive')
        return types.SimpleNamespace(returncode=0,stdout='',stderr='')
    ns['subprocess'].run=child
    assert ns['main']()==0
    assert len(set(destinations))==2
    assert all((d/'run-summary.json').read_text()=='child summary must survive' for d in destinations)
    assert json.loads((out/'run-summary.json').read_text())['attempt_count']==2
