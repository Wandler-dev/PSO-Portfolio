<template>
  <section class="kpi-grid">
    <div v-for="item in items" :key="item.label" class="kpi-card">
      <span>{{ item.label }}</span>
      <strong>{{ item.value }}</strong>
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, default: null }
})

const percent = (value) => (Number.isFinite(value) ? `${(value * 100).toFixed(2)}%` : '-')
const fixed = (value, digits = 4) => (Number.isFinite(value) ? value.toFixed(digits) : '-')

const items = computed(() => {
  const result = props.result
  const objectiveText = result?.objective_mode === 'risk_adjusted_return' ? '风险厌恶收益' : '夏普比率'
  const maxWeight = Number.isFinite(result?.max_asset_weight) ? `${(result.max_asset_weight * 100).toFixed(0)}%` : '无'
  return [
    { label: '期望收益率（Expected Return）', value: percent(result?.expected_return) },
    { label: '波动率（Volatility）', value: percent(result?.volatility) },
    { label: '夏普比率（Sharpe Ratio）', value: fixed(result?.sharpe_ratio, 4) },
    { label: '目标函数', value: result ? objectiveText : '-' },
    { label: '单策略上限', value: result ? maxWeight : '-' },
    { label: '入选策略数', value: result?.selected_assets?.length ?? '-' },
    { label: '缓存状态', value: result ? (result.cache_hit ? '缓存命中' : '实时计算') : '-' },
    {
      label: '计算耗时',
      value: Number.isFinite(result?.compute_time_seconds) ? `${result.compute_time_seconds.toFixed(3)}s` : '-'
    }
  ]
})
</script>
