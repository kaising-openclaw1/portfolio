"""Example: Protecting documents from AI agent corruption."""

from doc_guard import DocGuard

# Scenario: An AI agent is editing a configuration file
# Without DocGuard, the AI might silently corrupt parts of the file.
# With DocGuard, we detect and can rollback any corruption.

# Step 1: Protect the original document
guard = DocGuard("config.yaml")

original_content = """
# Application Configuration
database:
  host: localhost
  port: 5432
  name: myapp

server:
  host: 0.0.0.0
  port: 8080
  workers: 4

logging:
  level: INFO
  format: json
"""

result = guard.protect(original_content, label="original_config")
print(f"✅ Protected: {result['checksum'][:16]}...")

# Step 2: Simulate AI editing the document
# A well-behaved AI would only change the logging level
ai_modified_content = """
# Application Configuration
database:
  host: localhost
  port: 5432
  name: myapp

server:
  host: 0.0.0.0
  port: 8080
  workers: 4

logging:
  level: DEBUG
  format: json
"""

# Step 3: Verify the modified content
result = guard.verify(ai_modified_content)
print(f"\n🔍 Verification result:")
print(f"   Safe: {result['safe']}")
print(f"   Status: {result['status']}")

if result.get("change_summary"):
    print(f"   Changes: {result['change_summary']}")

# Step 4: Simulate AI corrupting the document
# The AI accidentally changed the database host
corrupted_content = """
# Application Configuration
database:
  host: 192.168.1.100
  port: 5432
  name: myapp

server:
  host: 0.0.0.0
  port: 8080
  workers: 4

logging:
  level: DEBUG
  format: json
  file: /tmp/lo
"""

result = guard.verify(corrupted_content)
print(f"\n🔍 Verification result:")
print(f"   Safe: {result['safe']}")
print(f"   Status: {result['status']}")

if result.get("diff"):
    print(f"\n📋 Change summary:")
    summary = result["diff"].change_summary
    print(f"   Additions: {summary['additions']}")
    print(f"   Deletions: {summary['deletions']}")
    print(f"   Similarity: {summary['similarity']}%")

# Step 5: Rollback if corruption detected
if not result["safe"]:
    recovered = guard.rollback()
    print(f"\n🔄 Rolling back to protected version...")
    print(f"   Recovered checksum matches original: ", end="")
    from doc_guard import compute_checksum
    print(compute_checksum(recovered) == result.get("checksum") or result.get("checksum") is None)

# Step 6: Check history
print(f"\n📜 Snapshot history:")
for snap in guard.history():
    print(f"   - {snap['label']} ({snap['timestamp']})")
