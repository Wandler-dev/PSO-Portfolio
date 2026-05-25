<template>
  <section class="chart-panel">
    <div class="chart-title">PSO 收敛曲线</div>
    <div v-if="!curve.length" class="empty-state">等待优化结果</div>
    <div ref="chartRef" class="chart-canvas" />
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  curve: { type: Array, default: () => [] }
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

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 48, right: 20, top: 36, bottom: 36 },
    tooltip: {
      trigger: 'axis',
      ...tooltipStyle,
      formatter: (params) => {
        const point = params[0]
        return `第 ${point.axisValue} 次迭代<br/>夏普比率：${Number(point.value).toFixed(4)}`
      }
    },
    xAxis: {
      type: 'category',
      data: props.curve.map((point) => point.iteration),
      name: '迭代次数',
      nameTextStyle: { color: chartTextColor },
      axisLabel: { color: chartLabelColor },
      axisLine: { lineStyle: { color: axisLineColor } },
      axisTick: { lineStyle: { color: axisLineColor } }
    },
    yAxis: {
      type: 'value',
      name: '夏普比率（Sharpe Ratio）',
      scale: true,
      nameTextStyle: { color: chartTextColor },
      axisLabel: { color: chartLabelColor },
      axisLine: { lineStyle: { color: axisLineColor } },
      splitLine: { lineStyle: { color: splitLineColor } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: props.curve.map((point) => point.sharpe_ratio),
        lineStyle: { color: '#28d6a3', width: 3 },
        areaStyle: { color: 'rgba(40, 214, 163, 0.12)' }
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
watch(() => props.curve, renderChart, { deep: true })
</script>
