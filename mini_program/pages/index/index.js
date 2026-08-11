const app = getApp()
Page({
  data: {
    sceneList: ["朋友圈", "小红书", "短视频标题", "通知公告", "节日祝福"],
    sceneIdx: 0,
    styleList: ["简约", "文艺", "搞笑", "正式", "可爱"],
    styleIdx: 0,
    lenList: ["100", "200", "300", "500"],
    lenIdx: 1,
    require: "",
    result: "",
    todayCount: 0,
    loading: false,
    historyList: []
  },

  onLoad() {
    this.getTodayCount()
    this.loadHistory()
  },

  loadHistory() {
    const list = wx.getStorageSync('historyList') || []
    this.setData({ historyList: list })
  },

  saveHistory() {
    wx.setStorageSync('historyList', this.data.historyList)
  },

  getTodayCount() {
    const that = this
    wx.request({
      url: "http://10.10.27.62:8000/api/count",
      success(res) {
        that.setData({ todayCount: res.data.todayCount })
      }
    })
  },

  changeScene(e) {
    this.setData({ sceneIdx: e.detail.value })
  },
  changeStyle(e) {
    this.setData({ styleIdx: e.detail.value })
  },
  changeLen(e) {
    this.setData({ lenIdx: e.detail.value })
  },
  inputReq(e) {
    this.setData({ require: e.detail.value })
  },

  generate() {
    const that = this
    if (!that.data.require.trim()) {
      wx.showToast({ title: '请输入文案需求', icon: 'none' })
      return
    }
    that.setData({ loading: true })
    wx.request({
      url: "http://10.10.27.62:8000/api/generate",
      method: "POST",
      data: {
        scene: that.data.sceneList[that.data.sceneIdx],
        style: that.data.styleList[that.data.styleIdx],
        require: that.data.require,
        maxLen: that.data.lenList[that.data.lenIdx]
      },
      success(res) {
        that.setData({ loading: false })
        if (res.data.code === 0) {
          that.setData({
            result: res.data.data,
            todayCount: res.data.todayCount
          })
          wx.vibrateShort({ type: 'light' })
        } else {
          wx.showToast({ title: res.data.msg, icon: 'none' })
        }
      },
      fail() {
        that.setData({ loading: false })
        wx.showToast({ title: '后端服务未启动', icon: 'none' })
      }
    })
  },

  clearAll() {
    this.setData({ require: '', result: '' })
  },

  copy() {
    wx.setClipboardData({
      data: this.data.result,
      success: () => wx.showToast({ title: '已复制到剪贴板', icon: 'success' })
    })
  },

  saveToHistory() {
    const list = this.data.historyList.slice()
    list.unshift(this.data.result)
    if (list.length > 20) list.pop()
    this.setData({ historyList: list })
    this.saveHistory()
    wx.showToast({ title: '已加入收藏', icon: 'success' })
  },

  sendQQ() {
    wx.request({
      url: "http://10.10.27.62:8000/api/send_qq",
      method: "POST",
      data: { content: this.data.result },
      success() {
        wx.showToast({ title: '已推送QQ频道', icon: 'success' })
      }
    })
  },

  setTimer() {
    wx.showModal({
      title: '定时发布',
      editable: true,
      placeholderText: '格式 HH:MM，如 09:30',
      success: res => {
        if (res.confirm && res.content) {
          wx.request({
            url: "http://10.10.27.62:8000/api/task",
            method: "POST",
            data: { time: res.content, content: this.data.result },
            success() {
              wx.showToast({ title: '定时已添加', icon: 'success' })
            }
          })
        }
      }
    })
  },

  useHistory(e) {
    const text = e.currentTarget.dataset.text
    this.setData({ result: text })
    wx.showToast({ title: '已应用', icon: 'none' })
  },

  clearHistory() {
    const that = this
    wx.showModal({
      title: '确认清空',
      content: '将删除全部历史记录',
      success: res => {
        if (res.confirm) {
          that.setData({ historyList: [] })
          that.saveHistory()
          wx.showToast({ title: '已清空', icon: 'success' })
        }
      }
    })
  }
})
