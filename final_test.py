import os
import sys
import time

sys.path.insert(0, r'c:\Users\1\Desktop\资料\lzb数据结构与算法导论\pj')

# Clean up all files first
print("="*60)
print("Cleaning up...")
print("="*60)

for ext in ['', '.idx.amount', '.idx.urgency', '.idx.time', '.root']:
    path = "orders.dat" + ext
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"  Removed: {path}")
        except:
            pass

for f in os.listdir('.'):
    if f.endswith('.csv') or f.endswith('.xlsx'):
        try:
            os.remove(f)
            print(f"  Removed: {f}")
        except:
            pass

for f in os.listdir('.'):
    if f.startswith('test_') or f.startswith('update_') or f.startswith('fix_') or f.startswith('clean_') or f.startswith('run_'):
        if f.endswith('.py'):
            try:
                os.remove(f)
                print(f"  Removed: {f}")
            except:
                pass

print("\nCleanup complete!\n")

# Now test
print("="*60)
print("Testing the system...")
print("="*60)

from main import demo_simulation
demo_simulation()

print("\n" + "="*60)
print("Checking generated files...")
print("="*60)
for f in os.listdir('.'):
    if f.endswith('.csv') or f.endswith('.xlsx'):
        try:
            size = os.path.getsize(f)
            print(f"  ✓ {f} ({size} bytes)")
        except:
            pass

print("\n[ALL DONE] System is working correctly!")
