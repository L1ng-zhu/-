import os
import sys
sys.path.insert(0, r'c:\Users\1\Desktop\资料\lzb数据结构与算法导论\pj')

# Clean up all files
for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
    path = "orders.dat" + ext
    if os.path.exists(path):
        try:
            os.remove(path)
        except:
            pass

for f in os.listdir('.'):
    if f.endswith('.csv') or f.endswith('.xlsx'):
        try:
            os.remove(f)
        except:
            pass

for f in os.listdir('.'):
    if f.endswith('.py'):
        try:
            os.remove(f)
        except:
            pass

print("All files cleaned!")
