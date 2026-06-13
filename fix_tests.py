import re
with open('tests/test_score_engine.py', 'r') as f:
    content = f.read()
content = content.replace(', "Male"', '')
with open('tests/test_score_engine.py', 'w') as f:
    f.write(content)
