#!/usr/bin/env python3
"""
Additional test for the duplicate line fix
"""
import sys
sys.path.append('/app/backend')

from server import extract_clean_script

# Test case with multiple potential duplicates
test_script_2 = '''
**VIDEO TITLE:** Morning Productivity Tips

**[0:00-0:03] SHOT 1: HOOK**
**[CHARACTER:]** Text: "Transform your mornings in 3 simple steps!"
**[DIALOGUE:]** (Voiceover - Energetic tone) "Transform your mornings in 3 simple steps!"

**[0:03-0:06] SHOT 2: TIP 1** 
**[CHARACTER:]** Person making bed
**[DIALOGUE:]** "First, make your bed. It's a quick win to start your day right."

**[0:06-0:09] SHOT 3: TIP 2**
**[CHARACTER:]** Text: "Move your body for 5 minutes!"
**[DIALOGUE:]** (Voiceover - Motivational) "Move your body for 5 minutes!"

**[0:09-0:12] SHOT 4: CALL TO ACTION**
**[CHARACTER:]** Text: "Try this tomorrow and see the difference!"
**[DIALOGUE:]** (Direct to camera) "Try this tomorrow and see the difference!"
'''

print("Testing duplicate detection in complex script...")
print("=" * 60)

clean_script = extract_clean_script(test_script_2)

print(f"Original script:\n{test_script_2}")
print("\n" + "=" * 60)
print(f"Cleaned script:\n{clean_script}")
print("\n" + "=" * 60)

# Check for duplicates
test_phrases = [
    "Transform your mornings in 3 simple steps!",
    "Move your body for 5 minutes!",
    "Try this tomorrow and see the difference!"
]

all_good = True
for phrase in test_phrases:
    count = clean_script.count(phrase)
    if count <= 1:
        print(f"✅ '{phrase}' appears {count} time(s)")
    else:
        print(f"❌ '{phrase}' appears {count} times (DUPLICATE!)")
        all_good = False

if all_good:
    print(f"\n🎉 SUCCESS: No duplicate lines detected in cleaned script!")
else:
    print(f"\n❌ FAILED: Duplicates still exist!")

print(f"\nFinal cleaned script length: {len(clean_script)} characters")