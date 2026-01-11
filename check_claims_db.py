#!/usr/bin/env python
"""Check what claims are in the database"""

import os
import sys
import django

# Add the project to path
sys.path.insert(0, 'c:\\Users\\asus4\\Desktop\\autonomous Hacks 26')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'credible.settings')
django.setup()

from notes.models import Claim

print("=" * 80)
print("CLAIMS DATABASE DIAGNOSTIC")
print("=" * 80)

# Count all claims
total = Claim.objects.count()
print(f"\n📊 Total claims: {total}")

# Count by status
for status, label in Claim.STATUS_CHOICES:
    count = Claim.objects.filter(status=status).count()
    print(f"   - {label}: {count}")

# Count by source type
print(f"\n📊 By source type:")
sources = Claim.objects.values_list('source_type', flat=True).distinct()
if sources:
    for source in sources:
        count = Claim.objects.filter(source_type=source).count()
        print(f"   - {source}: {count}")
else:
    print("   No sources found")

# Show recent claims
print(f"\n📋 Recent claims (last 5):")
recent = Claim.objects.order_by('-created_at')[:5]
if not recent:
    print("   ❌ No claims found!")
else:
    for claim in recent:
        print(f"\n   ✓ Title: {claim.title[:80]}")
        print(f"     Status: {claim.status}")
        print(f"     Created: {claim.created_at}")
        print(f"     Created by: {claim.created_by}")

print("\n" + "=" * 80)
