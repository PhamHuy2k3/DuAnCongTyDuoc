import json

log_path = r'C:\Users\QUOC HUY\.gemini\antigravity\brain\e8fda61b-3c4f-4d12-a20a-4da1cb3e98f7\.system_generated\logs\transcript.jsonl'
with open(log_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

out = open('scratch/views_edits.txt', 'w', encoding='utf-8')
for line in lines[-2000:]: # Look at the last 2000 steps
    try:
        step = json.loads(line)
        if step.get('type') == 'PLANNER_RESPONSE' and 'tool_calls' in step:
            for call in step['tool_calls']:
                if call['name'] in ['replace_file_content', 'write_to_file', 'multi_replace_file_content']:
                    if 'views.py' in call['args'].get('TargetFile', ''):
                        out.write(f"--- Step {step['step_index']} ---\n")
                        out.write(str(call['args'].get('ReplacementContent', call['args'].get('CodeContent', ''))))
                        out.write("\n")
    except Exception as e:
        pass
out.close()
