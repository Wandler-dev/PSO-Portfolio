<template>
  <section class="chart-panel wide-panel comparison-panel">
    <div class="chart-title">不同 Preset 下的组合权重对比</div>
    <div v-if="loading" class="empty-state">正在加载组合权重对比</div>
    <div v-else-if="!assetIds.length" class="empty-state">点击“加载预设对比”查看组合结构变化</div>
    <div ref="chartRef" class="chart-canvas comparison-large" />
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  results: { type: Object, default: () => ({}) },
  loading: { type: Boolean, default: false }
})

const presetOrder = ['conservative', 'balanced', 'aggressive']
const presetLabels = {
  conservative: '保守型',
  balanced: '均衡型',
  aggressive: '激进型'
}
const colors = {
  conservative: '#28d6a3',
  balanced: '#4f8cff',
  aggressive: '#ffbf3f'
}

const chartRef = ref(null)
let chart = null
const chartTextColor = '#e5e7eb'
const chartLabelColor = '#dbeafe'
const axisLineColor = 'rgba(226, 232, 240, 0.65)'
const splitLineColor = 'rgba(148, 163, 184, 0.25)'
const tooltipStyle = {
  backgroundColor: 'rgba(15, 23, 42, 0.95)',
  borderColor: 'rgba(148, 163, 184, 0.35)',
  textStyle: { color: '#f8fafc' }
}

function topRowsFor(preset) {
  return [...(props.results?.[preset]?.asset_weight_table || [])]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 10)
}

const assetIds = computed(() => {
  const weightByAsset = new Map()
  presetOrder.forEach((preset) => {
    topRowsFor(preset).forEach((row) => {
      const current = weightByAsset.get(row.asset_id) || 0
      weightByAsset.set(row.asset_id, Math.max(current, row.weight))
    })
  })
  return [...weightByAsset.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, 12)
    .map(([assetId]) => assetId)
})

function weightMapFor(preset) {
  return new Map((props.results?.[preset]?.asset_weight_table || []).map((row) => [row.asset_id, row.weight]))
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  const ids = assetIds.value
  const series = presetOrder.map((preset) => {
    const weightMap = weightMapFor(preset)
    return {
      name: presetLabels[preset],
      type: 'bar',
      data: ids.map((assetId) => weightMap.get(assetId) || 0),
      itemStyle: { color: colors[preset], borderRadius: [3, 3, 0, 0] }
    }
  })

  chart.setOption({
    legend: {
      top: 2,
      textStyle: { color: chartTextColor }
    },
    grid: { left: 58, right: 24, top: 48, bottom: 92 },
    tooltip: {
      trigger: 'axis',
      ...tooltipStyle,
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const assetId = params[0]?.name || ''
        const lines = [`候选策略：${assetId}`]
        params.forEach((point) => {
          lines.push(`${point.seriesName}: ${(point.value * 100).toFixed(2)}%`)
        })
        return lines.join('<br/>')
      }
    },
    xAxis: {
      type: 'category',
      name: '候选策略',
      data: ids,
      nameTextStyle: { color: chartTextColor },
      axisLabel: {
        rotate: 38,
        color: chartLabelColor,
        formatter: (value) => (value.length > 14 ? `${value.slice(0, 12)}...` : value)
      },
      axisLine: { lineStyle: { color: axisLineColor } },
      axisTick: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      name: '权重',
      nameTextStyle: { color: chartTextColor },
      axisLabel: {
        color: chartLabelColor,
        formatter: (value) => `${(value * 100).toFixed(0)}%`
      },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series
  })
}

function resizeChart() {
  chart?.resize()
}

onMounted(() => {
  renderChart()
  window.addEventListener('resize', resizeChart)
})
onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chart?.dispose()
})
watch(() => props.results, renderChart, { deep: true })
watch(assetIds, renderChart)
</script>
