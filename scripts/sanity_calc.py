# -*- coding: utf-8 -*-
"""sanity_calc.py —— 土木论文评审数值量级速算工具

用法:
    python sanity_calc.py centrifugal --m 192000 --v 1 --r 500    # 离心力(N): 质量kg 车速m/s 半径m
    python sanity_calc.py freq --v 1 --L 20                       # 移动荷载激励频率(Hz) vs 常见桥基频
    python sanity_calc.py verify-force --peak-kn 500 --spans 5    # 由支反力峰值反推验证集中力量级
    python sanity_calc.py dynamic-factor --v 1 --L 20 --f1 3.5    # 简化冲击系数量级判断
"""
import sys
import argparse

sys.stdout.reconfigure(encoding="utf-8")


def cmd_centrifugal(a):
    F = a.m * a.v ** 2 / a.r
    print(f"离心力 F = m·v²/R = {a.m} kg × ({a.v} m/s)² / {a.r} m = {F:.1f} N = {F/1000:.3f} kN")
    if F < 1000:
        print(f"→ 判断: {F/1000:.2f} kN 相对车辆荷载(数百kN)可忽略, '考虑离心力'的宣称在该工况下物理失效")
    elif F < 50000:
        print(f"→ 判断: {F/1000:.1f} kN 量级不可忽略, 论文若宣称考虑需在耦合方程中体现")
    else:
        print(f"→ 判断: {F/1000:.1f} kN 为主要横向作用, 必须纳入分析")


def cmd_freq(a):
    f = a.v / a.L
    print(f"移动荷载激励频率 f ≈ v/L = {a.v}/{a.L} = {f:.4f} Hz")
    print(f"常见梁桥一阶竖弯基频: 20m 跨约 4~5 Hz, 30m 跨约 3~4 Hz, 100m 跨约 1 Hz")
    ratio = f / 3.0
    if ratio < 0.05:
        print(f"→ 判断: 激励频率仅为典型基频的 {ratio:.1%}, 动力放大系数≈1, 计算退化为准静态")


def cmd_verify_force(a):
    # 简支/连续梁过桥时单支座峰值反力量级 ≈ 集中力 × 分配系数(0.3~0.6, 连续梁更分散)
    for k in (0.3, 0.6):
        est = a.peak_kn / k
        print(f"若峰值反力 {a.peak_kn} kN 为集中力的 {k:.0%} → 推算实际集中力 ≈ {est:.0f} kN = {est*1000:.1e} N")
    print("→ 用此结果与正文声称的验证荷载对比: 相差 1000 倍量级即存在录入或输入不一致, 应写'须核查'而非断言")


def cmd_dynamic_factor(a):
    f = a.v / a.L
    ratio = f / a.f1
    print(f"激励频率/基频 = {f:.3f}/{a.f1} = {ratio:.3f}")
    if ratio < 0.05:
        print("→ 准静态, 冲击系数≈1.0, '动力分析'表述不成立")
    elif ratio < 0.5:
        print("→ 准静态为主, 动力放大 <5%, 一般工程可按静力+冲击系数处理")
    else:
        print("→ 动力效应显著, 需完整车桥耦合振动分析")


def main():
    ap = argparse.ArgumentParser(description="土木论文评审数值量级速算")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("centrifugal", help="离心力 mv²/R")
    p.add_argument("--m", type=float, required=True, help="质量 kg")
    p.add_argument("--v", type=float, required=True, help="车速 m/s")
    p.add_argument("--r", type=float, required=True, help="曲率半径 m")
    p.set_defaults(fn=cmd_centrifugal)

    p = sub.add_parser("freq", help="移动荷载激励频率 v/L")
    p.add_argument("--v", type=float, required=True, help="车速 m/s")
    p.add_argument("--L", type=float, required=True, help="跨径 m")
    p.set_defaults(fn=cmd_freq)

    p = sub.add_parser("verify-force", help="由支反力峰值反推验证集中力")
    p.add_argument("--peak-kn", type=float, required=True, help="图上支反力峰值 kN")
    p.add_argument("--spans", type=int, default=5, help="跨数(默认5)")
    p.set_defaults(fn=cmd_verify_force)

    p = sub.add_parser("dynamic-factor", help="动力放大系数量级判断")
    p.add_argument("--v", type=float, required=True, help="车速 m/s")
    p.add_argument("--L", type=float, required=True, help="跨径 m")
    p.add_argument("--f1", type=float, required=True, help="结构一阶频率 Hz")
    p.set_defaults(fn=cmd_dynamic_factor)

    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
