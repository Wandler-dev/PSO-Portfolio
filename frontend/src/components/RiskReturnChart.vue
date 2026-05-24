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

function tooltip(point) {
  return [
    `volatility: ${(point.value[0] * 100).toFixed(2)}%`,
    `expected_return: ${(point.value[1] * 100).toFixed(2)}%`,
    `sharpe_ratio: ${point.value[2].toFixed(4)}`
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
    tooltip: { formatter: tooltip },
    xAxis: {
      type: 'value',
      name: 'volatility',
      axisLabel: { formatter: (value) => `${(value * 100).toFixed(1)}%` }
    },
    yAxis: {
      type: 'value',
      name: 'expected_return',
      axisLabel: { formatter: (value) => `${(value * 100).toFixed(1)}%` }
    },
    series: [
      {
        name: 'random',
        type: 'scatter',
        symbolSize: 5,
        data: randomData,
        itemStyle: { color: 'rgba(99, 125, 168, 0.45)' }
      },
      {
        name: 'pso_best',
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
