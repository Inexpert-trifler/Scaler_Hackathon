import os, requests
from huggingface_hub import HfApi

r = requests.get('https://huggingface.co/spaces/saranshhyadav/promptgym/raw/main/README.md')
content = r.text
print("Has base_path:", 'base_path' in content)

fixed = '\n'.join(line for line in content.split('\n') if 'base_path' not in line)

with open('README.md', 'w') as f:
    f.write(fixed)

api = HfApi(token=os.environ['HF_TOKEN'])
api.upload_file(
    path_or_fileobj='README.md',
    path_in_repo='README.md',
    repo_id='saranshhyadav/promptgym',
    repo_type='space'
)
print("Done!")
