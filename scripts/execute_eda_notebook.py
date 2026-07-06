import json
import pathlib

root = pathlib.Path(__file__).resolve().parents[1]
nb_path = root / 'notebooks' / '03_Exploratory_Data_Analysis.ipynb'

nb = json.loads(nb_path.read_text(encoding='utf-8'))
ns = {'__name__': '__main__'}

import os
os.chdir(root)

for idx, cell in enumerate(nb['cells']):
    if cell.get('cell_type') == 'code':
        source = ''.join(cell.get('source', []))
        if source.strip():
            exec(compile(source, f'{nb_path.name}#cell{idx+1}', 'exec'), ns)

print('EXECUTION_COMPLETE')
report_dir = root / 'reports' / 'eda_outputs'
print('REPORT_DIR_EXISTS', report_dir.exists())
print('REPORT_FILES', [p.name for p in sorted(report_dir.glob('*'))])
