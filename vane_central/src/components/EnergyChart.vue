<template>
  <div ref="chartContainer" class="w-full h-64"></div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer])

const props = defineProps({
  data: { type: Array, default: () => [] },
  color: { type: String, default: '#00D4FF' },
  yLabel: { type: String, default: '' },
})

const chartContainer = ref(null)
let chart = null

function renderChart() {
  if (!chartContainer.value || props.data.length === 0) return

  if (!chart) {
    chart = echarts.init(chartContainer.value, 'dark')
  }

  chart.setOption({
    backgroundColor: 'transparent',
    grid: { top: 20, right: 20, bottom: 30, left: 50 },
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(10, 14, 39, 0.95)',
      borderColor: props.color,
      textStyle: { color: '#E2E8F0' },
      formatter: (params) => {
        const date = new Date(params[0].value[0]).toLocaleString()
        const val = typeof params[0].value[1] === 'number' ? params[0].value[1].toFixed(2) : params[0].value[1]
        return `${date}<br/>${props.yLabel}: <b style="color:${props.color}">${val}</b>`
      },
    },
    xAxis: {
      type: 'time',
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#A0AEC0', fontSize: 10 },
    },
    yAxis: {
      type: 'value',
      name: props.yLabel,
      nameTextStyle: { color: '#A0AEC0', fontSize: 11 },
      axisLine: { lineStyle: { color: 'rgba(255,255,255,0.1)' } },
      axisLabel: { color: '#A0AEC0', fontSize: 10 },
      splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } },
    },
    series: [{
      type: 'line',
      data: props.data,
      smooth: true,
      symbol: 'none',
      lineStyle: { color: props.color, width: 2 },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          { offset: 0, color: props.color + '40' },
          { offset: 1, color: props.color + '00' },
        ]),
      },
    }],
  })
}

onMounted(() => {
  renderChart()
})

watch(() => props.data, () => {
  renderChart()
}, { deep: true })
</script>
