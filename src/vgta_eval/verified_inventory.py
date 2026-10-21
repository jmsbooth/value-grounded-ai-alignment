"""Explicit evidence binding; no directory scan, latest-match, or status-only gate.

This verifies declared artifacts and assertions. It does not prove that a
producer computed honestly, grant execution approval, or infer model benefit.
A caller must pin the reviewed plan hash independently of the inventory.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path, PurePosixPath
from typing import Any, Mapping

class EvidenceError(ValueError):
    pass

def digest(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''):h.update(block)
    return h.hexdigest()

def canonical(value: Any) -> str:
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()

def _pairs(items):
    out={}
    for k,v in items:
        if k in out:raise EvidenceError(f'duplicate JSON key: {k}')
        out[k]=v
    return out

def read_json(path: Path) -> dict[str,Any]:
    try:
        value=json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=_pairs,
                         parse_constant=lambda x: (_ for _ in ()).throw(EvidenceError(f'nonfinite JSON: {x}')))
    except (OSError,json.JSONDecodeError) as exc:raise EvidenceError(f'cannot read {path.name}: {exc}') from exc
    if not isinstance(value,dict):raise EvidenceError('artifact must be a JSON object')
    return value

def _path(root: Path, relative: str) -> Path:
    if not isinstance(relative,str) or not relative or '\\' in relative:
        raise EvidenceError('invalid relative artifact path')
    p=PurePosixPath(relative)
    if p.is_absolute() or '..' in p.parts:raise EvidenceError('artifact path escapes root')
    value=(root/relative).resolve()
    if not value.is_relative_to(root.resolve()):raise EvidenceError('symlink escapes root')
    if not value.is_file():raise EvidenceError(f'missing artifact: {relative}')
    return value

def _ref(root: Path, ref: Mapping[str,Any]) -> Path:
    if not isinstance(ref,dict) or set(ref)!={'path','sha256'}:raise EvidenceError('reference requires exactly path and sha256')
    value=_path(root,ref['path'])
    if digest(value)!=ref['sha256']:raise EvidenceError(f'file hash mismatch: {ref["path"]}')
    return value

def _pointer(value: Any, pointer: str) -> Any:
    if not isinstance(pointer,str) or not pointer.startswith('/'):raise EvidenceError('assertion requires JSON pointer')
    try:
        for part in pointer[1:].split('/'):
            key=part.replace('~1','/').replace('~0','~')
            value=value[int(key)] if isinstance(value,list) else value[key]
        return value
    except (KeyError,IndexError,TypeError,ValueError) as exc:raise EvidenceError(f'missing result pointer: {pointer}') from exc

def _assertion(result: dict[str,Any], assertion: dict[str,Any]) -> None:
    if set(assertion)!={'pointer','op','value'}:raise EvidenceError('invalid assertion fields')
    actual=_pointer(result,assertion['pointer']); expected=assertion['value'];op=assertion['op']
    if op=='eq':
        ok=type(actual) is type(expected) and actual==expected
    elif op in {'ge','le'}:
        if type(actual) not in {int,float} or type(expected) not in {int,float}:raise EvidenceError('numeric assertion on non-number')
        ok=actual>=expected if op=='ge' else actual<=expected
    else:raise EvidenceError('unsupported assertion operator')
    if not ok:raise EvidenceError(f'assertion failed: {assertion["pointer"]}')

def verify_inventory(root: Path, inventory_path: Path, *, approved_plan_sha256: str, expected_scope: str) -> dict[str,Any]:
    """Verify every role against one explicitly pinned plan and source snapshot."""
    root=root.resolve();inv=read_json(inventory_path)
    if set(inv)!={'schema','plan','entries'} or inv['schema']!='vga-evidence-inventory-v1':
        raise EvidenceError('unsupported or incomplete evidence inventory')
    plan_path=_ref(root,inv['plan'])
    if not approved_plan_sha256 or digest(plan_path)!=approved_plan_sha256:
        raise EvidenceError('plan does not match independently supplied approved hash')
    plan=read_json(plan_path)
    required={'schema','protocol','scope','context','source_files','requirements','protected_files'}
    if set(plan)!=required or plan['schema']!='vga-evidence-plan-v1':raise EvidenceError('invalid evidence plan')
    if plan['scope']!=expected_scope:raise EvidenceError('evidence scope mismatch')
    if expected_scope not in {'fixture','canary','development','locked','replication'}:raise EvidenceError('unknown scope')
    if not isinstance(plan['context'],dict) or not plan['context']:raise EvidenceError('context binding is required')
    if not isinstance(plan['source_files'],dict) or not plan['source_files']:raise EvidenceError('source snapshot is required')
    if not isinstance(plan['protected_files'],dict):raise EvidenceError('protected file map is required')
    for mapping in (plan['source_files'],plan['protected_files']):
        for relative,h in mapping.items():_ref(root,{'path':relative,'sha256':h})
    reqs=plan['requirements'];entries=inv['entries']
    if not isinstance(reqs,list) or not reqs or not isinstance(entries,list):raise EvidenceError('nonempty required evidence roles are needed')
    def unique(rows):
        out={}
        for row in rows:
            role=row.get('role') if isinstance(row,dict) else None
            if not isinstance(role,str) or not role or role in out:raise EvidenceError('missing or duplicate role')
            out[role]=row
        return out
    required_by_role=unique(reqs);by_role=unique(entries)
    if set(required_by_role)!=set(by_role):raise EvidenceError('required evidence roles do not match supplied roles')
    verified=[]
    for role,req in required_by_role.items():
        if set(req)!={'role','producer_kind','experiment_id','assertions'} or not req['assertions']:
            raise EvidenceError(f'invalid requirement for {role}')
        entry=by_role[role]
        if set(entry)!={'role','receipt','result','attachments'}:raise EvidenceError('invalid inventory entry')
        receipt_path=_ref(root,entry['receipt']);result_path=_ref(root,entry['result'])
        receipt=read_json(receipt_path);result=read_json(result_path)
        supplied=receipt.pop('receipt_digest',None)
        if supplied!=canonical(receipt):raise EvidenceError(f'receipt digest mismatch: {role}')
        if receipt.get('receipt_version')!='evidence-receipt-v1':raise EvidenceError('unknown receipt version')
        for document in (receipt,result):
            if document.get('protocol')!=plan['protocol'] or document.get('experiment_id')!=req['experiment_id']:
                raise EvidenceError(f'foreign producer or protocol: {role}')
            if document.get('context')!=plan['context']:raise EvidenceError(f'context mismatch: {role}')
            if document.get('scope')!=expected_scope:raise EvidenceError(f'producer scope mismatch: {role}')
        if receipt.get('producer_kind')!=req['producer_kind']:raise EvidenceError(f'wrong producer kind: {role}')
        if receipt.get('result_sha256')!=digest(result_path):raise EvidenceError(f'result not bound by receipt: {role}')
        if receipt.get('run_id')!=result.get('run_id') or not result.get('run_id'):raise EvidenceError(f'run identity mismatch: {role}')
        # Every listed result dependency is checked. No unlisted attachment may
        # be smuggled into the evidence used by this verifier.
        attachments=result.get('artifact_hashes')
        if not isinstance(attachments,dict) or attachments!=entry['attachments']:
            raise EvidenceError(f'attachment inventory mismatch: {role}')
        for relative,h in attachments.items():_ref(root,{'path':relative,'sha256':h})
        for assertion in req['assertions']:_assertion(result,assertion)
        verified.append({'role':role,'result_sha256':digest(result_path),'receipt_sha256':digest(receipt_path)})
    return {'status':'EVIDENCE_INVENTORY_VERIFIED','scope':expected_scope,'protocol':plan['protocol'],
            'plan_sha256':digest(plan_path),'verified_roles':verified,'locked_launch_authorized':False,
            'scientific_outcome':'not_determined_by_artifact_verification'}
