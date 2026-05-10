#!/usr/bin/env python3
"""DocGuard CLI - Protect and verify document integrity from the command line."""

import argparse
import json
import sys

from doc_guard import DocGuard


def cmd_protect(args):
    """Protect a document."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.text:
        content = args.text
    else:
        content = sys.stdin.read()

    guard = DocGuard(args.doc_id, store_path=args.store)
    result = guard.protect(content, label=args.label or "cli_protect")
    print(json.dumps(result, indent=2, ensure_ascii=False))


def cmd_verify(args):
    """Verify a document."""
    if args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            content = f.read()
    elif args.text:
        content = args.text
    else:
        content = sys.stdin.read()

    guard = DocGuard(args.doc_id, store_path=args.store)
    result = guard.verify(content)

    if result.get("diff"):
        result["diff"] = result["diff"].to_markdown()

    print(json.dumps(result, indent=2, ensure_ascii=False))

    if not result.get("safe"):
        sys.exit(1)


def cmd_rollback(args):
    """Roll back to a previous version."""
    guard = DocGuard(args.doc_id, store_path=args.store)
    content = guard.rollback(steps=args.steps)
    if content:
        print(content)
    else:
        print("Error: No snapshot available for rollback.", file=sys.stderr)
        sys.exit(1)


def cmd_history(args):
    """Show snapshot history."""
    guard = DocGuard(args.doc_id, store_path=args.store)
    history = guard.history()
    print(json.dumps(history, indent=2, ensure_ascii=False))


def cmd_status(args):
    """Show protection status."""
    guard = DocGuard(args.doc_id, store_path=args.store)
    status = guard.status()
    print(json.dumps(status, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(
        prog="docguard",
        description="DocGuard - Document Integrity Monitoring for AI Workflows",
    )
    parser.add_argument("--store", default=".docguard_store.json",
                        help="Path to checksum store file")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # protect
    p_protect = subparsers.add_parser("protect", help="Protect a document")
    p_protect.add_argument("doc_id", help="Document identifier")
    p_protect.add_argument("--file", "-f", help="File to protect")
    p_protect.add_argument("--text", "-t", help="Text content to protect")
    p_protect.add_argument("--label", "-l", help="Protection label")
    p_protect.set_defaults(func=cmd_protect)

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify a document")
    p_verify.add_argument("doc_id", help="Document identifier")
    p_verify.add_argument("--file", "-f", help="File to verify")
    p_verify.add_argument("--text", "-t", help="Text content to verify")
    p_verify.set_defaults(func=cmd_verify)

    # rollback
    p_rollback = subparsers.add_parser("rollback", help="Roll back to previous version")
    p_rollback.add_argument("doc_id", help="Document identifier")
    p_rollback.add_argument("--steps", "-s", type=int, default=1,
                            help="Number of snapshots to roll back")
    p_rollback.set_defaults(func=cmd_rollback)

    # history
    p_history = subparsers.add_parser("history", help="Show snapshot history")
    p_history.add_argument("doc_id", help="Document identifier")
    p_history.set_defaults(func=cmd_history)

    # status
    p_status = subparsers.add_parser("status", help="Show protection status")
    p_status.add_argument("doc_id", help="Document identifier")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == "__main__":
    main()
