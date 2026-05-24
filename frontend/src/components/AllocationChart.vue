<template>
  <section class="chart-panel">
    <div class="chart-title">最优组合权重 Top 10</div>
    <div v-if="!topWeights.length" class="empty-state">等待优化结果</div>
    <div ref="chartRef" class="chart-canvas" />
  </section>
</template>

<script setup>
import * as echarts from 'echarts'
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = defineProps({
  assetWeightTable: { type: Array, default: () => [] }
})

const chartRef = ref(null)
let chart = null

const topWeights = computed(() =>
  [...props.assetWeightTable]
    .sort((a, b) => b.weight - a.weight)
    .slice(0, 10)
)

function renderChart() {
  if (!chartRef.value) return
  if (!chart) chart = echarts.init(chartRef.value)
  chart.setOption({
    grid: { left: 56, right: 20, top: 30, bottom: 76 },
    tooltip: {
      formatter: (params) => `${params.name}<br/>weight: ${(params.value * 100).toFixed(2)}%`
    },
    xAxis: {
      type: 'category',
      data: topWeights.value.map((row) => row.asset_id),
      axisLabel: { rotate: 40 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { formatter: (value) => `${(value * 100).toFixed(0)}%` }
    },
    series: [
      {
        type: 'bar',
        data: topWeights.value.map((row) => row.weight),
        itemStyle: { color: '#4f8cff', borderRadius: [4, 4, 0, 0] }
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
watch(topWeights, renderChart, { deep: true })
</script>
