"""Prepare or verify the pinned Pythia CPU environment, without training."""
import argparse, hashlib, importlib.metadata, json, os, pathlib, platform, subprocess, time, uuid
p=argparse.ArgumentParser()
p.add_argument('--root',type=pathlib.Path,default=pathlib.Path('/vercel'))
p.add_argument('--source-revision',default='41d01730ca98430d282a06f089b0617d6351ab6b')
p.add_argument('--download',action='store_true')
a=p.parse_args()
root=a.root.resolve(); repo=root/'value-grounded-ai-alignment'
head=subprocess.check_output(['git','-C',str(repo),'rev-parse','HEAD'],text=True).strip()
if head != a.source_revision: raise RuntimeError('Source revision mismatch')
os.environ['HF_HOME']=str(root/'vga-model-cache')
os.environ['HF_HUB_DISABLE_XET']='1'
os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
if not a.download: os.environ['HF_HUB_OFFLINE']='1'
from huggingface_hub import snapshot_download
expected={
 'config.json':'d4c11e84a59c8af4d88446bba53b718f7aef740daa070ded08fd6a9a3aca4fc6',
 'model.safetensors':'1c88b0bf18293fae0e09c1d978b14b1adb08cb6a83154463133982fe460fcea4',
 'special_tokens_map.json':'6f50ab5a5a509a1c309d6171f339b196a900dc9c99ad0408ff23bb615fdae7ad',
 'tokenizer.json':'c24618a1b3e6a38167beff1c72cffd126c3a66254347304b50547d12c5f25624',
 'tokenizer_config.json':'70e38394e494931c6f773ba41e19460dd4436526b852207367f04341b4066d3f'}
revision='bba6a464f54bbf08fc174cfb351d9794d58af21d'
cache=pathlib.Path(snapshot_download('EleutherAI/pythia-410m',revision=revision,allow_patterns=list(expected),local_files_only=not a.download,token=False,max_workers=2))
for name,want in expected.items():
 h=hashlib.sha256()
 with (cache/name).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
 if h.hexdigest()!=want: raise RuntimeError('Asset checksum mismatch: '+name)
import torch
from vgta_transformer.model_loader import load_tokenizer,load_base_model
from vgta_transformer.adaptation import add_lora
torch.set_num_threads(4); torch.manual_seed(11)
tokenizer=load_tokenizer(local_files_only=True)
model=load_base_model(local_files_only=True,device='cpu'); model.eval()
inputs=tokenizer('Environment qualification: apply the stated policy.',return_tensors='pt',add_special_tokens=False)
with torch.inference_mode(): scores=model(**inputs,use_cache=False).logits
if not torch.isfinite(scores).all().item(): raise RuntimeError('Non-finite model output')
shape=list(scores.shape); del scores
model=add_lora(model)
trainable=sum(v.numel() for v in model.parameters() if v.requires_grad)
if trainable!=3145728: raise RuntimeError('Unexpected LoRA parameter count')
record={'environment_id':'vga-vercel-cpu-v1','source_commit':head,'model_revision':revision,'verified_asset_sha256':expected,'python':platform.python_version(),'versions':{k:importlib.metadata.version(k) for k in ['torch','transformers','peft','numpy','pytest']},'finite_logits':True,'logits_shape':shape,'lora_trainable_parameters':trainable,'pretrained_training_steps':0,'scope':'environment_qualification','model_hypothesis_tested':False}
record_dir=root/'vga-environment-records'/('verification-'+time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())+'-'+uuid.uuid4().hex[:8])
record_dir.mkdir(parents=True,exist_ok=False)
(record_dir/'qualification.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
activate='\n'.join(['# Source this file before executing tests in the prepared sandbox.',f'export PATH="{root}/vga-env/bin:$PATH"',f'export HF_HOME="{root}/vga-model-cache"','export HF_HUB_OFFLINE=1 TRANSFORMERS_OFFLINE=1 HF_HUB_DISABLE_XET=1 HF_HUB_DISABLE_TELEMETRY=1','export TOKENIZERS_PARALLELISM=false OMP_NUM_THREADS=4 MKL_NUM_THREADS=4',f'export PYTHONPATH="{repo}/src"',f'cd "{repo}"',''])
(root/'vga-activate.sh').write_text(activate)
print(json.dumps({'environment_ready':True,'qualification':str(record_dir/'qualification.json'),'training_started':False}))
