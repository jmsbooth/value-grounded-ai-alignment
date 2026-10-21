"""Targeted source/algebra contracts, not Pythia model-quality tests.

The serializer is loaded from its actual source, with only the external
annotation projection replaced by an identity mapping. Training functions run
unchanged against hand-authored PyTorch tensors and a small algebra fixture.
These tests do not require or stand in for the pretrained checkpoint.
"""
from __future__ import annotations
import ast
import copy
import importlib.util
import json
from pathlib import Path
import sys
import types
import pytest
import torch
from vgta_transformer.training import accumulated_train_step
from vgta_transformer.auxiliary_heads import AuxiliaryHeads, pool_prompt_hidden

ROOT = Path(__file__).resolve().parents[2]

def serializer_module():
    path = ROOT / 'src/vgta_transformer/response_contract.py'
    tree = ast.parse(path.read_text())
    tree.body = [node for node in tree.body if not (
        isinstance(node, ast.ImportFrom) and (node.module or '').startswith('vgta_eval.'))]
    name = '_vga_serializer_contract_fixture'
    module = types.ModuleType(name)
    module.__dict__['build_response_target'] = lambda annotation: annotation
    sys.modules[name] = module
    exec(compile(tree, str(path), 'exec'), module.__dict__)
    return module

@pytest.mark.parametrize('value', ['policy_compliance', 'quoted "value" and \\ path', '\u03b1\u00e9', '', ['privacy','agency'], []])
def test_exact_top_level_value_span(value):
    module = serializer_module()
    target = {'action':'say "a"', 'relation_class':value, 'useful':True}
    result = module.serialize_response_target(target)
    assert result.text == json.dumps(target, ensure_ascii=False, sort_keys=True, separators=(',',':'))
    ((start,end),) = result.value_spans['relation_class']
    assert result.text[start:end] == json.dumps(value, ensure_ascii=False, separators=(',',':'))
    assert result.text[start-1] == ':'
    assert result.text[end] in ',}'

class CharacterTokenizer:
    eos_token_id = 0
    pad_token_id = 0
    def __call__(self, text, **kwargs):
        out={'input_ids':[ord(c)+1 for c in text]}
        if kwargs.get('return_offsets_mapping'):
            out['offset_mapping']=[(i,i+1) for i in range(len(text))]
        return out

@pytest.mark.parametrize('field',['salient_values','relation_class','applicable_norm_ids','conflict_class'])
def test_weights_hit_exact_value_not_key_or_colon(field):
    module=serializer_module()
    target={'action':'request additional information','salient_values':['privacy'], 'relation_class':'consent_scope', 'applicable_norm_ids':['norm_01'], 'conflict_class':'resolvable_conflict'}
    out=module.serialize_response_target(target)
    weights=module._selected_weight_mask(CharacterTokenizer(),out,[field])
    # Compute independent expected offset from JSON key text, not reported span.
    key=json.dumps(field)+':'
    start=out.text.index(key)+len(key)
    value=json.dumps(target[field],separators=(',',':'))
    expected=set(range(start,start+len(value)))
    assert {i for i,w in enumerate(weights) if w==2.0}==expected

class AlgebraFixture(torch.nn.Module):
    """Small differentiable expression; not a Transformer or Pythia proxy."""
    def __init__(self):
        super().__init__()
        self.embedding=torch.nn.Embedding(7,4,dtype=torch.float64)
        self.readout=torch.nn.Linear(4,7,dtype=torch.float64)
    def forward(self,input_ids,attention_mask,**kwargs):
        h=self.embedding(input_ids)
        return types.SimpleNamespace(logits=self.readout(h),hidden_states=(h,))

def batch(ids, weights):
    x=torch.tensor([ids]); mask=torch.ones_like(x,dtype=torch.bool); mask[:,0]=False
    return {'input_ids':x,'attention_mask':torch.ones_like(x),'labels':x.clone(), 'response_mask':mask,'prompt_mask':~mask,'response_weight_mask':torch.tensor([weights],dtype=torch.float64)}

def independently_normalized_objective(model,heads,batches,targets,coeff,response_coeff,masks):
    response_num=0.;response_den=0.;aux_num={};aux_den={}
    for b,t,ms in zip(batches,targets,masks):
        out=model(b['input_ids'],b['attention_mask'])
        flat=torch.nn.functional.cross_entropy(out.logits[:,:-1].reshape(-1,7),b['labels'][:,1:].reshape(-1),reduction='none')
        w=(b['response_weight_mask'][:,1:]*b['response_mask'][:,1:]).reshape(-1)
        response_num=response_num+(flat*w).sum();response_den=response_den+w.sum()
        pooled=out.hidden_states[-1][:,0]
        for name,logits in heads(pooled).items():
            if name not in t or not coeff.get(name,0):continue
            loss=torch.nn.functional.binary_cross_entropy_with_logits(logits,t[name],reduction='none')
            mk=ms.get(name,torch.ones_like(loss))
            aux_num[name]=aux_num.get(name,0.)+(loss*mk).sum()
            aux_den[name]=aux_den.get(name,0.)+mk.sum()
    obj=response_coeff*response_num/response_den
    for name in aux_num:obj=obj+coeff[name]*aux_num[name]/aux_den[name].clamp_min(1.)
    return obj

@pytest.mark.parametrize('response_coeff,aux_coeff',[(1.,.2),(0.,.2),(.5,.7),(1.,1.)])
def test_logged_weighted_objective_and_actual_update(response_coeff,aux_coeff):
    torch.manual_seed(31)
    model=AlgebraFixture();heads=AuxiliaryHeads(4,value_count=2,relation_count=2,norm_count=2,conflict_count=2).double()
    reference=copy.deepcopy(model);reference_heads=copy.deepcopy(heads)
    batches=[batch([1,2,3],[1,2,1]),batch([1,4,2,5,6],[1,1,1,2,1])]
    targets=[{'values':torch.tensor([[1.,0.]],dtype=torch.float64)},{'values':torch.tensor([[0.,1.]],dtype=torch.float64)}]
    masks=[{'values':torch.tensor([[1.,0.]],dtype=torch.float64)},{'values':torch.ones((1,2),dtype=torch.float64)}]
    coeff={'values':aux_coeff}
    expected=independently_normalized_objective(reference,reference_heads,batches,targets,coeff,response_coeff,masks)
    expected.backward()
    refopt=torch.optim.SGD(list(reference.parameters())+list(reference_heads.parameters()),lr=.01)
    refopt.step()
    opt=torch.optim.SGD(list(model.parameters())+list(heads.parameters()),lr=.01)
    metrics=accumulated_train_step(model,batches,opt,auxiliary_heads=heads,auxiliary_targets=targets,auxiliary_weights=coeff,auxiliary_masks=masks,response_loss_coefficient=response_coeff,max_grad_norm=1e9)
    # Algebra and update assertions run before the reporting assertion.
    for actual,wanted in zip(list(model.parameters())+list(heads.parameters()),list(reference.parameters())+list(reference_heads.parameters())):
        assert torch.allclose(actual,wanted,atol=1e-10,rtol=1e-10)
    assert metrics['loss']==pytest.approx(float(expected.detach()),rel=1e-9,abs=1e-10)
    assert metrics['loss']==pytest.approx(response_coeff*metrics['response']+aux_coeff*metrics['values'])
