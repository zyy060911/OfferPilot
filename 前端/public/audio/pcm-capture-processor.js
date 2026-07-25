class PcmCaptureProcessor extends AudioWorkletProcessor {
  constructor() {
    super()
    this.bufferSize = 2048
    this.buffer = new Float32Array(this.bufferSize)
    this.offset = 0
  }

  process(inputs) {
    const input = inputs[0]?.[0]
    if (!input) return true

    let sourceOffset = 0
    while (sourceOffset < input.length) {
      const remaining = this.bufferSize - this.offset
      const copyLength = Math.min(remaining, input.length - sourceOffset)
      this.buffer.set(input.subarray(sourceOffset, sourceOffset + copyLength), this.offset)
      this.offset += copyLength
      sourceOffset += copyLength

      if (this.offset === this.bufferSize) {
        const completed = this.buffer
        this.port.postMessage(completed.buffer, [completed.buffer])
        this.buffer = new Float32Array(this.bufferSize)
        this.offset = 0
      }
    }
    return true
  }
}

registerProcessor('pcm-capture-processor', PcmCaptureProcessor)
