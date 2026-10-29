import { defineStore } from 'pinia'
import api from '../api/client'

export const useTelemetryStore = defineStore('telemetry', {
  state: () => ({
    sites: [],
    selectedSiteId: null,
    devices: [],
    selectedDeviceId: null,
    currentTelemetry: null,
    relayStates: [true, true, true, true],
    relaySource: 'system',
    alerts: [],
    historyData: [],
    pollInterval: null,
  }),

  actions: {
    async fetchSites() {
      const response = await api.get('/sites/')
      this.sites = response.data
      if (this.sites.length > 0 && !this.selectedSiteId) {
        this.selectedSiteId = this.sites[0].id
        await this.fetchDevices()
      }
    },

    async fetchDevices() {
      if (!this.selectedSiteId) return
      const response = await api.get('/sites/devices/')
      this.devices = response.data.filter(d => d.site === this.selectedSiteId)
      if (this.devices.length > 0 && !this.selectedDeviceId) {
        this.selectedDeviceId = this.devices[0].id
        await this.fetchRelayStates()
        await this.fetchAlerts()
        this.startPolling()
      }
    },

    async fetchRelayStates() {
      if (!this.selectedDeviceId) return
      const response = await api.get('/telemetry/relay-states/', {
        params: { device_id: this.selectedDeviceId }
      })
      this.relayStates = response.data.relay_states
      this.relaySource = response.data.last_source
    },

    async toggleRelay(relayIndex, newState) {
      if (!this.selectedDeviceId) return
      const newStates = [...this.relayStates]
      newStates[relayIndex] = newState
      const response = await api.post('/telemetry/relay-states/', {
        device_id: this.selectedDeviceId,
        relay_states: newStates,
      })
      this.relayStates = response.data.relay_states
      this.relaySource = 'manual'
      await this.fetchAlerts()
    },

    async fetchAlerts() {
      if (!this.selectedDeviceId) return
      const response = await api.get('/telemetry/alerts/', {
        params: { device_id: this.selectedDeviceId, limit: 20 }
      })
      this.alerts = response.data
    },

    async fetchHistory(hours = 24) {
      if (!this.selectedDeviceId) return
      const response = await api.get('/telemetry/history/', {
        params: { device_id: this.selectedDeviceId, hours }
      })
      this.historyData = response.data
    },

    selectSite(siteId) {
      this.stopPolling()
      this.selectedSiteId = siteId
      this.selectedDeviceId = null
      this.currentTelemetry = null
      this.relayStates = [true, true, true, true]
      this.alerts = []
      this.historyData = []
      this.fetchDevices()
    },

    selectDevice(deviceId) {
      this.stopPolling()
      this.selectedDeviceId = deviceId
      this.fetchRelayStates()
      this.fetchAlerts()
      this.startPolling()
    },

    startPolling() {
      this.stopPolling()
      this.fetchRelayStates()
      this.fetchAlerts()
      this.pollInterval = setInterval(() => {
        this.fetchRelayStates()
        this.fetchAlerts()
      }, 5000)
    },

    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval)
        this.pollInterval = null
      }
    },
  },
})
