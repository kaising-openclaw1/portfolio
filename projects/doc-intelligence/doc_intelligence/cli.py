#!/usr/bin/env python3
"""Doc Intelligence - CLI 命令行入口"""

import argparse
import sys
import json

from .processor import DocumentProcessor


def main():
    parser = argparse.ArgumentParser(
        description="Doc Intelligence - 智能文档处理工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # summarize
    p_sum = subparsers.add_parser("summarize", help="生成文档摘要")
    p_sum.add_argument("file", help="文档路径")
    p_sum.add_argument("--max-length", type=int, default=500, help="摘要最大长度")

    # translate
    p_trans = subparsers.add_parser("translate", help="翻译文档")
    p_trans.add_argument("file", help="文档路径")
    p_trans.add_argument("--target", default="en", help="目标语言 (en/zh/ja/ko)")

    # keywords
    p_kw = subparsers.add_parser("keywords", help="提取关键词")
    p_kw.add_argument("file", help="文档路径")
    p_kw.add_argument("--top-k", type=int, default=10, help="关键词数量")
    p_kw.add_argument("--method", default="hybrid", choices=["hybrid", "tfidf", "textrank", "llm"])

    # convert
    p_conv = subparsers.add_parser("convert", help="格式转换")
    p_conv.add_argument("file", help="文档路径")
    p_conv.add_argument("--format", default="markdown", help="输出格式")

    # batch
    p_batch = subparsers.add_parser("batch", help="批量处理")
    p_batch.add_argument("input_dir", help="输入目录")
    p_batch.add_argument("--ops", required=True, help="操作列表，逗号分隔 (summarize,keywords,convert)")
    p_batch.add_argument("--output", default="./results", help="输出目录")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    proc = DocumentProcessor()

    if args.command == "summarize":
        result = proc.summarize(args.file, max_length=args.max_length)
        print(f"\n📝 文档摘要 ({args.file}):\n{'='*50}\n{result}\n")

    elif args.command == "translate":
        result = proc.translate(args.file, target_lang=args.target)
        print(f"\n🌐 翻译结果 ({args.file}):\n{'='*50}\n{result}\n")

    elif args.command == "keywords":
        result = proc.extract_keywords(args.file, top_k=args.top_k, method=args.method)
        print(f"\n🔑 关键词 ({args.file}):\n{'='*50}\n{', '.join(result)}\n")

    elif args.command == "convert":
        result = proc.convert(args.file, output_format=args.format)
        print(f"\n📄 转换完成 → {result}\n")

    elif args.command == "batch":
        ops = [o.strip() for o in args.ops.split(",")]
        results = proc.batch_process(args.input_dir, ops, args.output)
        print(f"\n📦 批量处理完成，共处理 {len(results)} 个文件\n")
        for r in results:
            print(f"  {r['file']}: {list(r['operations'].keys())}")


if __name__ == "__main__":
    main()
