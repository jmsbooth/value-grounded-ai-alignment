"""Tamper tests use synthetic evidence; no fixture is a model receipt."""
from __future__ import annotations
import copy,json
from pathlib import Path
import pytest
from vgta_eval.verified_inventory import EvidenceError,canonical,digest,verify_inventory

def dump(p,v):p.write_text(json.dumps(v,sort_keys=True,indent=2)+'\n');return {'path':p.name,'sha256':digest(p)}

def setup(tmp):
    (tmp/'source.py').write_text('known source')
    (tmp/'protected.txt').write_text('historical artifact')
    (tmp/'stdout.txt').write_text('executed fixture log')
    context={'source_revision':'fixture-source','environment':'fixture-environment'}
    result={'protocol':'fixture-protocol','scope':'fixture','experiment_id':'counterexample','run_id':'fixed-1','context':context,
            'checks':{'passed':True,'cases':3},'artifact_hashes':{'stdout.txt':digest(tmp/'stdout.txt')}}
    result_ref=dump(tmp/'result.json',result)
    receipt={'receipt_version':'evidence-receipt-v1','producer_kind':'known_fixture','protocol':'fixture-protocol','scope':'fixture','context':context,
             'experiment_id':'counterexample','run_id':'fixed-1','status':'PASS','result_sha256':result_ref['sha256']}
    receipt['receipt_digest']=canonical(receipt)
    receipt_ref=dump(tmp/'receipt.json',receipt)
    plan={'schema':'vga-evidence-plan-v1','protocol':'fixture-protocol','scope':'fixture','context':context,
          'source_files':{'source.py':digest(tmp/'source.py')},'protected_files':{'protected.txt':digest(tmp/'protected.txt')},
          'requirements':[{'role':'numerical_contract','producer_kind':'known_fixture','experiment_id':'counterexample',
                           'assertions':[{'pointer':'/checks/passed','op':'eq','value':True},{'pointer':'/checks/cases','op':'ge','value':3}]}]}
    plan_ref=dump(tmp/'plan.json',plan)
    inventory={'schema':'vga-evidence-inventory-v1','plan':plan_ref,'entries':[{'role':'numerical_contract','receipt':receipt_ref,'result':result_ref,'attachments':result['artifact_hashes']}]}
    dump(tmp/'inventory.json',inventory)
    return plan,inventory,result,receipt

def verify(tmp,plan_hash=None,scope='fixture'):
    return verify_inventory(tmp,tmp/'inventory.json',approved_plan_sha256=plan_hash or digest(tmp/'plan.json'),expected_scope=scope)

def test_valid_fixture_inventory_does_not_authorize_training(tmp_path):
    setup(tmp_path);result=verify(tmp_path)
    assert result['status']=='EVIDENCE_INVENTORY_VERIFIED'
    assert result['scope']=='fixture' and result['locked_launch_authorized'] is False

@pytest.mark.parametrize('path',['source.py','protected.txt','stdout.txt','receipt.json','result.json'])
def test_tampered_file_fails(tmp_path,path):
    setup(tmp_path);(tmp_path/path).write_text('changed bytes')
    with pytest.raises(EvidenceError):verify(tmp_path)

@pytest.mark.parametrize('change',['missing_receipt','missing_role','duplicate_role','status_only','wrong_scope','foreign_protocol','foreign_context','false_assertion','too_few_cases','wrong_run','invalid_receipt_digest','unknown_attachment'])
def test_invalid_evidence_cannot_pass(tmp_path,change):
    plan,inv,result,receipt=setup(tmp_path)
    if change=='missing_receipt':(tmp_path/'receipt.json').unlink()
    elif change=='missing_role':inv['entries']=[]
    elif change=='duplicate_role':inv['entries'].append(copy.deepcopy(inv['entries'][0]))
    elif change=='status_only':result.pop('checks');result['status']='PASS'
    elif change=='wrong_scope':result['scope']='development'
    elif change=='foreign_protocol':result['protocol']='another-protocol'
    elif change=='foreign_context':result['context']={'source_revision':'other-source'}
    elif change=='false_assertion':result['checks']['passed']=False
    elif change=='too_few_cases':result['checks']['cases']=1
    elif change=='wrong_run':result['run_id']='another-run'
    elif change=='unknown_attachment':result['artifact_hashes']['unlisted.txt']='f'*64
    # Re-hash altered results/receipts so semantic binding, not only byte hashes,
    # must reject these mutations. The independently pinned plan stays fixed.
    if change not in {'missing_receipt','missing_role','duplicate_role'}:
        inv['entries'][0]['result']=dump(tmp_path/'result.json',result)
        receipt['result_sha256']=inv['entries'][0]['result']['sha256']
        receipt.pop('receipt_digest');receipt['receipt_digest']=canonical(receipt)
        if change=='invalid_receipt_digest':receipt['receipt_digest']='f'*64
        inv['entries'][0]['receipt']=dump(tmp_path/'receipt.json',receipt)
    dump(tmp_path/'inventory.json',inv)
    with pytest.raises(EvidenceError):verify(tmp_path)

def test_independent_plan_pin_rejects_rewritten_requirements(tmp_path):
    plan,inv,_,_=setup(tmp_path);expected=digest(tmp_path/'plan.json')
    plan['requirements'][0]['assertions'][1]['value']=0
    inv['plan']=dump(tmp_path/'plan.json',plan);dump(tmp_path/'inventory.json',inv)
    with pytest.raises(EvidenceError):verify(tmp_path,expected)

def test_fixture_cannot_fill_model_scope(tmp_path):
    setup(tmp_path)
    with pytest.raises(EvidenceError):verify(tmp_path,scope='development')

@pytest.mark.parametrize('path',['../elsewhere.json','/tmp/elsewhere.json'])
def test_escape_path_rejected(tmp_path,path):
    _,inv,_,_=setup(tmp_path);inv['entries'][0]['receipt']['path']=path;dump(tmp_path/'inventory.json',inv)
    with pytest.raises(EvidenceError):verify(tmp_path)

def test_boolean_not_interchangeable_with_integer(tmp_path):
    _,inv,result,receipt=setup(tmp_path);result['checks']['passed']=1
    inv['entries'][0]['result']=dump(tmp_path/'result.json',result);receipt['result_sha256']=inv['entries'][0]['result']['sha256']
    receipt.pop('receipt_digest');receipt['receipt_digest']=canonical(receipt);inv['entries'][0]['receipt']=dump(tmp_path/'receipt.json',receipt);dump(tmp_path/'inventory.json',inv)
    with pytest.raises(EvidenceError):verify(tmp_path)
