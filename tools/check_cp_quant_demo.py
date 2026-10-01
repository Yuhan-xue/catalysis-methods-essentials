# -*- coding: utf-8 -*-
"""R5-C02 验收：CP/MAS 强度比不能直接当产率比的最小反例。

模型（示意，参数取常见量级；结论不依赖具体取值，只依赖 τ₁≠τ₂）：
    S_i(t) = N_i · η_i(t)，  η_i(t) = 1 − exp(−t/τ_i)
  · S_i  为接触时间 t 内记录的 CP/MAS 峰强（忽略 T₁ρ 衰减；计入后偏差更大）；
  · N_i  为核数（要定量求的量）；
  · τ_i  为交叉极化建立时间常数：有直接 H 的 CH₃ 类 ≈ 0.1 ms，
         无直接 H 的季碳类 ≈ 5 ms（chapters/parts/ch08-a.tex §8.1.3：
         CP 效率随偶极耦合与接触时间变化）。

反例：两个物种核数相同（N₁=N₂=1），只因 η 不同，任何单一接触时间下的强度比
都不等于 1；把 S₁/S₂ 当产率比，就会把真实的 1:1 读成数倍偏差。定量必须回到
单脉冲（Bloch 衰减）MAS 谱并按 §8.3.3 的弛豫延迟/积分纪律执行。

用法：python tools/check_cp_quant_demo.py
退出码：0 反例成立（强度比偏差 > 1 倍）/ 1 模型失效（偏差 ≤ 1 倍，需复查）
"""
import math

TAU_FAST, TAU_SLOW = 0.1, 5.0     # ms：CH3 类 / 季碳类
N1 = N2 = 1.0                      # 真实核数相同


def eta(t, tau):
    return 1.0 - math.exp(-t / tau)


def ratio(t):
    return (N1 * eta(t, TAU_FAST)) / (N2 * eta(t, TAU_SLOW))


def main():
    print('CP/MAS intensity ratio with equal nuclear counts (N1=N2=1):')
    print('  t/ms   eta1     eta2     S1/S2   naive yield read')
    worst = 0.0
    for t in (0.5, 1.0, 2.0, 5.0, 10.0):
        r = ratio(t)
        worst = max(worst, abs(r - N1 / N2))
        print('  %5.1f  %7.4f  %7.4f  %6.2f  %6.2f' % (t, eta(t, TAU_FAST), eta(t, TAU_SLOW), r, r))
    print('  (t -> inf: both eta -> 1, but T1rho decay differs by species and')
    print('   limits usable contact time; the textbook discipline is single-pulse.)')
    ok = worst > 1.0
    print('cp_quant_demo: %s  worst yield-ratio bias = %.2fx (true 1.00)'
          % ('PASS' if ok else 'FAIL', worst))
    return 0 if ok else 1


if __name__ == '__main__':
    raise SystemExit(main())
