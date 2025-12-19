export class ObjectDetector {
  constructor(videoElement, canvasElement, onDetection) {
    this.video = videoElement
    this.canvas = canvasElement
    this.ctx = canvasElement.getContext('2d')
    this.onDetection = onDetection
    this.objects = []
    this.isDetecting = false
  }
  
  async initializeCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: 'environment'
        }
      })
      this.video.srcObject = stream
      
      return new Promise((resolve) => {
        this.video.onloadedmetadata = () => {
          this.canvas.width = this.video.videoWidth
          this.canvas.height = this.video.videoHeight
          resolve()
        }
      })
    } catch (error) {
      console.error('Error accessing camera:', error)
      throw error
    }
  }
  
  drawBoundingBoxes() {
    this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
    
    this.objects.forEach(obj => {
      const box = obj.bounding_box
      const category = obj.prediction?.waste_category
      
      const colors = {
        'biodegradable': '#4CAF50',
        'recyclable': '#2196F3',
        'hazardous': '#F44336',
        'non-recyclable': '#9E9E9E'
      }
      
      if (box && box.x && box.y && box.width && box.height) {
        this.ctx.strokeStyle = colors[category] || '#9E9E9E'
        this.ctx.lineWidth = 3
        this.ctx.strokeRect(box.x, box.y, box.width, box.height)
        
        if (obj.prediction) {
          this.ctx.fillStyle = colors[category] || '#9E9E9E'
          this.ctx.font = '16px Arial'
          this.ctx.fillText(
            `${obj.prediction.object_name} (${Math.round((obj.prediction.confidence || 0) * 100)}%)`,
            box.x,
            box.y > 20 ? box.y - 5 : box.y + 20
          )
        }
      }
    })
  }
  
  captureImage() {
    this.canvas.width = this.video.videoWidth
    this.canvas.height = this.video.videoHeight
    this.ctx.drawImage(this.video, 0, 0)
    return this.canvas.toDataURL('image/jpeg', 0.8)
  }
  
  stopCamera() {
    if (this.video.srcObject) {
      this.video.srcObject.getTracks().forEach(track => track.stop())
    }
  }
}
