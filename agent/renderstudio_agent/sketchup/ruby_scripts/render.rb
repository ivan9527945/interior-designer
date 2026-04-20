# render.rb — Sprint 0 PoC
# 讀 RS_ARGS_JSON: { skp_in, vray, output_png }
# 透過 V-Ray 6 Ruby API 觸發渲染

require 'json'
require 'sketchup'

def rs_log(msg)
  STDERR.puts "[RS] #{msg}"
  STDERR.flush
end

begin
  args       = JSON.parse(ENV.fetch("RS_ARGS_JSON", "{}"))
  skp_in     = args["skp_in"]
  vray_cfg   = args["vray"] || {}
  output_png = args["output_png"] || ENV.fetch("RS_OUTPUT", "/tmp/render.png")

  model = Sketchup.active_model

  # 載入 .skp
  if skp_in && File.exist?(skp_in)
    Sketchup.open_file(skp_in)
    model = Sketchup.active_model
  end

  # ── V-Ray 設定 ─────────────────────────────────────────────
  vr = nil
  begin
    # V-Ray 6 for SketchUp Ruby API namespace
    vr = VRay::Scene.get(model)
  rescue NameError
    rs_log "V-Ray Ruby API not loaded — make sure V-Ray plugin is installed"
    exit 2
  end

  if vr.nil?
    rs_log "VRay::Scene.get returned nil"
    exit 2
  end

  settings = vr.renderSettings
  renderer = settings.renderer

  # 解析度
  w = (vray_cfg["width"] || 1920).to_i
  h = (vray_cfg["height"] || 1080).to_i
  renderer.width  = w
  renderer.height = h

  # Sampling
  renderer.samplerType = "bucketSampler"
  renderer.minShades   = (vray_cfg["min_samples"] || 1).to_i
  renderer.maxShades   = (vray_cfg["max_samples"] || 16).to_i

  # GI
  gi = vr.giSettings
  gi.on = (vray_cfg["gi"] != false)

  # Denoiser
  de = vr.denoiserSettings
  de.enabled = (vray_cfg["denoiser"] != false)

  # 輸出路徑
  out_settings = vr.outputSettings
  out_settings.img_file       = output_png
  out_settings.img_rawFile    = ""
  out_settings.progressiveMaxTime = 0

  rs_log "starting render #{w}x#{h} → #{output_png}"
  vr.start

  # 等渲染完成（polling）
  max_wait = 3600
  elapsed  = 0
  while vr.rendering? && elapsed < max_wait
    sleep 5
    elapsed += 5
    pct = (vr.renderProgress * 100).to_i rescue 0
    rs_log "rendering #{pct}% (#{elapsed}s elapsed)"
  end

  if vr.rendering?
    vr.stop
    rs_log "render stopped (timeout)"
    exit 3
  end

  rs_log "render complete → #{output_png}"

rescue => e
  rs_log "FATAL: #{e}\n#{e.backtrace.first(5).join("\n")}"
  exit 1
ensure
  Sketchup.quit
end
