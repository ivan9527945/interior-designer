# place_furniture.rb — Sprint 3
# 讀 RS_ARGS_JSON: { skp_in, rooms, style }
# 依房間類型與 furniture_language 擺放家具 (component)

require 'json'
require 'sketchup'

def rs_log(msg)
  STDERR.puts "[RS] #{msg}"
  STDERR.flush
end

begin
  args    = JSON.parse(ENV.fetch("RS_ARGS_JSON", "{}"))
  skp_in  = args["skp_in"]
  rooms   = args["rooms"] || []
  style   = args["style"] || {}
  out_path = ENV.fetch("RS_OUTPUT", skp_in)

  model = Sketchup.active_model
  if skp_in && File.exist?(skp_in)
    model.load(skp_in) rescue nil
  end

  # Sprint 3 TODO: 載入公司材質/家具 component library，依 room type 插入
  # 目前佔位：在每個房間重心放一個預設 group 標記
  rooms.each do |room|
    cx = (room["centroid_x"] || 0).to_f.mm
    cy = (room["centroid_y"] || 0).to_f.mm
    pt = Geom::Point3d.new(cx, cy, 0)
    # 插入一個 text marker
    model.active_entities.add_cpoint(pt)
  end

  model.save(out_path)
  rs_log "furniture placed (stub), saved to #{out_path}"

rescue => e
  rs_log "FATAL: #{e}"
  exit 1
ensure
  Sketchup.quit
end
