<template>
  <section class="chart-panel wide-panel">
    <div class="chart-title">风险-收益散点图：随机组合 vs PSO 最优解</div>
    <div v-if="!points.length" class="empty-state">等待优化结果</div>
    <div ref="chartRef" class="chart-canvas large" />
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  points: { type: Array, default: () => [] },
  bestPoint: { type: Object, default: null }
})

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

function tooltip(point) {
  const typeLabel = point.seriesName === 'PSO 最优解' ? 'PSO 最优解' : '随机组合'
  return [
    `类型：${typeLabel}`,
    `波动率（Volatility）：${(point.value[0] * 100).toFixed(2)}%`,
    `期望收益率（Expected Return）：${(point.value[1] * 100).toFixed(2)}%`,
    `夏普比率（Sharpe Ratio）：${point.value[2].toFixed(4)}`
  ].join('<br/>')
}

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  const randomData = props.points.map((point) => [point.volatility, point.expected_return, point.sharpe_ratio])
  const bestData = props.bestPoint
    ? [[props.bestPoint.volatility, props.bestPoint.expected_return, props.bestPoint.sharpe_ratio]]
    : []
  chart.setOption({
    grid: { left: 58, right: 28, top: 30, bottom: 44 },
    tooltip: { ...tooltipStyle, formatter: tooltip },
    xAxis: {
      type: 'value',
      name: '波动率（Volatility）',
      nameTextStyle: { color: chartTextColor },
      axisLabel: { color: chartLabelColor, formatter: (value) => `${(value * 100).toFixed(1)}%` },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    yAxis: {
      type: 'value',
      name: '期望收益率（Expected Return）',
      nameTextStyle: { color: chartTextColor },
      axisLabel: { color: chartLabelColor, formatter: (value) => `${(value * 100).toFixed(1)}%` },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series: [
      {
        name: '随机组合',
        type: 'scatter',
        symbolSize: 5,
        data: randomData,
        itemStyle: { color: 'rgba(99, 125, 168, 0.45)' }
      },
      {
        name: 'PSO 最优解',
        type: 'scatter',
        symbolSize: 18,
        data: bestData,
        itemStyle: { color: '#ffbf3f', borderColor: '#1b2433', borderWidth: 2 }
      }
    ]
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
watch(() => [props.points, props.bestPoint], renderChart, { deep: true })
</script>
